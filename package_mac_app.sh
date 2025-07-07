#!/bin/bash
# Mac用Fletアプリケーションパッケージ作成スクリプト
# Mac Flet Application Packaging Script

set -e  # Exit on any error

echo "🚀 Indonesian Language Learning Tool - Mac App Packaging"
echo "========================================================"

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if flet is installed
if ! python3 -c "import flet" &> /dev/null; then
    echo "❌ Flet is not installed"
    echo "Please install: pip install flet"
    exit 1
fi

# Create assets directory and icon
echo "📁 Creating assets directory..."
mkdir -p assets

# Create a simple app icon using ImageMagick if available
if command -v convert &> /dev/null; then
    echo "🎨 Creating app icon..."
    convert -size 256x256 xc:'#2E7D32' \
        -gravity center \
        -pointsize 24 \
        -fill white \
        -annotate +0+0 "インドネシア語\n学習ツール" \
        assets/app_icon.png
    echo "✅ App icon created"
else
    echo "⚠️  ImageMagick not found, using placeholder icon"
    echo "# Placeholder icon" > assets/app_icon.png
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the application
echo "🔨 Building Mac application..."

# Method 1: Use flet pack directly
echo "📦 Using flet pack..."
python3 -m flet pack main.py \
    --name "Indonesian Language Learning Tool" \
    --add-data "sample_data:sample_data" \
    --add-data "assets:assets" \
    --icon "assets/app_icon.png" \
    --onefile \
    --windowed

# Check if build was successful
if [ -d "dist" ]; then
    echo "✅ Build successful!"
    
    # List contents of dist directory
    echo "📋 Build output:"
    ls -la dist/
    
    # Check for .app bundle
    if ls dist/*.app 1> /dev/null 2>&1; then
        APP_NAME=$(ls dist/*.app | head -1)
        echo "🎉 Mac app created: $APP_NAME"
        
        # Make the app executable
        chmod +x "$APP_NAME/Contents/MacOS/"*
        
        # Optional: Create DMG installer
        read -p "Create DMG installer? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "💿 Creating DMG installer..."
            
            DMG_NAME="Indonesian_Language_Learning_Tool.dmg"
            
            # Create DMG
            hdiutil create -volname "Indonesian Language Learning Tool" \
                -srcfolder dist \
                -ov -format UDZO \
                "$DMG_NAME"
            
            if [ -f "$DMG_NAME" ]; then
                echo "✅ DMG created: $DMG_NAME"
            else
                echo "❌ DMG creation failed"
            fi
        fi
        
    else
        echo "⚠️  No .app bundle found, checking for executable..."
        if ls dist/* 1> /dev/null 2>&1; then
            EXECUTABLE=$(ls dist/* | head -1)
            echo "📱 Executable created: $EXECUTABLE"
            chmod +x "$EXECUTABLE"
        fi
    fi
    
    echo ""
    echo "🎯 Installation Instructions:"
    echo "1. Navigate to the 'dist' directory"
    echo "2. Double-click the .app file to run"
    echo "   OR"
    echo "3. Run from terminal: open dist/*.app"
    echo ""
    echo "📂 To install system-wide:"
    echo "   Copy the .app file to /Applications/"
    echo "   cp -r dist/*.app /Applications/"
    
else
    echo "❌ Build failed - no dist directory found"
    exit 1
fi

echo ""
echo "🎉 Mac app packaging completed!"