"""
Dependencies:
    1. Tesseract (https://github.com/tesseract-ocr/tesseract)
        - ensure it is available in the system's path
    2. poppler (https://poppler.freedesktop.org/)
        - ensure it is available in the system's path
    2. pip install unstructured
    3. pip install unstructured[pdf,ocr]
"""


from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Text, Table


def extract_text(pdf_path: str, out_path: str, strategy: str = "auto", infer_table: bool = True) -> bool:
    """Extracts text from the given PDF file via `pdf_path` using Unstructured. Extracted text is sent to a file that is either
    created (or overwritten) as specified by `out_path`. Behavior of the text extraction can be controlled by `strategy`
    and `infer_table`.

    Args:
        pdf_path: a str representing the path to the PDF file (.pdf)
        out_path: a str representing the path to the output file (.txt)
        strategy: what text extraction method to use: `auto` for automatically choosing between fast and hi_res depending on the page's content (faster); `hi_res` to understand page layout and use OCR (slower)
        infer_table: whether to infer tables, only has an effect if current strategy is `hi_res`

    Returns:
        bool: whether the operation succeeded or not
    """
    try:
        # first get all elements in the pdf
        elements = partition_pdf(pdf_path, strategy=strategy, infer_table_structure=infer_table)
        print("done")
        # then collect the relevant text from each element
        with open(out_path, "w", encoding="utf-8") as out_file:
            for elem in elements:
                extract_text = ""
                # for tables, append their html format to preserve table structure
                if isinstance(elem, Table):
                    extract_text = elem.metadata.text_as_html or ""
                # for general text, treat normally
                elif isinstance(elem, Text):
                    extract_text = elem.text
                # write extracted text from current elem to out file
                if extract_text:
                    # filter out characters that can't be encoded in UTF-8
                    cleaned_text = extract_text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
                    out_file.write(f"{cleaned_text}\n\n")
        return True  
    except Exception as e:
        print(e)
        return False
    