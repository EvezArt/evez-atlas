# Image Machine - Android Detail Enhancement Module

An Android application that projects an AI-generated detail-enhancing overlay on a live camera scene with ultra-low latency, acting as a UI accelerator.

## Overview

The Image Machine uses on-device TensorFlow Lite inference to generate real-time overlays on camera feed. It's designed for maximum performance with:
- **Target**: 120fps where hardware supports it; gracefully degrades on lower-end devices
- **Low latency**: Async inference pipeline, GPU acceleration, non-blocking UI
- **On-device**: No network required, runs entirely on device

## Features

- ✅ Real-time camera preview with CameraX
- ✅ On-device TFLite model inference (GPU-accelerated when available)
- ✅ Live overlay compositing
- ✅ Runtime controls (toggle overlay, adjust intensity)
- ✅ Performance monitoring (FPS, latency statistics)
- ✅ Proper camera permission handling
- ✅ Placeholder mode (works without a real ML model for testing)

## Requirements

### Device Requirements
- Android 7.0 (API 24) or higher
- Camera (rear camera required)
- For 120fps: High-end device with capable camera hardware
- GPU (recommended for faster inference)

### Build Requirements
- Android Studio Arctic Fox (2020.3.1) or newer
- Gradle 7.0+
- Android SDK 34
- Kotlin 1.9.20

## Setup Instructions

### 1. Clone and Open Project

```bash
cd android
# Open in Android Studio or build from command line
```

### 2. Build the Project

#### Using Android Studio:
1. Open the `android` directory in Android Studio
2. Let Gradle sync
3. Build → Make Project
4. Run on device or emulator

#### Using Command Line:
```bash
cd android
./gradlew build
./gradlew installDebug
```

### 3. Camera Permissions

The app will request camera permission on first launch. This is required for the app to function.

**Permissions declared in AndroidManifest.xml:**
- `android.permission.CAMERA` - Required for camera access

### 4. Add Your TFLite Model (Optional)

The app includes a placeholder overlay generator for testing. To use a real ML model:

1. Place your `.tflite` model in `app/src/main/assets/`
2. Update `MODEL_FILE_NAME` in `OverlayModelInference.kt`
3. Adjust input/output dimensions if needed
4. See `app/src/main/assets/MODEL_README.md` for details

## Architecture

### Pipeline Overview

```
┌──────────────┐
│ CameraX      │  Frame capture (640x480 @ max fps)
│ ImageAnalysis│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Background   │  Async inference on background thread
│ Inference    │  GPU-accelerated TFLite model
│ Thread       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Overlay      │  GPU compositing via SurfaceView
│ Renderer     │  Non-blocking UI thread
└──────────────┘
```

### Key Components

1. **MainActivity**: Main activity managing the pipeline
2. **CameraManager**: CameraX integration for low-latency frame access
3. **OverlayModelInference**: TFLite model interface with GPU support
4. **OverlayRenderer**: GPU-accelerated overlay compositing and performance tracking

### Low-Latency Design

- **Async inference**: Model runs on dedicated thread pool
- **Backpressure strategy**: `STRATEGY_KEEP_ONLY_LATEST` - drops frames if inference is slow
- **GPU acceleration**: TFLite GPU delegate when available
- **Efficient frame format**: RGBA_8888 for direct bitmap conversion
- **Non-blocking UI**: All heavy operations off main thread

## Performance

### FPS Capabilities

- **120fps target**: Achievable on high-end devices (Snapdragon 8 Gen 2+, etc.)
- **60fps**: Most modern devices (2020+)
- **30fps**: Older/budget devices
- **Actual FPS displayed**: Real-time measurement shown in app

### Latency Expectations

- **"Negative latency is not possible"**: Despite the ultra-low latency design, we cannot predict the future. The term "ultra-low latency" means:
  - Minimized processing delay (typically 5-20ms on modern devices)
  - GPU-accelerated pipeline
  - Async processing to avoid blocking
  - The overlay reflects recent frames, not future frames

### Performance Tips

1. **Use GPU acceleration**: Ensure device supports TFLite GPU delegate
2. **Optimize model**: Use quantized models (int8) for faster inference
3. **Reduce model size**: Smaller input resolution = faster inference
4. **Test on target device**: Performance varies greatly by hardware

## Usage

### Controls

- **Toggle Overlay Button**: Enable/disable overlay rendering
- **Intensity Slider**: Adjust overlay opacity (0-100%)
- **Stats Panel**: Shows real-time FPS and latency

### Stats Interpretation

- **FPS**: Frames per second (actual rendering rate)
- **Latency**: Average rendering time per frame (milliseconds)

## Limitations

1. **Frame rate ceiling**: Limited by device hardware; 120fps requires high-end devices
2. **Model complexity**: Complex models may reduce FPS significantly
3. **No future prediction**: Latency reduction has physical limits (negative latency impossible)
4. **Camera API limits**: Some devices may not support high frame rates via CameraX
5. **GPU availability**: Not all devices support TFLite GPU delegate

## Testing

### Without a Real Model

The app runs in placeholder mode, generating a simple edge-detection overlay. This allows you to:
- Test the pipeline performance
- Verify camera and rendering work correctly
- Measure baseline FPS and latency

### Unit Tests

```bash
./gradlew test
```

### Instrumentation Tests

```bash
./gradlew connectedAndroidTest
```

## Troubleshooting

### Camera not working
- Check camera permission is granted
- Ensure device has a rear camera
- Try restarting the app

### Low FPS
- Check device capabilities
- Try a smaller/simpler model
- Ensure GPU acceleration is available
- Close background apps

### Model not loading
- Verify `.tflite` file is in `assets/` directory
- Check filename matches `MODEL_FILE_NAME` constant
- Review model input/output tensor shapes

### Black screen
- Camera permission might be denied
- Check device compatibility (API 24+)
- Review Logcat for errors

## Development

### Project Structure

```
android/
├── build.gradle.kts           # Root build configuration
├── settings.gradle.kts        # Project settings
└── ImageMachine/
    └── app/
        ├── build.gradle.kts   # App module build config
        ├── src/
        │   ├── main/
        │   │   ├── AndroidManifest.xml
        │   │   ├── java/com/evezart/imagemachine/
        │   │   │   ├── MainActivity.kt
        │   │   │   ├── ml/
        │   │   │   │   └── OverlayModelInference.kt
        │   │   │   └── utils/
        │   │   │       ├── CameraManager.kt
        │   │   │       └── OverlayRenderer.kt
        │   │   ├── res/           # Resources (layouts, strings, etc.)
        │   │   └── assets/        # TFLite models go here
        │   ├── test/              # Unit tests
        │   └── androidTest/       # Instrumentation tests
        └── proguard-rules.pro     # ProGuard rules
```

### Adding Dependencies

Edit `app/build.gradle.kts` and sync Gradle.

### Modifying the UI

Edit layouts in `app/src/main/res/layout/` or strings in `values/strings.xml`.

## License

Part of the Evez666 repository. See main repository for license information.

## Support

For issues, questions, or contributions, see the main repository: https://github.com/EvezArt/Evez666
