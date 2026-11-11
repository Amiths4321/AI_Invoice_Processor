
import fitz
from PIL import Image
import io
import ollama

OLLAMA_HOST = "http://10.22.39.192:11434"
CHAT_MODEL = "qwen2.5vl:latest"

client = ollama.Client(host=OLLAMA_HOST)


def extract_pdf_text(uploaded_file):

    pdf = fitz.open(
        stream=uploaded_file.getvalue(),
        filetype="pdf"
    )

    extracted_pages = []

    for page_number, page in enumerate(pdf):

        text = page.get_text().strip()

        # Use OCR if the PDF page has no selectable text
        if len(text) < 20:

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image_bytes = pix.tobytes("png")

            response = client.chat(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Extract all visible text from this "
                            "invoice image. Preserve the text "
                            "and numbers accurately."
                        ),
                        "images": [image_bytes]
                    }
                ]
            )

            text = response.message.content

        extracted_pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    return extracted_pages


def extract_image_text(uploaded_file):

    image = Image.open(uploaded_file).convert("RGB")

    image_buffer = io.BytesIO()

    image.save(image_buffer, format="PNG")

    response = client.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract all visible text from this invoice. "
                    "Preserve invoice numbers, dates, GSTINs, "
                    "amounts and line items accurately."
                ),
                "images": [image_buffer.getvalue()]
            }
        ]
    )

    return response.message.content
