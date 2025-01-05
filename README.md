# Data extractor for PDF invoices

InvoiceData Extractor is a tool for extracting  invoice date and total amount from PDFs. The application then generates an Excel file and a CSV file for further analysis and reporting. The tool also supports handling various currencies and date formats.

### Brief Overview of the Tool

1. **PDF Input**:  
   - The tool reads all invoice PDFs in the base folder.

2. **Data Extraction**:  
   - Extracts the invoice date and total amount, handling both tables and fallback text extraction.

3. **Data Cleaning and Conversion**:  
   - Normalizes the date format to `DD/MM/YYYY` and converts amounts to Euros if required.

4. **File Generation**:  
   - **Excel Output**: Creates an `Invoices.xlsx`.
   - **CSV Output**: Creates a `Invoices.csv` in semicolon-separated format for analysis.

5. **Output**:  
   - Both Excel and CSV files are stored in the same folder as the input PDFs.


### Outputs from the Code

The tool generates the following files:

1. **Invoices.xlsx**:
   - **Sheet 1: Raw Data**: Contains columns for:
     - **File Name**: Name of the PDF file.
     - **Date**: Extracted date in `DD/MM/YYYY` format.
     - **Total (EUR)**: Total amount in EUR after conversion.
   - **Sheet 2: Pivot Table**: A summary table aggregating total amounts by date and file name.

2. **Invoices.csv**:
   - Contains the same data as **Sheet 1** in the Excel file but formatted with semicolon separators (`;`).


### Steps to Run

1. Place the PDF files and the executable in the same folder.
2. Double-click the `.exe` file to run the tool.
3. The tool will automatically process all PDFs in the folder and generate output.


### Tool Capabilities and Considerations (SWOT Analysis)

**Strengths:**  
1. Supports multiple date formats and currencies, normalizing them for consistency.  
2. Extraction process checks for tables first and falls back to text-based extraction, increasing reliability.  

**Weaknesses:**  
1. Currently supports only English and could benefit from improved handling of highly complex PDFs, offering opportunities to expand language support and enhance accuracy.
2. Uses current exchange rates instead of rates on actual invoice dates for currency conversion.  
3. The executable file is designed to run only on Windows OS.

**Opportunities:**  
1. Integrate real-time Forex data to convert non-EUR currencies to EUR using an API like Open Exchange Rates, improving conversion accuracy based on exchange rates on specific invoice dates. 
2. Leverage advanced AI-based tools like LlamaIndex's SmartPDFLoader to enhance PDF data extraction, for better handling of complex and poorly structured invoices, ensuring more accurate data retrieval.
3. The tool can be adapted and built for different operating systems, broadening its usability across diverse environments.

**Threats:**  
1. In cases of incomplete extraction, downstream calculations and summaries might require further refinement to ensure accuracy.

### Troubleshooting

- Ensure PDFs are in the same folder as the executable.
- Check for corrupted PDFs.
- Verify executable permissions.
