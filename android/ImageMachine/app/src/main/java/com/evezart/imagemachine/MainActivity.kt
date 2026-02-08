package com.evezart.imagemachine

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.view.SurfaceHolder
import android.widget.SeekBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.evezart.imagemachine.ml.OverlayModelInference
import com.evezart.imagemachine.utils.CameraManager
import com.evezart.imagemachine.utils.OverlayRenderer
import com.google.android.material.button.MaterialButton
import android.view.SurfaceView
import android.widget.TextView
import kotlinx.coroutines.*
import java.util.concurrent.Executors

/**
 * Main Activity for the Image Machine application.
 * 
 * This activity manages:
 * - Camera preview and frame capture
 * - AI model inference for overlay generation
 * - Real-time overlay compositing
 * - Performance monitoring (FPS, latency)
 * - User controls (toggle overlay, adjust intensity)
 * 
 * The pipeline is designed for ultra-low latency:
 * - Async inference on background thread
 * - GPU-accelerated rendering where available
 * - Non-blocking UI thread
 * - Target 120fps where device supports it
 */
class MainActivity : AppCompatActivity() {
    
    // Views
    private lateinit var previewView: PreviewView
    private lateinit var overlayView: SurfaceView
    private lateinit var toggleButton: MaterialButton
    private lateinit var intensitySlider: SeekBar
    private lateinit var intensityValue: TextView
    private lateinit var fpsText: TextView
    private lateinit var latencyText: TextView
    
    // Core components
    private lateinit var cameraManager: CameraManager
    private lateinit var overlayRenderer: OverlayRenderer
    private var modelInference: OverlayModelInference? = null
    
    // Inference executor for async processing
    private val inferenceExecutor = Executors.newSingleThreadExecutor()
    
    // State
    private var isOverlayEnabled = true
    private var currentIntensity = 50f // 0-100
    
    // Performance tracking
    private var statsUpdateJob: Job? = null
    
    companion object {
        private const val CAMERA_PERMISSION_REQUEST_CODE = 1001
        private const val STATS_UPDATE_INTERVAL_MS = 100L // Update stats 10 times per second
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize views
        initializeViews()
        
        // Request camera permission
        if (checkCameraPermission()) {
            initializeImageMachine()
        } else {
            requestCameraPermission()
        }
    }
    
    /**
     * Initialize all view references.
     */
    private fun initializeViews() {
        previewView = findViewById(R.id.previewView)
        overlayView = findViewById(R.id.overlayView)
        toggleButton = findViewById(R.id.toggleOverlayButton)
        intensitySlider = findViewById(R.id.intensitySlider)
        intensityValue = findViewById(R.id.intensityValue)
        fpsText = findViewById(R.id.fpsText)
        latencyText = findViewById(R.id.latencyText)
        
        // Set up control listeners
        setupControls()
    }
    
    /**
     * Set up user control listeners.
     */
    private fun setupControls() {
        // Toggle overlay button
        toggleButton.setOnClickListener {
            isOverlayEnabled = !isOverlayEnabled
            overlayRenderer.setOverlayEnabled(isOverlayEnabled)
            
            toggleButton.text = if (isOverlayEnabled) {
                getString(R.string.overlay_enabled)
            } else {
                getString(R.string.overlay_disabled)
            }
        }
        
        // Intensity slider
        intensitySlider.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                currentIntensity = progress.toFloat()
                intensityValue.text = "$progress%"
            }
            
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
    }
    
    /**
     * Initialize the image machine pipeline.
     */
    private fun initializeImageMachine() {
        // Initialize overlay surface
        overlayView.holder.addCallback(object : SurfaceHolder.Callback {
            override fun surfaceCreated(holder: SurfaceHolder) {
                // Initialize renderer when surface is ready
                overlayRenderer = OverlayRenderer(holder)
            }
            
            override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {}
            override fun surfaceDestroyed(holder: SurfaceHolder) {}
        })
        
        // Initialize ML model
        try {
            modelInference = OverlayModelInference(this)
            Toast.makeText(
                this, 
                "Model loaded (GPU: ${modelInference?.isUsingGpu() == true})",
                Toast.LENGTH_SHORT
            ).show()
        } catch (e: Exception) {
            Toast.makeText(this, getString(R.string.model_load_failed), Toast.LENGTH_LONG).show()
        }
        
        // Initialize camera
        cameraManager = CameraManager(this, this, previewView)
        val cameraStarted = cameraManager.startCamera { frame ->
            processFrame(frame)
        }
        
        if (!cameraStarted) {
            Toast.makeText(this, getString(R.string.camera_init_failed), Toast.LENGTH_LONG).show()
            return
        }
        
        // Start performance stats updates
        startStatsUpdates()
    }
    
    /**
     * Process camera frame through inference pipeline.
     * 
     * This runs on a background thread to avoid blocking the camera pipeline.
     */
    private fun processFrame(frame: Bitmap) {
        if (!isOverlayEnabled) return
        
        // Run inference asynchronously
        inferenceExecutor.execute {
            try {
                // Generate overlay using ML model
                val overlay = modelInference?.runInference(frame)
                
                // Render overlay on main thread
                runOnUiThread {
                    if (::overlayRenderer.isInitialized) {
                        overlayRenderer.renderOverlay(overlay, currentIntensity)
                    }
                }
            } catch (e: Exception) {
                // Inference failed, skip frame
            }
        }
    }
    
    /**
     * Start periodic stats updates on UI.
     */
    private fun startStatsUpdates() {
        statsUpdateJob = lifecycleScope.launch(Dispatchers.Main) {
            while (isActive) {
                updateStats()
                delay(STATS_UPDATE_INTERVAL_MS)
            }
        }
    }
    
    /**
     * Update performance statistics on UI.
     */
    private fun updateStats() {
        if (::overlayRenderer.isInitialized) {
            val fps = overlayRenderer.getCurrentFps()
            val latency = overlayRenderer.getAverageLatency()
            
            fpsText.text = getString(R.string.fps_label, fps)
            latencyText.text = getString(R.string.latency_label, latency)
        }
    }
    
    /**
     * Check if camera permission is granted.
     */
    private fun checkCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    /**
     * Request camera permission from user.
     */
    private fun requestCameraPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.CAMERA),
            CAMERA_PERMISSION_REQUEST_CODE
        )
    }
    
    /**
     * Handle permission request result.
     */
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == CAMERA_PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted, initialize image machine
                initializeImageMachine()
            } else {
                // Permission denied
                Toast.makeText(
                    this,
                    getString(R.string.camera_permission_denied),
                    Toast.LENGTH_LONG
                ).show()
                finish()
            }
        }
    }
    
    /**
     * Clean up resources.
     */
    override fun onDestroy() {
        super.onDestroy()
        
        // Stop stats updates
        statsUpdateJob?.cancel()
        
        // Stop camera
        if (::cameraManager.isInitialized) {
            cameraManager.stopCamera()
        }
        
        // Clean up model
        modelInference?.close()
        
        // Shutdown executor
        inferenceExecutor.shutdown()
    }
}
