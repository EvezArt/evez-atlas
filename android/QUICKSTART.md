# Quick Start Guide - Android Image Machine

Get up and running with the Image Machine in 5 minutes!

## Prerequisites

- Android Studio (Arctic Fox or newer)
- Android device or emulator with:
  - Android 7.0 (API 24) or higher
  - Camera support
  - Optional: GPU for faster inference

## Step 1: Open Project (1 minute)

```bash
# Clone the repository (if not already)
git clone https://github.com/EvezArt/Evez666.git
cd Evez666
```

Open Android Studio and select "Open an existing project", then navigate to the `android` directory.

## Step 2: Sync and Build (2 minutes)

1. Wait for Gradle sync to complete (Android Studio will do this automatically)
2. If prompted, install any missing SDK components
3. Click Build → Make Project (or press Ctrl+F9 / Cmd+F9)

## Step 3: Run on Device (1 minute)

### Option A: Physical Device
1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect via USB
4. Click Run (green play button) or press Shift+F10

### Option B: Emulator
1. Click AVD Manager (phone icon in toolbar)
2. Create a new virtual device if needed (Pixel 5 recommended)
3. Launch emulator
4. Click Run

## Step 4: Grant Camera Permission (30 seconds)

When the app launches:
1. Tap "Allow" when prompted for camera permission
2. The camera preview should appear immediately
3. You should see a cyan edge-detection overlay (placeholder mode)

## Step 5: Try the Controls (30 seconds)

- **Toggle Overlay button**: Turn overlay on/off
- **Intensity slider**: Adjust overlay opacity (0-100%)
- **Stats panel**: Watch real-time FPS and latency

## What You Should See

In placeholder mode (no ML model):
- Camera preview with cyan edge overlay
- FPS: 15-60 depending on device
- Latency: 5-20ms depending on device

## Next Steps

### Add a Real ML Model

1. Train or obtain a TFLite model for detail enhancement
2. Place it in `app/src/main/assets/your_model.tflite`
3. Update `MODEL_FILE_NAME` in `OverlayModelInference.kt`
4. Rebuild and run

See `MODEL_README.md` in assets for details.

### Customize the Overlay

Edit `generatePlaceholderOverlay()` in `OverlayModelInference.kt` to change the synthetic overlay effect.

### Optimize Performance

1. Use quantized INT8 models for 2-4x speedup
2. Reduce model input size (e.g., 128x128 instead of 224x224)
3. Enable GPU delegate (automatically done if available)
4. Test on high-end device for 60+ fps

## Troubleshooting

### "Camera permission denied"
- Grant camera permission in Settings → Apps → Image Machine → Permissions

### "Failed to load TFLite model"
- This is expected without a real model file
- The app will use placeholder mode (edge detection)
- No action needed unless you want to add a real model

### Black screen
- Check camera permission
- Try restarting the app
- Check Logcat for errors (View → Tool Windows → Logcat)

### Low FPS
- Normal on older devices or emulators
- Try on a physical device for better performance
- GPU emulation is often slow

### Build errors
- Ensure Android Studio is up to date
- File → Invalidate Caches / Restart
- Build → Clean Project, then Rebuild

## Getting Help

- See full documentation: `android/README.md`
- Technical details: `android/TECHNICAL_DETAILS.md`
- Report issues: https://github.com/EvezArt/Evez666/issues

## Success Checklist

- ✅ Camera preview displays
- ✅ Overlay toggles on/off
- ✅ Intensity slider works
- ✅ FPS/latency stats update
- ✅ No crashes or errors

Congratulations! Your Image Machine is running. 🎉
