"""
Word Document Generator for College Memory Book
Generates a .docx file in Arabic (RTL) with meetings, colleagues, and memories.
"""
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
import io
from django.conf import settings


def set_rtl_paragraph(paragraph):
    """Set RTL direction for a paragraph."""
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)

def add_rtl_paragraph(doc, text, font_size=12, bold=False, alignment=WD_ALIGN_PARAGRAPH.RIGHT):
    """Add a right-to-left paragraph with Arabic text."""
    paragraph = doc.add_paragraph()
    paragraph.alignment = alignment
    set_rtl_paragraph(paragraph)
    
    run = paragraph.add_run(text)
    run.font.size = Pt(font_size)
    run.font.name = 'Arial'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    if bold:
        run.bold = True
    return paragraph


def add_section_title(doc, title):
    """Add a section title with page break before."""
    # Add page break
    doc.add_page_break()
    # Add title
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_rtl_paragraph(paragraph)
    
    run = paragraph.add_run(title)
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.name = 'Arial'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    # Add spacing
    doc.add_paragraph()


def add_decorative_separator(doc):
    """Add a decorative horizontal separator between sections."""
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Create a table for the decorative bar
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.rows[0].cells[0]
    cell.width = Inches(6)
    
    # Set cell background color (light gray)
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'D3D3D3')
    cell._element.get_or_add_tcPr().append(shading_elm)
    
    # Set cell height
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), '120')  # Small height for separator
    trPr.append(trHeight)
    
    # Remove borders
    for cell in table.rows[0].cells:
        cell._element.get_or_add_tcPr().append(
            OxmlElement('w:tcBorders')
        )
    
    doc.add_paragraph()  # Add spacing after separator


def add_image_to_doc(doc, image_path, width_inches=3.0, height_inches=None):
    """Add an image to the document with proper sizing."""
    if not os.path.exists(image_path):
        return False
    
    try:
        # Open image to get dimensions
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # Calculate aspect ratio
        aspect_ratio = img_width / img_height
        
        # Set width and calculate height if not provided
        if height_inches is None:
            height_inches = width_inches / aspect_ratio
        
        # Ensure height doesn't exceed page height
        max_height = 7.0  # Maximum height in inches
        if height_inches > max_height:
            height_inches = max_height
            width_inches = height_inches * aspect_ratio
        
        # Add image
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(image_path, width=Inches(width_inches), height=Inches(height_inches))
        
        return True
    except Exception as e:
        print(f"Error adding image {image_path}: {e}")
        return False


def generate_memory_book_word():
    """
    Generate a Word document (.docx) for the College Memory Book.
    Order: Meetings (latest first) → Colleagues → Memories (by category)
    """
    from api.models import MeetingCategory, Colleague, MemoryCategory
    
    # Create document
    doc = Document()
    
    # Set default paragraph style to RTL for the document
    # Note: python-docx doesn't directly support document-level RTL
    # We'll set it per paragraph
    
    # ============================================
    # 1️⃣ اللقاءات (Meetings) - Latest First
    # ============================================
    add_section_title(doc, "اللقاءات")
    
    # Get all meeting categories ordered by year descending (latest first)
    meeting_categories = MeetingCategory.objects.prefetch_related('photos').all().order_by('-year', '-created_at')
    
    for meeting_category in meeting_categories:
        photos = meeting_category.photos.all()
        if not photos.exists():
            continue
        
        # Meeting title - In RTL mode, LEFT alignment positions text on RIGHT side
        paragraph = doc.add_paragraph()
        
        # Set RTL direction first
        set_rtl_paragraph(paragraph)
        
        # In RTL mode: LEFT alignment = text appears on RIGHT side of page
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Explicitly set justification to LEFT (which appears on right in RTL)
        pPr = paragraph._element.get_or_add_pPr()
        # Remove any existing jc element
        for elem in pPr:
            if elem.tag.endswith('}jc'):
                pPr.remove(elem)
        # Add LEFT justification (appears on right in RTL mode)
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'left')
        pPr.append(jc)
        
        run = paragraph.add_run(meeting_category.name)
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.name = 'Arial'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        
        # Meeting description if exists
        if meeting_category.description:
            add_rtl_paragraph(doc, meeting_category.description, font_size=12)
        
        doc.add_paragraph()  # Spacing
        
        # Add photos in a grid (2 per row)
        photos_list = list(photos)
        for i in range(0, len(photos_list), 2):
            # Create table for 2 images side by side
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            
            for j, photo in enumerate(photos_list[i:i+2]):
                cell = table.rows[0].cells[j]
                cell.width = Inches(3.0)
                
                # Add image to cell
                if photo.image and os.path.exists(photo.image.path):
                    paragraph = cell.paragraphs[0]
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = paragraph.add_run()
                    try:
                        run.add_picture(photo.image.path, width=Inches(2.8))
                    except Exception as e:
                        print(f"Error adding meeting photo: {e}")
                
                # Add description if exists
                if photo.description_ar:
                    desc_para = cell.add_paragraph()
                    desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    desc_run = desc_para.add_run(photo.description_ar)
                    desc_run.font.size = Pt(10)
                    desc_run.font.name = 'Arial'
                    desc_run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
            
            doc.add_paragraph()  # Spacing after row
        
        # Add spacing between meetings
        doc.add_paragraph()
        add_decorative_separator(doc)
    
    # ============================================
    # 2️⃣ الزملاء (Colleagues)
    # ============================================
    add_section_title(doc, "الزملاء")
    
    # Get all colleagues with photos
    colleagues = Colleague.objects.prefetch_related('archive_photos').all().order_by('name')
    
    for colleague in colleagues:
        # Check if colleague has any photos
        has_photo_1973 = colleague.photo_1973 and os.path.exists(colleague.photo_1973.path)
        has_latest_photo = colleague.latest_photo and os.path.exists(colleague.latest_photo.path)
        archive_photos = list(colleague.archive_photos.all())
        
        # Skip if no photos at all
        if not has_photo_1973 and not has_latest_photo and not archive_photos:
            continue
        
        # Colleague name
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_rtl_paragraph(paragraph)
        run = paragraph.add_run(colleague.name)
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.name = 'Arial'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        
        # Two images side-by-side at top: صورة 73 and الصورة الأخيرة
        if has_photo_1973 or has_latest_photo:
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            
            # صورة 73
            cell1 = table.rows[0].cells[0]
            cell1.width = Inches(3.0)
            para1 = cell1.paragraphs[0]
            para1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_rtl_paragraph(para1)
            label1 = para1.add_run("صورة 73")
            label1.font.size = Pt(12)
            label1.font.bold = True
            label1.font.name = 'Arial'
            label1._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
            
            if has_photo_1973:
                para1_img = cell1.add_paragraph()
                para1_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run1_img = para1_img.add_run()
                try:
                    run1_img.add_picture(colleague.photo_1973.path, width=Inches(2.5))
                except Exception as e:
                    print(f"Error adding photo_1973: {e}")
            
            # الصورة الأخيرة
            cell2 = table.rows[0].cells[1]
            cell2.width = Inches(3.0)
            para2 = cell2.paragraphs[0]
            para2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_rtl_paragraph(para2)
            label2 = para2.add_run("الصورة الأخيرة")
            label2.font.size = Pt(12)
            label2.font.bold = True
            label2.font.name = 'Arial'
            label2._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
            
            if has_latest_photo:
                para2_img = cell2.add_paragraph()
                para2_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run2_img = para2_img.add_run()
                try:
                    run2_img.add_picture(colleague.latest_photo.path, width=Inches(2.5))
                except Exception as e:
                    print(f"Error adding latest_photo: {e}")
            
            doc.add_paragraph()  # Spacing
        
        # Additional archive photos (max 2 per row, larger size)
        if archive_photos:
            for i in range(0, len(archive_photos), 2):
                table = doc.add_table(rows=1, cols=2)
                table.style = 'Table Grid'
                
                for j, archive_photo in enumerate(archive_photos[i:i+2]):
                    cell = table.rows[0].cells[j]
                    cell.width = Inches(3.5)
                    
                    if archive_photo.image and os.path.exists(archive_photo.image.path):
                        paragraph = cell.paragraphs[0]
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        run = paragraph.add_run()
                        try:
                            run.add_picture(archive_photo.image.path, width=Inches(3.2))
                        except Exception as e:
                            print(f"Error adding archive photo: {e}")
                
                doc.add_paragraph()  # Spacing after row
        
        # Add decorative separator between colleagues
        doc.add_paragraph()
        add_decorative_separator(doc)
    
    # ============================================
    # 3️⃣ الذكريات (Memories) - By Category
    # ============================================
    add_section_title(doc, "الذكريات")
    
    # Get all memory categories ordered by year descending (latest first)
    memory_categories = MemoryCategory.objects.prefetch_related('photos').all().order_by('-year', 'name')
    
    for memory_category in memory_categories:
        photos = memory_category.photos.all()
        if not photos.exists():
            continue
        
        # Category title with page break before
        doc.add_page_break()
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_rtl_paragraph(paragraph)
        run = paragraph.add_run(memory_category.name)
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.name = 'Arial'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        
        # Category description if exists
        if memory_category.description:
            add_rtl_paragraph(doc, memory_category.description, font_size=12)
        
        doc.add_paragraph()  # Spacing
        
        # Add photos in a grid (2 per row)
        photos_list = list(photos)
        for i in range(0, len(photos_list), 2):
            # Create table for 2 images side by side
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            
            for j, photo in enumerate(photos_list[i:i+2]):
                cell = table.rows[0].cells[j]
                cell.width = Inches(3.0)
                
                # Add image to cell
                if photo.image and os.path.exists(photo.image.path):
                    paragraph = cell.paragraphs[0]
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = paragraph.add_run()
                    try:
                        run.add_picture(photo.image.path, width=Inches(2.8))
                    except Exception as e:
                        print(f"Error adding memory photo: {e}")
                
                # Add description if exists
                if photo.description_ar:
                    desc_para = cell.add_paragraph()
                    desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    desc_run = desc_para.add_run(photo.description_ar)
                    desc_run.font.size = Pt(10)
                    desc_run.font.name = 'Arial'
                    desc_run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
            
            doc.add_paragraph()  # Spacing after row
        
        # Add spacing between categories
        doc.add_paragraph()
        add_decorative_separator(doc)
    
    return doc

