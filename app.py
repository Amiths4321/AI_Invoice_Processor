import streamlit as st
import fitz
from PIL import Image
from invoice_ai import extract_invoice_data

from invoice_extractor import (
    extract_pdf_text,
    extract_image_text
)

st.set_page_config(
    page_title="AI Invoice Processor",
    page_icon="📄",
    layout="wide"
)

st.title("AI Invoice Processing System")
st.write("Upload your invoice for AI-powered data extraction.")

uploaded_file = st.file_uploader(
    "Upload an invoice",
    type=["pdf", "png", "jpg", "jpeg"]
)

# Initialize session state for extracted text/data if not present
if "extracted_raw_text" not in st.session_state:
    st.session_state.extracted_raw_text = ""

if uploaded_file is not None:

    st.success("Invoice uploaded successfully!")

    file_name = uploaded_file.name
    file_type = uploaded_file.type

    st.write("**File name:**", file_name)
    st.write("**File type:**", file_type)

    if file_type == "application/pdf":
        pdf_document = fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        )
        st.write("**Total pages:**", len(pdf_document))
        pdf_document.close()
    else:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="Uploaded Invoice",
            use_container_width=True
        )

    # ---------------------------------
    # STEP 1: EXTRACT TEXT BUTTON
    # ---------------------------------
    if st.button("Extract Invoice Text"):
        with st.spinner("Extracting invoice text..."):
            if file_type == "application/pdf":
                pages = extract_pdf_text(uploaded_file)
                full_text = ""
                for page in pages:
                    st.subheader(f"Page {page['page_number']}")
                    st.text_area(
                        f"Extracted Text - Page {page['page_number']}",
                        page["text"],
                        height=250,
                        key=f"page_text_{page['page_number']}"
                    )
                    full_text += f"\n\n{page['text']}"
                st.session_state.extracted_raw_text = full_text
            else:
                extracted_text = extract_image_text(uploaded_file)
                st.subheader("Extracted Invoice Text")
                st.text_area(
                    "OCR Result",
                    extracted_text,
                    height=300,
                    key="image_ocr_text"
                )
                st.session_state.extracted_raw_text = extracted_text

    # ---------------------------------
    # STEP 2: EXTRACT STRUCTURED DATA BUTTON
    # ---------------------------------
    if st.button("Extract Invoice Data"):
        if not st.session_state.extracted_raw_text.strip():
            st.warning("Please extract the invoice text first using the button above.")
        else:
            with st.spinner("AI is extracting structured invoice data..."):
                invoice_data = extract_invoice_data(st.session_state.extracted_raw_text)

            st.subheader("Extracted Invoice Data")
            st.json(invoice_data)
            st.session_state["invoice_data"] = invoice_data