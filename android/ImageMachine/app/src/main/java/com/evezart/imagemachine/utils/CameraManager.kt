package com.evezart.imagemachine.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.ImageFormat
import android.graphics.Matrix
import android.util.Size
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * CameraX manager for low-latency frame access.
 * 
 * This class manages the camera lifecycle, preview, and frame analysis for the image machine.
 * It uses CameraX's ImageAnalysis use case for efficient frame access without blocking the UI.
 */
class CameraManager(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    private var cameraProvider: ProcessCameraProvider? = null
    private var camera: Camera? = null
    private var imageAnalysis: ImageAnalysis? = null
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    
    // Frame callback
    private var onFrameAvailable: ((Bitmap) -> Unit)? = null
    
    companion object {
        // Target resolution for analysis (balance between quality and performance)
        private val ANALYSIS_SIZE = Size(640, 480)
        
        // Aspirational FPS target - 120fps requires high-end hardware
        // Note: CameraX does not provide direct FPS configuration via this constant.
        // Actual FPS depends on device capabilities and is measured at runtime.
        private const val TARGET_FPS_ASPIRATIONAL = 120
    }
    
    /**
     * Initialize and start camera with preview and analysis.
     * 
     * @param onFrameCallback Callback invoked for each analyzed frame
     * @return true if camera started successfully, false otherwise
     */
    fun startCamera(onFrameCallback: (Bitmap) -> Unit): Boolean {
        this.onFrameAvailable = onFrameCallback
        
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        
        try {
            cameraProviderFuture.addListener({
                try {
                    cameraProvider = cameraProviderFuture.get()
                    bindCameraUseCases()
                } catch (e: Exception) {
                    // Failed to get camera provider
                }
            }, ContextCompat.getMainExecutor(context))
            
            return true
        } catch (e: Exception) {
            return false
        }
    }
    
    /**
     * Bind camera use cases: Preview and ImageAnalysis.
     */
    private fun bindCameraUseCases() {
        val cameraProvider = cameraProvider ?: return
        
        // Unbind all before rebinding
        cameraProvider.unbindAll()
        
        // Set up Preview use case
        val preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
        
        // Set up ImageAnalysis use case with high-performance configuration
        imageAnalysis = ImageAnalysis.Builder()
            .setTargetResolution(ANALYSIS_SIZE)
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
            .build()
            .also { analysis ->
                analysis.setAnalyzer(cameraExecutor) { imageProxy ->
                    processImageProxy(imageProxy)
                }
            }
        
        // Select back camera
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
        
        try {
            // Bind use cases to camera
            camera = cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalysis
            )
            
        } catch (e: Exception) {
            // Camera binding failed
        }
    }
    
    /**
     * Process ImageProxy and convert to Bitmap for inference.
     */
    private fun processImageProxy(imageProxy: ImageProxy) {
        try {
            // Convert ImageProxy to Bitmap
            val bitmap = imageProxyToBitmap(imageProxy)
            
            // Invoke callback with frame
            onFrameAvailable?.invoke(bitmap)
            
        } finally {
            // Always close the image proxy
            imageProxy.close()
        }
    }
    
    /**
     * Convert ImageProxy to Bitmap efficiently.
     * Assumes RGBA_8888 format from ImageAnalysis configuration.
     */
    private fun imageProxyToBitmap(imageProxy: ImageProxy): Bitmap {
        val planes = imageProxy.planes
        val buffer = planes[0].buffer
        val pixelStride = planes[0].pixelStride
        val rowStride = planes[0].rowStride
        val rowPadding = rowStride - pixelStride * imageProxy.width
        
        // Create bitmap from buffer
        val bitmap = Bitmap.createBitmap(
            imageProxy.width + rowPadding / pixelStride,
            imageProxy.height,
            Bitmap.Config.ARGB_8888
        )
        bitmap.copyPixelsFromBuffer(buffer)
        
        // Crop to actual image size if there's row padding
        return if (rowPadding > 0) {
            Bitmap.createBitmap(bitmap, 0, 0, imageProxy.width, imageProxy.height)
        } else {
            bitmap
        }
    }
    
    /**
     * Stop camera and release resources.
     */
    fun stopCamera() {
        cameraProvider?.unbindAll()
        cameraExecutor.shutdown()
    }
    
    /**
     * Check if camera is currently bound.
     */
    fun isCameraActive(): Boolean {
        return camera != null
    }
    
    /**
     * Get camera capabilities (for FPS info).
     */
    fun getCameraInfo(): String {
        val cameraInfo = camera?.cameraInfo ?: return "Camera not initialized"
        return buildString {
            append("Camera: ${cameraInfo.cameraSelector}\n")
            append("Target FPS: $TARGET_FPS_ASPIRATIONAL (device-dependent, measured at runtime)\n")
            append("Analysis Resolution: ${ANALYSIS_SIZE.width}x${ANALYSIS_SIZE.height}")
        }
    }
}
