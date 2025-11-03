# ============================================================
# ⚡️ GPU-Optimized Batch Background Replacer (Final No-Overwrite)
# ------------------------------------------------------------
# ✅ Uses rembg (with GPU via onnxruntime-gpu if available)
# ✅ Works for JPG, JPEG, PNG, BMP, GIF (static only), TIFF
# ✅ Case-insensitive file detection
# ✅ Handles duplicates: Adds _1, _2 etc. to avoid overwrite
# ✅ Logs every saved file name
# ✅ Counts actual unique outputs
#
# 🔧 Installation: pip install pillow rembg onnxruntime-gpu tqdm
#
# 🪄 Usage: python bg_final_no_overwrite.py
# ============================================================

import os
import glob
from PIL import Image
from rembg import remove
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog

def find_images(current_dir):
    """Find images with case-insensitive extension matching."""
    image_patterns = (
        '*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff',
        '*.JPG', '*.JPEG', '*.PNG', '*.BMP', '*.GIF', '*.TIFF'
    )
    images = []
    for pattern in image_patterns:
        images.extend(glob.glob(os.path.join(current_dir, pattern)))
    images = list(set(images))  # Remove exact duplicates
    return sorted(images)

def is_animated_gif(image_path):
    """Check if GIF is animated."""
    try:
        with Image.open(image_path) as img:
            return img.is_animated
    except:
        return False

def get_unique_output_path(output_dir, base_name, ext=".png"):
    """Generate unique filename: base.png → base_1.png if exists."""
    output_path = os.path.join(output_dir, base_name + ext)
    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    return output_path

def main():
    print("🔍 Scanning for images in current folder...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    images = find_images(current_dir)

    if not images:
        print("❌ No images found. Tip: Place images in same folder.")
        return

    print(f"🖼️ Found {len(images)} images: {', '.join([os.path.basename(p) for p in images[:5]])}...")

    # Background picker
    root = tk.Tk()
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    background_path = filedialog.askopenfilename(
        title="🖼️ Select Background Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.JPG *.JPEG *.PNG *.BMP *.GIF *.TIFF")]
    )
    root.destroy()

    if not background_path:
        print("❌ No background selected. Exiting...")
        return

    try:
        background = Image.open(background_path).convert('RGBA')
    except Exception as e:
        print(f"❌ Error loading background: {e}")
        return

    output_dir = os.path.join(current_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🧠 Background: {os.path.basename(background_path)}")
    print(f"📁 Output: {output_dir}")
    print(f"🖼️ Processing: {len(images)} images")
    print("⚡ GPU if available\n")

    success_count = 0
    fail_count = 0

    for image_path in tqdm(images, desc="Processing", unit="img"):
        try:
            file_name = os.path.basename(image_path)
            base_name = os.path.splitext(file_name)[0]
            ext = os.path.splitext(file_name)[1].lower()

            if ext == '.gif' and is_animated_gif(image_path):
                print(f"\n⚠️ Skipping animated GIF: {file_name}")
                fail_count += 1
                continue

            img = Image.open(image_path).convert("RGBA")
            removed_bg = remove(img)
            resized_bg = background.resize(img.size).convert('RGBA')
            removed_bg = removed_bg.convert('RGBA')
            result = Image.alpha_composite(resized_bg, removed_bg)

            output_path = get_unique_output_path(output_dir, base_name)
            result.save(output_path, "PNG")
            
            print(f"💾 Saved: {os.path.basename(output_path)}")  # Log each save
            success_count += 1

        except Exception as e:
            print(f"\n⚠️ Error on {file_name}: {e}")
            fail_count += 1

    # Actual count in folder
    output_files = glob.glob(os.path.join(output_dir, "*.png"))
    actual_count = len(output_files)

    print(f"\n🎉 Done!")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed/Skipped: {fail_count}")
    print(f"📁 Unique outputs: {actual_count} (in {output_dir})")

if __name__ == "__main__":
    main()