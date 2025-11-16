
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar


def text_extraction(element):
    # Extracting the text from the in line text element
    line_text = element.get_text()
    
    # Find the formats of the text
    # Initialize the list with all the formats appeared in the line of text
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Iterating through each character in the line of text
            for character in text_line:
                if isinstance(character, LTChar):
                    # Append the font name of the character
                    line_formats.append(character.fontname)
                    # Append the font size of the character
                    line_formats.append(character.size)
    # Find the unique font sizes and names in the line
    format_per_line = list(set(line_formats))
    
    # Return a tuple with the text in each line along with its format
    return (line_text, format_per_line)


def extract_full_text(pdf_path: str) -> str:
    # Create the dictionary to extract text from each image
    text_per_page = []
    # Create a boolean variable for image detection

    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):

        # Initialize the variables needed for the text extraction from the page
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []


        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the element as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the element of the page layout
            element = component[1]


            # Check if the element is text element
            if isinstance(element, LTTextContainer):
                # Use the function to extract the text and format for each text element
                (line_text, format_per_line) = text_extraction(element)
                # Append the text of each line to the page text
                page_text.append(line_text)
                # Append the format for each line containing text
                line_format.append(format_per_line)
                page_content.append(line_text)

        # Create the key of the dictionary
        dctkey = 'Page_'+str(pagenum)
        # Add the list of list as value of the page key
        text_per_page.append([page_text, line_format, text_from_images,text_from_tables, page_content])

    text_chunks = []
    for page_text in text_per_page:
        text_chunks.append(''.join(page_text[4]))
    
    return '\n'.join(text_chunks)
