#!/bin/bash

# Android Image Machine Build Validation Script
# This script checks that the project structure is complete and provides build instructions

set -e

echo "=== Android Image Machine Build Validation ==="
echo ""

# Check directory structure
echo "Checking project structure..."
REQUIRED_DIRS=(
    "android"
    "android/ImageMachine"
    "android/ImageMachine/app"
    "android/ImageMachine/app/src/main"
    "android/ImageMachine/app/src/test"
    "android/ImageMachine/app/src/androidTest"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir"
    else
        echo "✗ $dir (missing)"
        exit 1
    fi
done

echo ""
echo "Checking required files..."
REQUIRED_FILES=(
    "android/settings.gradle.kts"
    "android/build.gradle.kts"
    "android/gradle.properties"
    "android/gradlew"
    "android/ImageMachine/app/build.gradle.kts"
    "android/ImageMachine/app/src/main/AndroidManifest.xml"
    "android/ImageMachine/app/src/main/java/com/evezart/imagemachine/MainActivity.kt"
    "android/ImageMachine/app/src/main/java/com/evezart/imagemachine/ml/OverlayModelInference.kt"
    "android/ImageMachine/app/src/main/java/com/evezart/imagemachine/utils/CameraManager.kt"
    "android/ImageMachine/app/src/main/java/com/evezart/imagemachine/utils/OverlayRenderer.kt"
    "android/README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (missing)"
        exit 1
    fi
done

echo ""
echo "=== Validation Complete ==="
echo ""
echo "Project structure is correct!"
echo ""
echo "To build the Android app:"
echo "  1. Install Android Studio (https://developer.android.com/studio)"
echo "  2. Open the 'android' directory in Android Studio"
echo "  3. Let Gradle sync"
echo "  4. Build > Make Project"
echo ""
echo "Or from command line (requires Android SDK):"
echo "  cd android"
echo "  ./gradlew build"
echo ""
echo "See android/README.md for complete instructions."

