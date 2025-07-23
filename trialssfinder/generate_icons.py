from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with TF text"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#0056b3')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        # Adjust font size based on icon size
        font_size = int(size * 0.4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw white text
    text = "TF"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)
    
    # Save the image
    img.save(filename)
    print(f"Created {filename}")

# Create the public directory if it doesn't exist
public_dir = "public"
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

# Generate icons
create_icon(16, os.path.join(public_dir, "favicon.ico"))
create_icon(192, os.path.join(public_dir, "logo192.png"))
create_icon(512, os.path.join(public_dir, "logo512.png"))

print("Icons generated successfully!")