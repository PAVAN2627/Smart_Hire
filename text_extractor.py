import fitz  # PyMuPDF

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            text += page_text.strip() + "\n"  # strip and add newline for clarity
    return text.strip()  # strip overall text to remove trailing spaces/newlines
