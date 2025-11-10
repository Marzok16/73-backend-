#!/usr/bin/env python3
"""
Diagnostic script to test WeasyPrint installation and dependencies
Run this on the server: python test_weasyprint.py
"""

import sys
import os

def test_weasyprint():
    print("=" * 70)
    print("WeasyPrint Installation Test")
    print("=" * 70)
    
    # Test 1: Check Python version
    print("\n1. Python Version:")
    print(f"   {sys.version}")
    
    # Test 2: Try importing WeasyPrint
    print("\n2. Importing WeasyPrint:")
    try:
        import weasyprint
        print(f"   ✓ WeasyPrint imported successfully")
        print(f"   Version: {weasyprint.__version__}")
    except ImportError as e:
        print(f"   ✗ Failed to import WeasyPrint: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error importing WeasyPrint: {e}")
        print(f"   This usually means system libraries are missing")
        return False
    
    # Test 3: Check system libraries
    print("\n3. System Libraries:")
    try:
        from weasyprint.text.ffi import ffi, pango
        print("   ✓ Pango loaded successfully")
    except Exception as e:
        print(f"   ✗ Pango failed to load: {e}")
        print("\n   Install missing libraries:")
        print("   sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0")
        return False
    
    try:
        from weasyprint.text.ffi import pangocairo
        print("   ✓ PangoCairo loaded successfully")
    except Exception as e:
        print(f"   ✗ PangoCairo failed to load: {e}")
        print("\n   Install missing libraries:")
        print("   sudo apt-get install -y libpangocairo-1.0-0")
        return False
    
    # Test 4: Simple HTML to PDF conversion
    print("\n4. PDF Generation Test:")
    try:
        from weasyprint import HTML, CSS
        html_string = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: DejaVu Sans; direction: rtl; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>مرحباً بك - Test PDF</h1>
            <p>This is a test PDF document with Arabic text: اختبار النص العربي</p>
        </body>
        </html>
        """
        
        pdf_bytes = HTML(string=html_string).write_pdf()
        print(f"   ✓ PDF generated successfully ({len(pdf_bytes)} bytes)")
        
        # Save test PDF
        with open('/tmp/weasyprint_test.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("   ✓ Test PDF saved to /tmp/weasyprint_test.pdf")
        
    except Exception as e:
        print(f"   ✗ PDF generation failed: {e}")
        import traceback
        print("\n   Full error:")
        print(traceback.format_exc())
        return False
    
    # Test 5: Check LD_LIBRARY_PATH
    print("\n5. Environment Variables:")
    print(f"   PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
    print(f"   LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')}")
    
    print("\n" + "=" * 70)
    print("✓ All tests passed! WeasyPrint is working correctly.")
    print("=" * 70)
    return True

if __name__ == '__main__':
    try:
        success = test_weasyprint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
