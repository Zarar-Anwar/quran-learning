#!/usr/bin/env python3
"""
Favicon Generator Script for LearnQuranOnlinee.com

This script helps generate proper favicon files from the existing fav_logo.png
to ensure consistent favicon display across all browsers and search engines.

Usage:
    python generate_favicons.py

Requirements:
    pip install Pillow
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import shutil

def create_favicon_files():
    """Create favicon files in various sizes"""
    
    # Define favicon sizes
    favicon_sizes = [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (96, 96),
        (128, 128),
        (180, 180),
        (192, 192),
        (512, 512)
    ]
    
    # Apple touch icon sizes
    apple_sizes = [
        (57, 57),
        (60, 60),
        (72, 72),
        (76, 76),
        (114, 114),
        (120, 120),
        (144, 144),
        (152, 152),
        (180, 180)
    ]
    
    # Source favicon path
    source_favicon = "static/fav_logo.png"
    
    if not os.path.exists(source_favicon):
        print(f"Error: Source favicon not found at {source_favicon}")
        return False
    
    try:
        # Open the source image
        with Image.open(source_favicon) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create favicon directory
            favicon_dir = "static/favicons"
            os.makedirs(favicon_dir, exist_ok=True)
            
            # Generate standard favicons
            for width, height in favicon_sizes:
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                output_path = f"{favicon_dir}/favicon-{width}x{height}.png"
                resized_img.save(output_path, "PNG")
                print(f"Created: {output_path}")
            
            # Generate Apple touch icons
            for width, height in apple_sizes:
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                output_path = f"{favicon_dir}/apple-touch-icon-{width}x{height}.png"
                resized_img.save(output_path, "PNG")
                print(f"Created: {output_path}")
            
            # Create ICO file (16x16, 32x32, 48x48)
            ico_sizes = [(16, 16), (32, 32), (48, 48)]
            ico_images = []
            for width, height in ico_sizes:
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                ico_images.append(resized_img)
            
            ico_path = f"{favicon_dir}/favicon.ico"
            ico_images[0].save(ico_path, format='ICO', sizes=[(size[0], size[1]) for size in ico_sizes])
            print(f"Created: {ico_path}")
            
            # Copy the original as favicon.png
            shutil.copy2(source_favicon, f"{favicon_dir}/favicon.png")
            print(f"Copied: {favicon_dir}/favicon.png")
            
            print("\nFavicon generation completed successfully!")
            print(f"All favicon files are saved in: {favicon_dir}")
            
            return True
            
    except Exception as e:
        print(f"Error generating favicons: {e}")
        return False

def update_template_references():
    """Update template files to reference the new favicon directory"""
    
    template_files = [
        "src/web/website/templates/website/base.html",
        "templates/base.html",
        "templates/dev/starter-page.html"
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"Template file exists: {template_file}")
        else:
            print(f"Template file not found: {template_file}")

if __name__ == "__main__":
    print("Favicon Generator for LearnQuranOnlinee.com")
    print("=" * 50)
    
    # Check if Pillow is installed
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library is required.")
        print("Install it with: pip install Pillow")
        sys.exit(1)
    
    # Generate favicon files
    if create_favicon_files():
        print("\nNext steps:")
        print("1. Update your template files to reference the new favicon directory")
        print("2. Clear browser cache and test the favicon")
        print("3. Submit your sitemap to search engines for re-indexing")
    else:
        print("Favicon generation failed!")
        sys.exit(1)
