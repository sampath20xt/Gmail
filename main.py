import json
import shutil
import pandas as pd
import vertexai
import glob
import os
# import doc
import requests
from Email_extraction import extractor
from vertexai.preview.language_models import TextGenerationModel

# Extract emails initially
extractor()

# Docling API URL
DOCLING_API_URL = "http://34.41.177.18/pdf_process"

def docling_ocr(file_path):
    """
    Sends PDF file directly to Docling API for OCR and handles list responses.
    """
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(DOCLING_API_URL, files={'file': file})

        if response.status_code == 200:
            extracted_text = response.json().get('text', '')

            # Handle case where extracted_text is a list
            if isinstance(extracted_text, list):
                extracted_text = ' '.join(extracted_text)  # Join list items into a single string

            print(f"Extracted Text from {file_path}:\n", extracted_text)
            return extracted_text
        else:
            print(f"Docling API Error: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        print(f"Docling OCR Error: {e}")
        return ""

def Extraction(text):
    """
    Uses Vertex AI for extracting structured data from text.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "email-extraction-381718-3f73208ce3b71.json"
    vertexai.init(project="email-extraction-381718", location="us-central1")

    model_prediction = TextGenerationModel.from_pretrained("text-bison-32k")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 2048,
        "top_p": 0.4,
        "top_k": 30
    }
    prompt = """
        You are a fully trained extraction bot specialized in resumes.
        Your task is to identify candidate details from the text and return the information in valid JSON format.
        Extract the following keys:
        Name, Qualification, College Name, Passing year, Percentage, Phone, Email, Technologies.
        If data is missing, use "NULL" for those particular keys.
        Example output format:
        {
            "Name": " ",
            "Qualification": " ",
            "College Name": " ",
            "Passing year": " ",
            "Percentage": " ",
            "Phone": " ",
            "Email": " ",
            "Technologies": " "
        }
        """
    response = model_prediction.predict(prompt + text, **parameters)
    print(response)
    return response.text

# Process DOC and DOCX files
all_data = []
doc_file_list = glob.glob(os.path.join(os.getcwd(), "Base_Folder", "*.doc"))
docx_file_list = glob.glob(os.path.join(os.getcwd(), "Base_Folder", "*.docx"))
docx_file_list.extend(doc_file_list)

for docx_file in docx_file_list:
    if docx_file.endswith('doc'):
        from doc2docx import convert
        docx_file_name = os.path.basename(docx_file).split(".")[0] + ".docx"
        docx_file_path = os.path.join(os.getcwd(), "Base_Folder", docx_file_name)
        convert(docx_file, docx_file_path)
        os.remove(docx_file)
    else:
        docx_file_path = docx_file

    output_file_name = os.path.basename(docx_file_path).split(".")[0] + ".pdf"
    output_file_path = os.path.join(os.getcwd(), "Base_Folder", output_file_name)
    from docx2pdf import convert
    convert(docx_file_path, output_file_path)
    os.remove(docx_file_path)

# Process PDF files directly with Docling OCR
pdf_file_list = glob.glob(os.path.join(os.getcwd(), "Base_Folder", "*.pdf"))

for single_pdf in pdf_file_list:
    try:
        # Send PDF directly to Docling API
        extracted_text = docling_ocr(single_pdf)
        if not extracted_text:
            print(f"No text was extracted for {single_pdf}.")
            continue  # Skip if no text extracted

        # Extract structured data using Vertex AI
        data = Extraction(extracted_text)
        json_data = json.loads(data)
        print(json_data)

        # Convert JSON data to DataFrame
        df = pd.DataFrame.from_dict(json_data, orient='index').T
        all_data.append(df)

        # Move processed PDF to the "Processed" folder
        final_dir = os.path.join(os.getcwd(), "Processed")
        if not os.path.exists(final_dir):
            os.mkdir(final_dir)
        shutil.move(single_pdf, os.path.join(final_dir, os.path.basename(single_pdf)))

    except Exception as e:
        # Move unprocessed PDFs to the "Unprocessed" folder
        final_dir = os.path.join(os.getcwd(), "Unprocessed")
        if not os.path.exists(final_dir):
            os.mkdir(final_dir)
        shutil.move(single_pdf, os.path.join(final_dir, os.path.basename(single_pdf)))
        print(f"Error processing {single_pdf}: {e}")

# Save the final concatenated DataFrame to CSV
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv("Resume.csv", index=False)
else:
    print("No data extracted from any PDF.")
