#!/usr/bin/env python3
import os
import sys
from PIL import Image

MAX_WIDTH = 1900
MAX_HEIGHT = 1200
QUALITY = 85

if len(sys.argv) != 3:
    print("Usage: python3 resize_simple.py <input_dir> <output_dir>")
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = sys.argv[2]

if not os.path.isdir(input_dir):
    print(f"Error: {input_dir} does not exist")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)

files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
print(f"Processing {len(files)} images...")

for filename in sorted(files):
    try:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        img = Image.open(input_path)
        orig_size = os.path.getsize(input_path) / (1024 * 1024)
        
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)
        
        new_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✓ {filename}: {orig_size:.2f}MB -> {new_size:.2f}MB")
        
    except Exception as e:
        print(f"✗ {filename}: {e}")

print("Done!")
