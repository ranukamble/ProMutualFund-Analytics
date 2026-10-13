import os
import shutil
import glob

# Paths
upload_dir = r"C:\Users\v2spl_p5nx879\.gemini\antigravity-ide\brain\20c29e1f-d1af-4dd9-a322-e3fe2de066b5\.user_uploaded"
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Ensure static directory exists
os.makedirs(static_dir, exist_ok=True)

# Find the latest image (png, jpg, jpeg) in the user uploaded directory
image_files = []
for ext in ["*.png", "*.jpg", "*.jpeg"]:
    image_files.extend(glob.glob(os.path.join(upload_dir, ext)))

if not image_files:
    print("No image files found in uploaded directory.")
else:
    # Get the newest file
    latest_img = max(image_files, key=os.path.getctime)
    dest_path = os.path.join(static_dir, "logo.png")
    
    # Copy it as logo.png
    shutil.copy(latest_img, dest_path)
    print(f"Successfully copied new logo from {latest_img} to: {dest_path}")
