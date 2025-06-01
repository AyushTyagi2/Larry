import pytesseract
from PIL import Image
import tempfile
import os

# If tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def scan_text_from_image(image_path, output_file="extracted_text.txt"):
    try:
        # Create a custom temp directory
        with tempfile.TemporaryDirectory() as tempdir:
            os.environ['TMP'] = tempdir  # Redirect Tesseract temp folder

            # Open the image and extract text using Tesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            print("Extracted Text:\n", text)

            # Save the extracted text to the specified output file
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(text)
            print(f"Text successfully saved to {output_file}")

    except Exception as e:
        print("Failed to extract text:", e)
