import PyPDF2
import os
from typing import List, Tuple

def extract_lines_with_positions(page) -> List[Tuple[str, float]]:
    """
    Extract text from a page while preserving vertical positions of text elements.
    
    Args:
        page: PyPDF2 page object
        
    Returns:
        List of tuples containing (text, y_position)
    """
    # Extract text and layout information
    text_elements = []
    def visitor_body(text, cm, tm, fontDict, fontSize):
        if text.strip():
            # Extract the y-position from the text matrix (tm)
            y_position = tm[5] if tm else 0
            text_elements.append((text.strip(), y_position))
    
    page.extract_text(visitor_text=visitor_body)
    return text_elements

def convert_pdf_to_text(pdf_path: str, output_path: str = None) -> str:
    """
    Convert a PDF file to text format while preserving line breaks.
    
    Args:
        pdf_path (str): Path to the input PDF file
        output_path (str, optional): Path for the output text file.
                                   If not provided, uses the same name as PDF with .txt extension
    
    Returns:
        str: Path to the created text file
    
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        PyPDF2.PdfReadError: If there's an error reading the PDF
    """
    # Validate input file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + '.txt'
    
    try:
        # Open the PDF file in binary read mode
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Process each page
            all_pages_text = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # Get text elements with their positions
                text_elements = extract_lines_with_positions(page)
                
                # Sort elements by y-position in descending order (top to bottom)
                text_elements.sort(key=lambda x: -x[1])
                
                # Group elements with similar y-positions (within a small threshold)
                threshold = 1  # Adjust this value based on your needs
                current_line = []
                current_y = None
                lines = []
                
                for text, y_pos in text_elements:
                    if current_y is None:
                        current_y = y_pos
                        
                    if abs(y_pos - current_y) <= threshold:
                        current_line.append(text)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [text]
                        current_y = y_pos
                
                # Add the last line
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Join lines with newline characters
                page_text = '\n'.join(lines)
                
                # Add page separator
                if page_num < len(pdf_reader.pages) - 1:
                    page_text += "\n\n--- Page {} ---\n\n".format(page_num + 1)
                
                all_pages_text.append(page_text)
            
            # Write the final text to the output file
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write('\n'.join(all_pages_text))
            
            return output_path
            
    except PyPDF2.PdfReadError as e:
        raise PyPDF2.PdfReadError(f"Error reading PDF file: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Convert PDF to text
        output_file = convert_pdf_to_text("bankstatment.pdf")
        print(f"Text file created successfully: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")