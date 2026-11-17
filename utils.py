import pypdf
import io

def extract_text_from_file(uploaded_file):
    """根据文件类型提取文本"""
    # 1. 如果是 txt 
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    # 2.如果是 pdf
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader=pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    return "" # 如果都不是,返回空 
