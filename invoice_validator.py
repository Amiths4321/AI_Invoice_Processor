
import re
from datetime import date


def validate_invoice(invoice):

    errors = []
    warnings = []

    # 1. Check mandatory fields
    required_fields = [
        "invoice_number",
        "invoice_date",
        "vendor_name",
        "total_amount"
    ]

    for field in required_fields:

        if invoice.get(field) is None or invoice.get(field) == "":
            errors.append(f"Missing required field: {field}")

    # 2. Validate GSTIN format
    gstin = invoice.get("gstin")

    if gstin:

        gstin_pattern = (
            r"^[0-9]{2}[A-Z]{5}[0-9]{4}"
            r"[A-Z][1-9A-Z]Z[0-9A-Z]$"
        )

        if not re.match(gstin_pattern, str(gstin)):
            errors.append("Invalid GSTIN format.")

    # 3. Validate invoice date
    invoice_date = invoice.get("invoice_date")

    if invoice_date:

        try:
            parsed_date = date.fromisoformat(invoice_date)

            if parsed_date > date.today():
                warnings.append("Invoice date is in the future.")

        except (ValueError, TypeError):
            errors.append("Invalid invoice date. Expected YYYY-MM-DD.")

    # 4. Validate numeric fields
    numeric_fields = [
        "subtotal",
        "cgst",
        "sgst",
        "igst",
        "total_tax",
        "total_amount"
    ]

    for field in numeric_fields:

        value = invoice.get(field)

        if value is not None:

            if isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                errors.append(f"{field} must be numeric.")

    # 5. Check tax calculation
    subtotal = invoice.get("subtotal")
    cgst = invoice.get("cgst")
    sgst = invoice.get("sgst")
    igst = invoice.get("igst")
    total_tax = invoice.get("total_tax")
    total_amount = invoice.get("total_amount")

    tax_values = [cgst, sgst, igst]

    if all(isinstance(v, (int, float)) and not isinstance(v, bool)
           for v in tax_values):

        calculated_tax = sum(tax_values)

        if total_tax is not None and isinstance(total_tax, (int, float)):

            if abs(calculated_tax - total_tax) > 0.02:
                errors.append("Tax total does not match CGST + SGST + IGST.")

        if isinstance(subtotal, (int, float)) and isinstance(
            total_amount, (int, float)
        ):

            calculated_total = subtotal + calculated_tax

            if abs(calculated_total - total_amount) > 0.02:
                errors.append("Grand total does not match subtotal + tax.")

    # 6. Return validation result
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
