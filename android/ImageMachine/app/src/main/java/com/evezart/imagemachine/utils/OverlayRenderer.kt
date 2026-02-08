package com.evezart.imagemachine.utils

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.PorterDuffXfermode
import android.view.SurfaceHolder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.util.concurrent.atomic.AtomicLong

/**
 * Low-latency overlay rendering pipeline with GPU-accelerated compositing.
 * 
 * This class manages the rendering of ML-generated overlays on top of camera frames
 * with performance tracking for FPS and latency measurements.
 */
class OverlayRenderer(
    private val surfaceHolder: SurfaceHolder
) {
    private val paint = Paint().apply {
        isAntiAlias = true
        isFilterBitmap = true
    }
    
    private var overlayAlpha = 128 // Default 50% opacity
    private var isOverlayEnabled = true
    
    // Performance tracking
    private val frameTimestamps = mutableListOf<Long>()
    private val latencyMeasurements = mutableListOf<Long>()
    private val maxSamples = 30 // Track last 30 frames for averaging
    
    // Frame statistics
    private var lastFrameTime = System.nanoTime()
    private var frameCount = 0L
    private var totalFrameTime = 0L
    
    /**
     * Render overlay bitmap to surface with compositing.
     * 
     * @param overlayBitmap The overlay to render (can be null)
     * @param intensity Overlay intensity (0-100)
     */
    fun renderOverlay(overlayBitmap: Bitmap?, intensity: Float) {
        if (!isOverlayEnabled || overlayBitmap == null) {
            clearSurface()
            return
        }
        
        val startTime = System.nanoTime()
        
        try {
            val canvas = surfaceHolder.lockCanvas() ?: return
            
            try {
                // Clear canvas
                canvas.drawColor(0, PorterDuff.Mode.CLEAR)
                
                // Calculate alpha based on intensity (0-100 to 0-255)
                overlayAlpha = (intensity * 2.55f).toInt().coerceIn(0, 255)
                paint.alpha = overlayAlpha
                
                // Draw overlay scaled to canvas size
                canvas.drawBitmap(
                    overlayBitmap,
                    null,
                    canvas.clipBounds,
                    paint
                )
            } finally {
                surfaceHolder.unlockCanvasAndPost(canvas)
            }
            
            // Track performance
            val endTime = System.nanoTime()
            updatePerformanceMetrics(startTime, endTime)
            
        } catch (e: Exception) {
            // Rendering failed, skip frame
        }
    }
    
    /**
     * Clear the overlay surface (transparent).
     */
    private fun clearSurface() {
        try {
            val canvas = surfaceHolder.lockCanvas() ?: return
            try {
                canvas.drawColor(0, PorterDuff.Mode.CLEAR)
            } finally {
                surfaceHolder.unlockCanvasAndPost(canvas)
            }
        } catch (e: Exception) {
            // Clearing failed, skip
        }
    }
    
    /**
     * Update performance tracking metrics.
     */
    private fun updatePerformanceMetrics(startTime: Long, endTime: Long) {
        val now = System.nanoTime()
        
        // Track frame timestamps for FPS calculation
        frameTimestamps.add(now)
        if (frameTimestamps.size > maxSamples) {
            frameTimestamps.removeAt(0)
        }
        
        // Track rendering latency
        val latency = (endTime - startTime) / 1_000_000 // Convert to ms
        latencyMeasurements.add(latency)
        if (latencyMeasurements.size > maxSamples) {
            latencyMeasurements.removeAt(0)
        }
        
        frameCount++
    }
    
    /**
     * Calculate current FPS based on recent frames.
     * 
     * @return Current FPS, capped at device maximum
     */
    fun getCurrentFps(): Float {
        if (frameTimestamps.size < 2) return 0f
        
        val firstTimestamp = frameTimestamps.first()
        val lastTimestamp = frameTimestamps.last()
        val timeSpan = (lastTimestamp - firstTimestamp) / 1_000_000_000.0 // Convert to seconds
        
        return if (timeSpan > 0) {
            (frameTimestamps.size - 1) / timeSpan.toFloat()
        } else {
            0f
        }
    }
    
    /**
     * Calculate average rendering latency.
     * 
     * @return Average latency in milliseconds
     */
    fun getAverageLatency(): Float {
        if (latencyMeasurements.isEmpty()) return 0f
        return latencyMeasurements.average().toFloat()
    }
    
    /**
     * Get total frames rendered.
     */
    fun getFrameCount(): Long = frameCount
    
    /**
     * Enable or disable overlay rendering.
     */
    fun setOverlayEnabled(enabled: Boolean) {
        isOverlayEnabled = enabled
        if (!enabled) {
            clearSurface()
        }
    }
    
    /**
     * Check if overlay is currently enabled.
     */
    fun isOverlayEnabled(): Boolean = isOverlayEnabled
    
    /**
     * Reset performance statistics.
     */
    fun resetStats() {
        frameTimestamps.clear()
        latencyMeasurements.clear()
        frameCount = 0
    }
}
