import os
import pdfplumber
import pandas as pd
import re
from utils import clean_invoice_data

class InvoiceProcessor:
    def __init__(self,folder_path):
        self.folder_path = folder_path
        self.data = []

    def extract_tables_as_individual_dfs(self, file_path):
        """
        Extract tables from PDF file and return them as individual DataFrames.
        """
        individual_dfs = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    individual_dfs.append(df)
        # Return only first 2 tables as the required data is assumed to be in these
        return individual_dfs[:2]

    def extract_date_from_text(self, file_path):
        """
        Extract the date from the PDF, prioritizing date from table (if present), 
        and fallback to normal text extraction.
        """
        with pdfplumber.open(file_path) as pdf:
            # Check for tables in the first page with a "Date" column
            first_page = pdf.pages[0]
            tables = first_page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                if 'Date' in df.columns:
                    date_row = df[df['Date'].notna()]
                    if not date_row.empty:
                        # Extract the first non-empty value from 'Date'
                        return date_row['Date'].iloc[0].strip()  
            
            # If no date found in the tables, extracting using regex from parsed text
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    date_match = re.search(r'(Invoice\s*Date|Date)[:\s]*([A-Za-z]{3,9}\s\d{1,2},?\s\d{4}|(\d{1,2}\/\d{1,2}\/\d{4})|(\d{1,2}\.\s?[A-Za-z]{3,9}\s\d{4}))', text, re.IGNORECASE)
                    if date_match:
                        return date_match.group(2).strip()
        return None
        


    def extract_invoice_data(self, file_path):
        """
        Extract the relevant data from the tables and text.
        """
        # Getting the tables from pdf
        tables_dfs = self.extract_tables_as_individual_dfs(file_path)

        # Date extraction
        date = self.extract_date_from_text(file_path) 
        total = None
        gross_value = None

        for df in tables_dfs:
            if df.empty:
                continue

            # Prioritize Gross Amount
            if gross_value is None:
                gross_value = self.extract_table_value(df, "gross amount")
            
            # Extract Total if Gross Amount is not found
            if gross_value is None and total is None:
                total = self.extract_table_value(df, "total")
            
            # Break if amount is found
            if gross_value or total:
                break

        # Extract Total from text if not found in tables
        if total is None:
            total = self.extract_total_from_text(file_path)

        self.data.append({
            "File Name": os.path.basename(file_path),
            "Date": date,
            "Total": gross_value if gross_value else total,
        })
        

    def extract_table_value(self, df, search_term):
        """
        Extract a non-null value from the right-hand side of the row where the search term is found.
        Handles case insensitivity, partial matches, and allows search across all columns.
        """
        
        # Check if there is only one column
        if df.shape[1] < 2:
            return None

        try:
            # Iterate through each column to find rows containing the search term
            for col_index in range(df.shape[1]):
                value_row = df[df.iloc[:, col_index].astype(str).str.contains(search_term, na=False, case=False)]
                
                if not value_row.empty:
                    # Extract values from the columns to the right of the search term
                    for value in value_row.iloc[0, col_index + 1:]:
                        if pd.notnull(value):
                            return value.strip() if isinstance(value, str) else value
        except:
            # Skipping table due to unexpected data type in columns
            return None

        # No matches found for keyword in the table
        return None
    

    def extract_total_from_text(self, file_path):
        """
        Extract the total amount from the text in the PDF.
        Handles case insensitivity, various currency symbols, and flexible formats.
        """
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Define a regular expression for extracting the total amount
                    total_pattern = (
                        # Match total, optionally followed by : or -
                        r'(?:total|subtotal)\s*[:\-]?\s*'  
                        # Match currency symbol and amount
                        r'([€£¥₹$]?\s?[\d,]+(?:\.\d{2})?)'  
                    )
                    total_match = re.search(total_pattern, text, re.IGNORECASE)
                    if total_match:
                        # Clean and return the matched total amount
                        extracted_total = total_match.group(1).strip()
                        return extracted_total
        return None


    def create_output_files(self):
        """Create an Excel file with the extracted data."""
        if not self.data:
            print("No data available or unable to extract valid invoice data from the PDFs")
            return
        
        records= clean_invoice_data(self.data)
        
        df  = pd.DataFrame(records)
        # Convert 'Total' column to float
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
        
        # Output paths
        excel_path = os.path.join(self.folder_path, "Invoices.xlsx")
        csv_path   = os.path.join(self.folder_path, "Invoices.csv")
        df.rename(columns= {'Total': 'Total (EUR)'}, inplace=True)
        try:
            # Write Excel
            with pd.ExcelWriter(excel_path, engine="openpyxl", mode='w') as writer:
                # Sheet 1: Raw Data
                df.to_excel(writer, sheet_name="Sheet 1", index=False)
                

                # Sheet 2: Pivot Table
                pivot_df = pd.pivot_table(
                    df,
                    index="Date",
                    columns="File Name",
                    values="Total (EUR)",
                    aggfunc="sum",
                    fill_value=0,
                    margins=True,
                    margins_name="Total"
                )
                pivot_df.to_excel(writer, sheet_name="Sheet 2")

            # Write CSV (semicolon-separated)
            df.to_csv(csv_path, sep=";", index=False, mode='w')
        except:
            print("Please close the previously generated Excel or CSV file.")


    
    def generate_files(self):
        """Main function to extract data and generate Excel and CSV files."""
        pdf_files = [f for f in os.listdir(self.folder_path) if f.endswith('.pdf')]
        if not pdf_files:
            print("[WARNING] No PDF files found in the specified folder.")
            return

        # Process each PDF file
        for file_path in pdf_files:
            self.extract_invoice_data(file_path)
            print(f"Completed processing for: {file_path}")
        self.create_output_files()
        print("All PDF files have been processed! Excel and CSV files are ready.")


if __name__ == "__main__":
    folder_path = '.'  # Current directory
    processor = InvoiceProcessor(folder_path)
    processor.generate_files()
