#!/usr/bin/env python3
"""
アプリケーションアイコン作成スクリプト
Application Icon Creation Script
"""

import os
from pathlib import Path

def create_app_icon():
    """アプリケーションアイコンを作成"""
    print("Creating application icon...")
    
    # Create assets directory
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Try to create icon with PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create multiple sizes for macOS
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        for size in sizes:
            # Create base image
            img = Image.new('RGB', (size, size), color='#2E7D32')
            draw = ImageDraw.Draw(img)
            
            # Calculate font size based on image size
            font_size = max(size // 12, 8)
            
            # Try to use system font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                try:
                    font = ImageFont.truetype("Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Add text
            if size >= 64:
                text = "インドネシア語\n学習ツール"
            else:
                text = "ID"
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position to center text
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Draw text
            draw.text((x, y), text, fill='white', font=font)
            
            # Save icon
            icon_path = assets_dir / f"app_icon_{size}x{size}.png"
            img.save(icon_path)
            print(f"Created: {icon_path}")
        
        # Create main icon
        main_icon = assets_dir / "app_icon.png"
        img_256 = Image.new('RGB', (256, 256), color='#2E7D32')
        draw = ImageDraw.Draw(img_256)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        text = "インドネシア語\n学習ツール"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (256 - text_width) // 2
        y = (256 - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        img_256.save(main_icon)
        print(f"Created main icon: {main_icon}")
        
        # Create icns file for macOS
        try:
            create_icns_file(assets_dir)
        except Exception as e:
            print(f"Warning: Could not create .icns file: {e}")
        
        return True
        
    except ImportError:
        print("PIL not available, creating placeholder icon")
        create_placeholder_icon(assets_dir)
        return False

def create_icns_file(assets_dir):
    """macOS用.icnsファイルを作成"""
    try:
        import subprocess
        
        # Check if iconutil is available (macOS only)
        if os.system("which iconutil > /dev/null 2>&1") != 0:
            print("iconutil not found, skipping .icns creation")
            return
        
        # Create iconset directory
        iconset_dir = assets_dir / "AppIcon.iconset"
        iconset_dir.mkdir(exist_ok=True)
        
        # Icon mapping for macOS
        icon_mapping = {
            16: "icon_16x16.png",
            32: ["icon_16x16@2x.png", "icon_32x32.png"],
            64: "icon_32x32@2x.png",
            128: ["icon_64x64@2x.png", "icon_128x128.png"],
            256: ["icon_128x128@2x.png", "icon_256x256.png"],
            512: ["icon_256x256@2x.png", "icon_512x512.png"],
            1024: "icon_512x512@2x.png"
        }
        
        # Copy icons to iconset
        for size, filenames in icon_mapping.items():
            source = assets_dir / f"app_icon_{size}x{size}.png"
            if source.exists():
                if isinstance(filenames, list):
                    for filename in filenames:
                        dest = iconset_dir / filename
                        import shutil
                        shutil.copy2(source, dest)
                else:
                    dest = iconset_dir / filenames
                    import shutil
                    shutil.copy2(source, dest)
        
        # Create .icns file
        icns_path = assets_dir / "app_icon.icns"
        cmd = ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Created .icns file: {icns_path}")
            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
        else:
            print(f"Failed to create .icns file: {result.stderr}")
            
    except Exception as e:
        print(f"Error creating .icns file: {e}")

def create_placeholder_icon(assets_dir):
    """プレースホルダーアイコンを作成"""
    icon_path = assets_dir / "app_icon.png"
    
    # Create a simple SVG-like text file that can be converted later
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
    <rect width="256" height="256" fill="#2E7D32"/>
    <text x="128" y="120" text-anchor="middle" fill="white" font-size="24" font-family="Arial">
        インドネシア語
    </text>
    <text x="128" y="150" text-anchor="middle" fill="white" font-size="24" font-family="Arial">
        学習ツール
    </text>
</svg>'''
    
    svg_path = assets_dir / "app_icon.svg"
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    # Create a simple placeholder PNG description
    with open(icon_path, 'w', encoding='utf-8') as f:
        f.write("# Placeholder icon file\n")
        f.write("# Please install PIL (pip install pillow) to create actual icon\n")
        f.write("# Or use the SVG file: app_icon.svg\n")
    
    print(f"Created placeholder icon: {icon_path}")
    print(f"Created SVG icon: {svg_path}")

def main():
    """メイン関数"""
    print("Indonesian Language Learning Tool - Icon Creator")
    print("=" * 50)
    
    if create_app_icon():
        print("\n✅ Application icons created successfully!")
        print("Icons are available in the 'assets' directory")
    else:
        print("\n⚠️  Placeholder icons created")
        print("Install PIL for better icons: pip install pillow")
    
    return 0

if __name__ == "__main__":
    main()