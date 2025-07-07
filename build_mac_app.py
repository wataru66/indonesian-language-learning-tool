#!/usr/bin/env python3
"""
Mac用Fletアプリケーションビルドスクリプト
Build script for Mac Flet application
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """必要な依存関係をチェック"""
    print("Checking build dependencies...")
    
    # Check if flet is installed
    try:
        import flet
        print("✓ Flet is available")
    except ImportError:
        print("✗ Flet is not installed. Please run: pip install flet")
        return False
    
    # Check if flet pack command is available
    try:
        result = subprocess.run(["flet", "pack", "--help"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Flet pack command is available")
        else:
            print("✗ Flet pack command not found")
            return False
    except FileNotFoundError:
        print("✗ Flet command not found in PATH")
        return False
    
    return True

def clean_build_directory():
    """ビルドディレクトリをクリーンアップ"""
    print("Cleaning build directories...")
    
    build_dirs = ["build", "dist", "*.spec"]
    for dir_pattern in build_dirs:
        if '*' in dir_pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(dir_pattern):
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Removed: {path}")
        else:
            if os.path.exists(dir_pattern):
                shutil.rmtree(dir_pattern)
                print(f"Removed directory: {dir_pattern}")

def create_app_icon():
    """アプリケーションアイコンを作成"""
    print("Creating application icon...")
    
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple icon file (placeholder)
    icon_path = assets_dir / "app_icon.png"
    if not icon_path.exists():
        # Create a simple colored rectangle as placeholder icon
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 256x256 icon
            img = Image.new('RGB', (256, 256), color='#2E7D32')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = "インドネシア語\n学習ツール"
            draw.text((128, 128), text, fill='white', font=font, anchor='mm')
            
            img.save(icon_path)
            print(f"Created icon: {icon_path}")
            
        except ImportError:
            print("PIL not available, creating placeholder icon file")
            with open(icon_path, 'w') as f:
                f.write("# Placeholder icon file")
    
    return icon_path

def build_mac_app():
    """Mac用アプリケーションをビルド"""
    print("Building Mac application...")
    
    # Create icon
    icon_path = create_app_icon()
    
    # Build command for macOS
    cmd = [
        "flet", "pack",
        "main.py",
        "--name", "Indonesian Language Learning Tool",
        "--add-data", "sample_data:sample_data",
        "--add-data", "assets:assets", 
        "--icon", str(icon_path),
        "--onefile",
        "--windowed"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build successful!")
        print(result.stdout)
        
        # Check if the app was created
        dist_dir = Path("dist")
        if dist_dir.exists():
            app_files = list(dist_dir.glob("*.app"))
            if app_files:
                print(f"✓ Mac app created: {app_files[0]}")
            else:
                executable_files = list(dist_dir.glob("*"))
                if executable_files:
                    print(f"✓ Executable created: {executable_files[0]}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_dmg_installer():
    """DMGインストーラーを作成（オプション）"""
    print("Creating DMG installer...")
    
    dist_dir = Path("dist")
    app_files = list(dist_dir.glob("*.app"))
    
    if not app_files:
        print("No .app file found, skipping DMG creation")
        return
    
    app_file = app_files[0]
    dmg_name = "Indonesian_Language_Learning_Tool.dmg"
    
    # Create DMG using hdiutil (macOS built-in tool)
    try:
        # Create a temporary directory for DMG contents
        temp_dir = Path("temp_dmg")
        temp_dir.mkdir(exist_ok=True)
        
        # Copy app to temp directory
        shutil.copytree(app_file, temp_dir / app_file.name)
        
        # Create DMG
        cmd = [
            "hdiutil", "create",
            "-volname", "Indonesian Language Learning Tool",
            "-srcfolder", str(temp_dir),
            "-ov", "-format", "UDZO",
            dmg_name
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ DMG created: {dmg_name}")
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ DMG creation failed: {e}")
    except Exception as e:
        print(f"✗ DMG creation error: {e}")

def main():
    """メイン関数"""
    print("Indonesian Language Learning Tool - Mac App Builder")
    print("=" * 60)
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("⚠️  This script is designed for macOS")
        print("For other platforms, please use the regular flet pack command")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Required dependencies not found")
        print("Please install flet: pip install flet")
        return 1
    
    # Clean previous builds
    clean_build_directory()
    
    # Build the app
    if build_mac_app():
        print("\n✅ Mac app build completed successfully!")
        
        # Optionally create DMG
        create_dmg = input("\nCreate DMG installer? (y/n): ").lower().strip()
        if create_dmg == 'y':
            create_dmg_installer()
        
        print("\n🎉 Build process completed!")
        print("\nTo run the app:")
        print("1. Navigate to the 'dist' directory")
        print("2. Double-click the .app file")
        print("   OR")
        print("3. Run from terminal: open dist/*.app")
        
    else:
        print("\n❌ Build failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())