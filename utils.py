from datetime import datetime
import re

def extract_amount_and_currency(total_str):
    """
    Extract numeric value and currency from a string using regex.
    """
    
    match = re.search(r"([\d.,]+)", total_str)
    if match:
        amount_str = match.group()
        # Handle European decimal formats
        amount = float(amount_str.replace(",", ".") if ',' in amount_str else amount_str)
        currency = "EUR"
        if "$" in total_str or "USD" in total_str:
            currency = "USD"
        elif "£" in total_str or "GBP" in total_str:
            currency = "GBP"
    

        return amount, currency
    else:
        return None, None

def clean_invoice_data(invoice_data):
    """
    Clean invoice data by normalizing the date format to DD/MM/YYYY and converting totals to Euros.
    """
    month_mapping = {
        "Januar": "January", "Februar": "February", "März": "March", "April": "April",
        "Mai": "May", "Juni": "June", "Juli": "July", "August": "August", "September": "September",
        "Oktober": "October", "November": "November", "Dezember": "December"
    }

    cleaned_data = []

    for invoice in invoice_data:
        # Normalize Date
        try:
            raw_date = invoice["Date"]
            for de_month, en_month in month_mapping.items():
                raw_date = re.sub(rf"\b{de_month}\b", en_month, raw_date)

            parsed_date = None
            date_formats = [
                "%d. %B %Y",    # 01. März 2024
                "%b %d, %Y",    # Mar 01, 2024
                "%d/%m/%Y",     # 01/03/2024
                "%Y-%m-%d",     # 2024-03-01
                "%m/%d/%Y",     # 03/01/2024
                "%B %d, %Y",    # January 25, 2016
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(raw_date, fmt)
                    break
                except ValueError:
                    continue

            if not parsed_date:
                raise ValueError(f"Date format not recognized: {invoice['Date']}")
            invoice["Date"] = parsed_date.strftime("%d/%m/%Y")
        except Exception as e:
            invoice["Date"] = "Invalid date"

        # Convert to a common currency (EUR)
        try:
            amount, currency = extract_amount_and_currency(invoice["Total"])
            # Convert currency to EUR (Used exchange rates at the time of writing the code)
            if currency and currency == "USD":
                total_in_euro = float(amount) * 0.97
            elif currency and currency == "GBP":
                total_in_euro = float(amount) * 1.20
            else:
                total_in_euro = float(amount)

            invoice["Total"] = float(f"{total_in_euro:.2f}")
        except Exception as e:
            invoice["Total"] = 0.00

        cleaned_data.append(invoice)

    return cleaned_data


