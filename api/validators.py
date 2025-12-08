"""
Custom validators for API models and views
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image

# Optional import for python-magic (requires system library on Windows)
try:
    import magic
    HAS_MAGIC = True
except (ImportError, OSError):
    HAS_MAGIC = False


def validate_image_size(image):
    """
    Validate image file size
    Maximum size: 100MB
    """
    max_size = 100 * 1024 * 1024  # 100MB
    if image.size > max_size:
        raise ValidationError(
            f'Image size cannot exceed 100MB. Current size: {image.size / (1024*1024):.2f}MB'
        )


def validate_image_dimensions(image):
    """
    Validate image dimensions to prevent memory exhaustion
    Maximum dimensions: 10000x10000 pixels
    """
    max_width = 10000
    max_height = 10000
    
    try:
        img = Image.open(image)
        width, height = img.size
        
        if width > max_width or height > max_height:
            raise ValidationError(
                f'Image dimensions too large. Max: {max_width}x{max_height}px, '
                f'Got: {width}x{height}px'
            )
    except IOError as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def validate_image_content_type(file):
    """
    Validate that the file is actually an image by checking its MIME type
    Uses python-magic for robust detection (if available)
    """
    allowed_types = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp'
    ]
    
    # Use python-magic if available (Linux/production)
    if HAS_MAGIC:
        try:
            # Read first 2048 bytes for magic detection
            file.seek(0)
            file_header = file.read(2048)
            file.seek(0)
            
            # Detect MIME type
            mime = magic.from_buffer(file_header, mime=True)
            
            if mime not in allowed_types:
                raise ValidationError(
                    f'Invalid image type: {mime}. Allowed types: {", ".join(allowed_types)}'
                )
            return
        except Exception:
            pass  # Fall through to extension check
    
    # Fallback validation using file extension (works on all platforms)
    if not hasattr(file, 'name'):
        raise ValidationError('Invalid file upload')
    
    ext = file.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise ValidationError(f'Invalid file extension: .{ext}')


# Composite validator for images
def validate_uploaded_image(image):
    """
    Combined validator for uploaded images
    Checks: size, dimensions, and content type
    """
    validate_image_size(image)
    validate_image_dimensions(image)
    validate_image_content_type(image)


# Extension validator (used in model fields)
image_extension_validator = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
)

