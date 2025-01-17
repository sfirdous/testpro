import os
import PyPDF2
from groq import Groq
from typing import List, Tuple

class DocumentProcessor:
    def __init__(self):
        """
        Initialize the DocumentProcessor with necessary configurations.
        Checks for Groq API key in environment variables.
        """
        # Check for API key
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("Please set the GROQ_API_KEY environment variable")
        
        # Initialize Groq client
        self.client = Groq()
    
    def extract_lines_with_positions(self, page) -> List[Tuple[str, float]]:
        """
        Extract text from a PDF page while preserving vertical positions of text elements.
        
        Args:
            page: PyPDF2 page object
            
        Returns:
            List of tuples containing (text, y_position)
        """
        text_elements = []
        def visitor_body(text, cm, tm, fontDict, fontSize):
            if text.strip():
                # Extract the y-position from the text matrix
                y_position = tm[5] if tm else 0
                text_elements.append((text.strip(), y_position))
        
        page.extract_text(visitor_text=visitor_body)
        return text_elements

    def convert_pdf_to_text(self, pdf_path: str, temp_text_path: str = None) -> str:
        """
        Convert PDF file to text while preserving line breaks and structure.
        
        Args:
            pdf_path (str): Path to the input PDF file
            temp_text_path (str, optional): Path for temporary text file
            
        Returns:
            str: Path to the created text file
        """
        # Generate temporary text file path if not provided
        if temp_text_path is None:
            temp_text_path = os.path.splitext(pdf_path)[0] + '_temp.txt'
        
        try:
            print(f"Converting PDF: {pdf_path}")
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                all_pages_text = []
                
                for page_num in range(len(pdf_reader.pages)):
                    print(f"Processing page {page_num + 1}/{len(pdf_reader.pages)}")
                    page = pdf_reader.pages[page_num]
                    
                    # Get text elements with their positions
                    text_elements = self.extract_lines_with_positions(page)
                    
                    # Sort elements by y-position (top to bottom)
                    text_elements.sort(key=lambda x: -x[1])
                    
                    # Group elements with similar y-positions
                    threshold = 1
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
                
                # Write the final text to the temporary file
                with open(temp_text_path, 'w', encoding='utf-8') as text_file:
                    text_file.write('\n'.join(all_pages_text))
                
                return temp_text_path
                
        except Exception as e:
            raise Exception(f"Error converting PDF to text: {str(e)}")

    def process_text_with_groq(self, text_content: str, output_json_path: str):
        """
        Process text content using Groq's LLaMA 3.2 model and save as JSON.
        
        Args:
            text_content (str): The text content to be converted to JSON
            output_json_path (str): Path where the JSON output should be saved
        """
        try:
            print("Processing text with Groq API...")
            completion = self.client.chat.completions.create(
                model="llama-3.2-1b-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Convert the following text content to a well-structured JSON format. Create appropriate keys and organize the content logically. Ensure the output is valid JSON."
                    },
                    {
                        "role": "user",
                        "content": text_content
                    },
                    {
                        "role": "assistant",
                        "content": "I will convert this text to JSON format, organizing it in a logical structure."
                    },
                    {
                        "role": "assistant",
                        "content": ""
                    }
                ],
                temperature=0.2,
                max_tokens=1024,  # Changed from max_completion_tokens to max_tokens
                top_p=1,
                stream=True
            )
            
            print(f"Saving JSON output to {output_json_path}")
            with open(output_json_path, 'w', encoding='utf-8') as json_file:
                for chunk in completion:
                    content = chunk.choices[0].delta.content or ""
                    json_file.write(content)
                    print(content, end="", flush=True)
                    
            print("\nJSON conversion complete!")
            
        except Exception as e:
            raise Exception(f"Error processing with Groq API: {str(e)}")

    def convert_pdf_to_json(self, pdf_path: str, output_json_path: str, keep_text_file: bool = False):
        """
        Complete pipeline to convert PDF to JSON via text.
        
        Args:
            pdf_path (str): Path to input PDF file
            output_json_path (str): Path for final JSON output
            keep_text_file (bool): Whether to keep the intermediate text file
        """
        try:
            # Step 1: Convert PDF to text
            temp_text_path = self.convert_pdf_to_text(pdf_path)
            print(f"PDF successfully converted to text: {temp_text_path}")
            
            # Step 2: Read the text content
            with open(temp_text_path, 'r', encoding='utf-8') as text_file:
                text_content = text_file.read()
            
            # Step 3: Process text with Groq and save JSON
            self.process_text_with_groq(text_content, output_json_path)
            
            # Clean up temporary text file if not keeping it
            if not keep_text_file and os.path.exists(temp_text_path):
                os.remove(temp_text_path)
                print("Temporary text file removed")
            
            print(f"Conversion complete! JSON file saved to: {output_json_path}")
            
        except Exception as e:
            print(f"Error in conversion pipeline: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the processor
        processor = DocumentProcessor()
        
        # Convert PDF to JSON
        processor.convert_pdf_to_json(
            pdf_path="ProjectTest/bankstatment.pdf",  # Replace with your PDF file path
            output_json_path="ProjectTest/llama-3.2_1b/output.json",  # Replace with desired output path
            keep_text_file=True  # Set to False if you don't want to keep the intermediate text file
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")