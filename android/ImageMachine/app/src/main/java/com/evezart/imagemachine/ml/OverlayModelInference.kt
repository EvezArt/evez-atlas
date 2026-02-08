package com.evezart.imagemachine.ml

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

/**
 * TFLite model interface for detail enhancement overlay generation.
 * 
 * This class manages the TensorFlow Lite model that generates a detail-enhancing overlay
 * from camera frames. It includes GPU acceleration support for low-latency inference.
 * 
 * To use your own model:
 * 1. Place your .tflite model file in app/src/main/assets/
 * 2. Update MODEL_FILE_NAME constant
 * 3. Adjust input/output tensor shapes and preprocessing as needed
 */
class OverlayModelInference(context: Context) {
    
    companion object {
        // Model file name - this file is intentionally NOT included in assets
        // The app runs in placeholder mode when this file is absent
        // To use a real model: place your .tflite file in assets/ and update this name
        private const val OPTIONAL_MODEL_FILE_NAME = "detail_enhancer_placeholder.tflite"
        
        // Model input configuration - adjust based on your model
        private const val INPUT_WIDTH = 224
        private const val INPUT_HEIGHT = 224
        private const val INPUT_CHANNELS = 3
        private const val PIXEL_SIZE = 3 // RGB
        
        // Model output configuration - adjust based on your model
        private const val OUTPUT_WIDTH = 224
        private const val OUTPUT_HEIGHT = 224
        private const val OUTPUT_CHANNELS = 1 // Grayscale overlay
    }
    
    private var interpreter: Interpreter? = null
    private var gpuDelegate: GpuDelegate? = null
    private val isGpuAvailable: Boolean
    
    init {
        // Check GPU availability
        val compatList = CompatibilityList()
        isGpuAvailable = compatList.isDelegateSupportedOnThisDevice
        
        try {
            loadModel(context)
        } catch (e: Exception) {
            // Model loading failed - using placeholder mode
            interpreter = null
        }
    }
    
    /**
     * Load the TFLite model from assets.
     */
    private fun loadModel(context: Context) {
        val options = Interpreter.Options()
        
        // Enable GPU acceleration if available
        if (isGpuAvailable) {
            gpuDelegate = GpuDelegate()
            options.addDelegate(gpuDelegate)
        }
        
        // Use multiple threads for CPU inference
        options.setNumThreads(4)
        
        try {
            val modelBuffer = loadModelFile(context)
            interpreter = Interpreter(modelBuffer, options)
        } catch (e: Exception) {
            throw RuntimeException("Failed to load TFLite model: ${e.message}", e)
        }
    }
    
    /**
     * Load model file from assets as MappedByteBuffer.
     */
    private fun loadModelFile(context: Context): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(OPTIONAL_MODEL_FILE_NAME)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
    
    /**
     * Run inference on input bitmap and return overlay bitmap.
     * 
     * @param inputBitmap Camera frame as Bitmap
     * @return Overlay bitmap (can be null if using placeholder/stub)
     */
    fun runInference(inputBitmap: Bitmap): Bitmap? {
        if (interpreter == null) {
            // Placeholder mode: generate synthetic overlay
            return generatePlaceholderOverlay(inputBitmap)
        }
        
        try {
            // Preprocess input
            val inputBuffer = preprocessBitmap(inputBitmap)
            
            // Prepare output buffer
            val outputBuffer = ByteBuffer.allocateDirect(
                OUTPUT_WIDTH * OUTPUT_HEIGHT * OUTPUT_CHANNELS * 4 // float32
            ).apply {
                order(ByteOrder.nativeOrder())
            }
            
            // Run inference
            interpreter?.run(inputBuffer, outputBuffer)
            
            // Postprocess output to bitmap
            return postprocessOutput(outputBuffer)
        } catch (e: Exception) {
            // Inference failed, return placeholder
            return generatePlaceholderOverlay(inputBitmap)
        }
    }
    
    /**
     * Preprocess bitmap into model input format.
     */
    private fun preprocessBitmap(bitmap: Bitmap): ByteBuffer {
        val inputBuffer = ByteBuffer.allocateDirect(
            INPUT_WIDTH * INPUT_HEIGHT * INPUT_CHANNELS * 4 // float32
        ).apply {
            order(ByteOrder.nativeOrder())
        }
        
        // Resize bitmap if needed
        val scaledBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_WIDTH, INPUT_HEIGHT, true)
        
        // Convert to float array normalized to [0, 1]
        val pixels = IntArray(INPUT_WIDTH * INPUT_HEIGHT)
        scaledBitmap.getPixels(pixels, 0, INPUT_WIDTH, 0, 0, INPUT_WIDTH, INPUT_HEIGHT)
        
        for (pixel in pixels) {
            val r = ((pixel shr 16) and 0xFF) / 255.0f
            val g = ((pixel shr 8) and 0xFF) / 255.0f
            val b = (pixel and 0xFF) / 255.0f
            
            inputBuffer.putFloat(r)
            inputBuffer.putFloat(g)
            inputBuffer.putFloat(b)
        }
        
        return inputBuffer
    }
    
    /**
     * Convert model output to bitmap.
     */
    private fun postprocessOutput(outputBuffer: ByteBuffer): Bitmap {
        outputBuffer.rewind()
        
        val overlay = Bitmap.createBitmap(OUTPUT_WIDTH, OUTPUT_HEIGHT, Bitmap.Config.ARGB_8888)
        val pixels = IntArray(OUTPUT_WIDTH * OUTPUT_HEIGHT)
        
        for (i in pixels.indices) {
            val value = outputBuffer.float
            val grayValue = (value * 255).toInt().coerceIn(0, 255)
            
            // Create semi-transparent white overlay based on intensity
            val alpha = (grayValue * 0.5f).toInt() // 50% max opacity
            pixels[i] = (alpha shl 24) or (grayValue shl 16) or (grayValue shl 8) or grayValue
        }
        
        overlay.setPixels(pixels, 0, OUTPUT_WIDTH, 0, 0, OUTPUT_WIDTH, OUTPUT_HEIGHT)
        return overlay
    }
    
    /**
     * Generate a placeholder/synthetic overlay for testing without a real model.
     * This creates a simple edge-enhancement effect.
     */
    private fun generatePlaceholderOverlay(inputBitmap: Bitmap): Bitmap {
        val width = inputBitmap.width
        val height = inputBitmap.height
        val overlay = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        
        // Simple edge detection for placeholder
        val pixels = IntArray(width * height)
        inputBitmap.getPixels(pixels, 0, width, 0, 0, width, height)
        
        val overlayPixels = IntArray(width * height)
        
        for (y in 1 until height - 1) {
            for (x in 1 until width - 1) {
                val idx = y * width + x
                
                // Simple Sobel-like edge detection
                val center = pixels[idx]
                val left = pixels[idx - 1]
                val right = pixels[idx + 1]
                val top = pixels[idx - width]
                val bottom = pixels[idx + width]
                
                val centerGray = getLuminance(center)
                val dx = Math.abs(getLuminance(right) - getLuminance(left))
                val dy = Math.abs(getLuminance(bottom) - getLuminance(top))
                
                val edge = (dx + dy).coerceIn(0, 255)
                
                // Create semi-transparent cyan overlay for edges
                val alpha = (edge * 0.6f).toInt()
                overlayPixels[idx] = (alpha shl 24) or (0x00 shl 16) or (0xFF shl 8) or 0xFF
            }
        }
        
        overlay.setPixels(overlayPixels, 0, width, 0, 0, width, height)
        return overlay
    }
    
    /**
     * Get luminance (grayscale value) from RGB pixel.
     */
    private fun getLuminance(pixel: Int): Int {
        val r = (pixel shr 16) and 0xFF
        val g = (pixel shr 8) and 0xFF
        val b = pixel and 0xFF
        return (0.299 * r + 0.587 * g + 0.114 * b).toInt()
    }
    
    /**
     * Get model input dimensions.
     */
    fun getInputSize(): Pair<Int, Int> = Pair(INPUT_WIDTH, INPUT_HEIGHT)
    
    /**
     * Check if GPU acceleration is being used.
     */
    fun isUsingGpu(): Boolean = isGpuAvailable && interpreter != null
    
    /**
     * Clean up resources.
     */
    fun close() {
        interpreter?.close()
        gpuDelegate?.close()
    }
}
