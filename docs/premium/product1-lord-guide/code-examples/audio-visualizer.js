/**
 * LORD Dashboard - Audio Visualization Component
 * Real-time audio visualization with WebGL rendering
 * 
 * Complete LORD Integration Guide - Chapter 7
 */

class AudioVisualizer {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    // Configuration
    this.config = {
      fftSize: options.fftSize || 2048,
      smoothingTimeConstant: options.smoothing || 0.8,
      barWidth: options.barWidth || 2,
      barGap: options.barGap || 1,
      colorScheme: options.colorScheme || 'spectrum',
      ...options
    };
    
    // Audio context
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.animationId = null;
  }

  /**
   * Initialize audio input from microphone
   */
  async initialize() {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false
        } 
      });

      // Create audio context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      
      // Configure analyser
      this.analyser.fftSize = this.config.fftSize;
      this.analyser.smoothingTimeConstant = this.config.smoothingTimeConstant;
      
      // Connect audio source
      const source = this.audioContext.createMediaStreamSource(stream);
      source.connect(this.analyser);
      
      // Initialize data array
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
      
      console.log('✅ Audio visualizer initialized');
      return true;
    } catch (error) {
      console.error('❌ Failed to initialize audio:', error);
      return false;
    }
  }

  /**
   * Start visualization loop
   */
  start() {
    if (!this.audioContext) {
      console.error('Audio not initialized. Call initialize() first.');
      return;
    }

    const render = () => {
      this.animationId = requestAnimationFrame(render);
      
      // Get frequency data
      this.analyser.getByteFrequencyData(this.dataArray);
      
      // Clear canvas
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      
      // Draw visualization
      this.drawBars();
    };

    render();
  }

  /**
   * Draw frequency bars
   */
  drawBars() {
    const barCount = this.dataArray.length;
    const barWidth = this.config.barWidth;
    const barGap = this.config.barGap;
    const totalBarWidth = barWidth + barGap;

    for (let i = 0; i < barCount; i++) {
      const value = this.dataArray[i];
      const percent = value / 255;
      const height = this.canvas.height * percent;
      const x = i * totalBarWidth;
      const y = this.canvas.height - height;

      // Color gradient
      const hue = (i / barCount) * 360;
      this.ctx.fillStyle = `hsl(${hue}, 100%, ${50 + percent * 50}%)`;
      
      // Draw bar
      this.ctx.fillRect(x, y, barWidth, height);
    }
  }

  /**
   * Stop visualization
   */
  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  /**
   * Update configuration
   */
  updateConfig(options) {
    this.config = { ...this.config, ...options };
    
    if (this.analyser && options.fftSize) {
      this.analyser.fftSize = options.fftSize;
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    }
  }
}

// Export for use in LORD dashboard
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioVisualizer;
}
