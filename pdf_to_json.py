import PyPDF2
import os

def convert_pdf_to_text(pdf_path, output_path=None):
    """
    Convert a PDF file to text format.
    
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
            
            # Initialize a string to store all the text
            text_content = ""
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                # Get the page object
                page = pdf_reader.pages[page_num]
                
                # Extract text from the page
                text_content += page.extract_text()
                
                # Add a page separator if it's not the last page
                if page_num < len(pdf_reader.pages) - 1:
                    text_content += "\n\n--- Page {} ---\n\n".format(page_num + 1)
            
            # Write the extracted text to the output file
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text_content)
            
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