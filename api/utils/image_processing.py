"""
Image processing utilities for generating thumbnails and optimizing images
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import sys
import os


def generate_thumbnail(image_field, max_size=(400, 400), quality=85):
    """
    Generate a thumbnail from an image field
    
    Args:
        image_field: Django ImageField instance
        max_size: Tuple of (width, height) for maximum thumbnail size
        quality: JPEG quality (1-100, higher is better quality but larger file)
    
    Returns:
        InMemoryUploadedFile: Thumbnail image file ready to be saved
    """
    if not image_field:
        return None
    
    try:
        # Open the original image - handle file objects properly
        if hasattr(image_field, 'read'):
            # It's a file-like object (InMemoryUploadedFile, etc.)
            image_field.seek(0)  # Reset file pointer
            img = Image.open(image_field)
            original_name = image_field.name if hasattr(image_field, 'name') else 'image.jpg'
        elif hasattr(image_field, 'path'):
            # It's a Django ImageField with a path (already saved)
            img = Image.open(image_field.path)
            original_name = os.path.basename(image_field.name)
        else:
            # Try to open it directly
            img = Image.open(image_field)
            original_name = getattr(image_field, 'name', 'image.jpg')
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate thumbnail size maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Create a BytesIO buffer
        thumb_io = BytesIO()
        
        # Save thumbnail to buffer
        img.save(thumb_io, format='JPEG', quality=quality, optimize=True)
        thumb_io.seek(0)
        
        # Get the original filename and create thumbnail filename
        name, ext = os.path.splitext(os.path.basename(original_name))
        thumb_filename = f"{name}_thumb{ext if ext else '.jpg'}"
        
        # Create InMemoryUploadedFile
        thumbnail = InMemoryUploadedFile(
            thumb_io,
            None,
            thumb_filename,
            'image/jpeg',
            sys.getsizeof(thumb_io),
            None
        )
        
        return thumbnail
        
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        return None


def optimize_image(image_field, max_dimension=1920, quality=85):
    """
    Optimize an image by resizing if too large and compressing
    
    Args:
        image_field: Django ImageField instance
        max_dimension: Maximum width or height (maintains aspect ratio)
        quality: JPEG quality (1-100)
    
    Returns:
        InMemoryUploadedFile: Optimized image file or None if optimization fails
    """
    if not image_field:
        return None
    
    try:
        # Open the original image - handle file objects properly
        if hasattr(image_field, 'read'):
            # It's a file-like object (InMemoryUploadedFile, etc.)
            image_field.seek(0)  # Reset file pointer
            img = Image.open(image_field)
            original_name = image_field.name if hasattr(image_field, 'name') else 'image.jpg'
        elif hasattr(image_field, 'path'):
            # It's a Django ImageField with a path (already saved)
            img = Image.open(image_field.path)
            original_name = os.path.basename(image_field.name)
        else:
            # Try to open it directly
            img = Image.open(image_field)
            original_name = getattr(image_field, 'name', 'image.jpg')
        
        original_format = img.format
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image is larger than max_dimension
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a BytesIO buffer
        img_io = BytesIO()
        
        # Determine format
        save_format = 'JPEG' if original_format in ('JPEG', 'JPG') else 'JPEG'
        
        # Save optimized image
        img.save(img_io, format=save_format, quality=quality, optimize=True)
        img_io.seek(0)
        
        # Get original filename
        original_name = os.path.basename(original_name)
        
        # Create InMemoryUploadedFile
        optimized_image = InMemoryUploadedFile(
            img_io,
            None,
            original_name,
            f'image/{save_format.lower()}',
            sys.getsizeof(img_io),
            None
        )
        
        return optimized_image
        
    except Exception as e:
        print(f"Error optimizing image: {str(e)}")
        return None

