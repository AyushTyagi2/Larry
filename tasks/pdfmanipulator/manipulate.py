# tasks/documents/pdf_tools.py
import os
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import io

def merge_pdfs(input_files, output_file):
    """Merge multiple PDF files into one"""
    if not input_files:
        print("No input files provided")
        return False
    
    try:
        pdf_merger = PyPDF2.PdfMerger()
        
        # Add each PDF to the merger
        for pdf_file in input_files:
            if os.path.exists(pdf_file) and pdf_file.lower().endswith('.pdf'):
                pdf_merger.append(pdf_file)
            else:
                print(f"Warning: File not found or not a PDF: {pdf_file}")
        
        # Write the merged PDF to the output file
        pdf_merger.write(output_file)
        pdf_merger.close()
        
        print(f"Successfully merged {len(input_files)} PDFs into {output_file}")
        return True
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return False

def extract_pdf_pages(input_file, page_range, output_file):
    """Extract specific pages from a PDF file"""
    if not os.path.exists(input_file) or not input_file.lower().endswith('.pdf'):
        print(f"Input file not found or not a PDF: {input_file}")
        return False
    
    try:
        # Parse page range format like "1-3,5,7-9"
        pages_to_extract = []
        ranges = page_range.split(',')
        
        for r in ranges:
            if '-' in r:
                start, end = map(int, r.split('-'))
                pages_to_extract.extend(range(start, end + 1))
            else:
                pages_to_extract.append(int(r))
        
        # Adjust for 0-based indexing
        zero_based_pages = [p - 1 for p in pages_to_extract]
        
        # Extract pages
        pdf_writer = PyPDF2.PdfWriter()
        
        with open(input_file, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            
            for page_num in zero_based_pages:
                if 0 <= page_num < total_pages:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                else:
                    print(f"Warning: Page {page_num + 1} is out of range")
        
        # Write extracted pages to output file
        with open(output_file, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        print(f"Successfully extracted {len(zero_based_pages)} pages to {output_file}")
        return True
    except Exception as e:
        print(f"Error extracting PDF pages: {e}")
        return False

def rotate_pdf_pages(input_file, rotation_angle, output_file):
    """Rotate all pages in a PDF file"""
    if not os.path.exists(input_file) or not input_file.lower().endswith('.pdf'):
        print(f"Input file not found or not a PDF: {input_file}")
        return False
    
    try:
        # Validate rotation angle
        rotation = int(rotation_angle)
        if rotation not in [90, 180, 270]:
            print("Rotation angle must be 90, 180, or 270 degrees")
            return False
        
        # Rotate pages
        pdf_writer = PyPDF2.PdfWriter()
        
        with open(input_file, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page in pdf_reader.pages:
                page.rotate(rotation)
                pdf_writer.add_page(page)
        
        # Write rotated PDF to output file
        with open(output_file, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        print(f"Successfully rotated PDF pages by {rotation} degrees")
        return True
    except Exception as e:
        print(f"Error rotating PDF pages: {e}")
        return False

def create_pdf_from_text(text_content, output_file):
    """Create a simple PDF from text content"""
    try:
        # Create a new PDF with Reportlab
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        
        # Set up text parameters
        y_position = height - 50
        line_height = 14
        margin = 50
        max_width = width - 2 * margin
        
        # Split text into lines and add to PDF
        paragraphs = text_content.split('\n\n')
        
        for paragraph in paragraphs:
            lines = paragraph.split('\n')
            for line in lines:
                # Add text to PDF
                c.drawString(margin, y_position, line)
                y_position -= line_height
            
            # Extra space between paragraphs
            y_position -= line_height
            
            # Check if we need a new page
            if y_position < margin:
                c.showPage()
                y_position = height - 50
        
        c.save()
        print(f"PDF created successfully: {output_file}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def extract_text_from_pdf(input_file):
    """Extract text content from a PDF file"""
    if not os.path.exists(input_file) or not input_file.lower().endswith('.pdf'):
        print(f"Input file not found or not a PDF: {input_file}")
        return None
    
    try:
        text_content = ""
        
        with open(input_file, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n\n"
        
        if not text_content.strip():
            print("No text content could be extracted (the PDF might be scanned images)")
            return None
        
        print(f"Successfully extracted text from PDF")
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None