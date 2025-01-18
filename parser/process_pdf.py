import cv2
import numpy as np
import pdfplumber
from pdf2image import convert_from_path
import img2pdf
from PIL import Image
import io
import os

def extend_horizontal_lines(image, kernel_size=1, threshold=50):
    """
    Extends detected horizontal lines across the full width of the image.
    :param image: input image as a numpy array (BGR)
    :param kernel_size: width of the horizontal structuring element for dilation
    :param threshold: threshold value for binarization
    :return: processed image (grayscale, with extended lines)
    """
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply binary inversion thresholding: lines become white on black
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    # Create a horizontal kernel - a wide, 1-pixel-high rectangle
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, 1))
    # Dilate to connect and extend horizontal lines
    dilated = cv2.dilate(binary, horizontal_kernel, iterations=1)
    # Invert the result so that the lines are dark again on a light background
    result_img = cv2.bitwise_not(dilated)
    return result_img

def process_pdf_page_to_pdf(pdf_path, output_pdf, page_number=0):
    """
    Converts a PDF page to an image, extends horizontal lines,
    then converts the processed image back into a PDF.
    :param pdf_path: path to the input PDF file
    :param output_pdf: path to save the processed PDF
    :param page_number: which page of the PDF to process (0-indexed)
    :return: None
    """
    # Convert PDF to images (using 300 dpi)
    pages = convert_from_path(pdf_path, dpi=300)
    if page_number >= len(pages):
        raise ValueError("Page number out of range.")
    
    # Get the selected page as a PIL Image and convert to OpenCV (BGR format)
    pil_image = pages[page_number]
    open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    # Process the image to extend horizontal lines
    processed_image = extend_horizontal_lines(open_cv_image)
    
    # Convert the processed image (which is grayscale) back to a PIL image
    pil_processed = Image.fromarray(processed_image)
    
    # Save the processed image temporarily as a PNG in memory
    temp_image_path = "temp_processed.png"
    pil_processed.save(temp_image_path)
    
    # Convert the PNG image to a PDF using img2pdf
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(temp_image_path))
    
    # Clean up temporary image file
    #os.remove(temp_image_path)
    print(f"Processed PDF saved as '{output_pdf}'.")
