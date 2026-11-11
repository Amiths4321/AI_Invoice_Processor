
import ollama
import json

OLLAMA_HOST = "http://10.22.39.192:11434"
CHAT_MODEL = "qwen2.5vl:latest"

client = ollama.Client(host=OLLAMA_HOST)


def extract_invoice_data(invoice_text):

    prompt = f"""
    You are an expert invoice data extraction assistant.

    Extract invoice information from the supplied text.

    Return ONLY valid JSON.

    Use this exact JSON structure:

    {{
        "invoice_number": null,
        "invoice_date": null,
        "due_date": null,
        "vendor_name": null,
        "vendor_address": null,
        "gstin": null,
        "customer_name": null,
        "customer_address": null,
        "customer_gstin": null,
        "subtotal": null,
        "cgst": null,
        "sgst": null,
        "igst": null,
        "total_tax": null,
        "total_amount": null,
        "currency": "INR",
        "line_items": [
            {{
                "description": null,
                "quantity": null,
                "unit_price": null,
                "amount": null
            }}
        ]
    }}

    Rules:
    1. Do not invent missing information.
    2. Use null when a value is unavailable.
    3. Convert numeric amounts into numbers, not strings.
    4. Preserve invoice numbers and GSTINs accurately.
    5. Use YYYY-MM-DD for dates when unambiguous.
    6. Extract all available line items.
    7. Do not calculate missing values.
    8. Return JSON only.

    Invoice text:

    {invoice_text}
    """

    response = client.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    result = json.loads(response.message.content)

    return result
