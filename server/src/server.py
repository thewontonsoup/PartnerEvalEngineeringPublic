import os
import uuid
import json
from text_extraction.unstructured_extract import extract_text
from clean_text.clean_text import clean_full_chunk
from transformation import gpt, gptPortfolio
from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from chromadb.utils import embedding_functions
from database.database_handler import database_add
import chromadb
import tempfile
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed


app = Flask(__name__)

# Enable CORS for the /upload route, allowing requests from http://localhost:3000
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})
#  python -m flask --app server.py run

load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")

MAX_FILE_PROCESSING_THREADS = 4

DATABASE_DATA_FOLDER = "./db"
DATABASE_COLLECTION_NAME = "finalized_jsons"
DATABASE_EMBEDDING_FUNCTION = embedding_functions.DefaultEmbeddingFunction()
DATABASE_CHROMA_CLIENT = chromadb.PersistentClient(path=DATABASE_DATA_FOLDER)
DATABASE_COLLECTION = DATABASE_CHROMA_CLIENT.get_or_create_collection(
    name=DATABASE_COLLECTION_NAME, embedding_function=DATABASE_EMBEDDING_FUNCTION)

# Define directories for different stages
UPLOAD_FOLDER = 'uploads/'
DRAFT_FOLDER = 'drafts/'
FINAL_FOLDER = 'finalized/'
TEMP_FOLDER = 'temp/'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DRAFT_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(DATABASE_DATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/')
def home():
    return "Partner PDF Parser"


@app.route('/upload', methods=['POST'])
def upload() -> tuple[Response, int]:
    """
    Turns each PDF file given in the request into a JSON representing the parsed data from it. The JSON(s) are then added to the response.
    The request expects a field name `pdf_files` under files and a field named `doc_types` under form. The length of these fields must be equal.

    Args:
        None

    Returns:
        tuple[Response, int]: Response object and corresponding status code
    """
    try:
        # extract necessary information from the request
        # Expecting field name "pdf_files"
        
        print("Request Form:", request.form)

        files = request.files.getlist('file')
        print(files)

        if not files:
            return jsonify({"error": "No files provided"}), 400

        # Expecting field name "doc_types"
        doc_types = request.form.getlist('doc_types')
        if not doc_types:
            return jsonify({"error": "No file types (doc types) provided"}), 400

        if len(files) != len(doc_types):
            return jsonify({"error": "Number of files and doc types do not match"}), 400


        def process_single_file(index: int, file, doc_type: str) -> tuple[int, dict[str, str], int]:
            """
            Process a single file and return its parsed JSON data
            
            Args:
                index: the index of the file in the list
                file: the file object
                doc_type: the type of document as a str

            Returns:
                tuple[int, dict[str, str], int]: the index of the file, the parsed JSON data as a dict, and the status code
            """
            # make sure each file is a pdf
            if not file and not file.filename.lower().endswith('.pdf'):
                return index, {"error": "One or more selected files have no filename"}, 400

            # create id and filepath + save file
            unique_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            id_and_filename = f"{unique_id}_{filename}"[:128]  # limit to 128 characters, first 32 are uuid
            id_and_filename = id_and_filename + (
                "" if id_and_filename.endswith(".pdf") else ".pdf")  # add .pdf if cut off above
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], id_and_filename)

            try:
                # save file to upload folder
                file.save(filepath)

                # if file is portfolio jump to function process_portfolio
                if 'portfolio' in filename.lower():
                    return index, *process_portfolio(index, unique_id, doc_type, filepath)

                # generaye draft json
                draft_json = process_pdf_to_draft(unique_id, doc_type, filepath)
                if not draft_json:
                    return index, {"error": f"Unable to extract text from: {file.filename}"}, 400
                
                # clean draft json by replacing empty strings with None
                draft_json_obj: dict[str, str | None] = json.loads(draft_json)
                for key, val in draft_json_obj.items():
                    if val == "":
                        draft_json_obj[key] = None

                cleaned_draft_json = json.dumps(draft_json_obj, ensure_ascii=False)

                # save draft json for future use
                draft_file_path = os.path.join(DRAFT_FOLDER, f"{unique_id}.json")
                with open(draft_file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_draft_json)

                # return resulting json
                return index, {
                    "unique_id": unique_id,
                    "draft_json": draft_json_obj
                }, 200
            
            except Exception as e:
                return index, {"error": f"Error saving file {filename}: {str(e)}"}, 500

        # create results list
        results = [None] * len(files)

        # process files in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers = MAX_FILE_PROCESSING_THREADS) as executor:
            # submit tasks to the executor and get futures
            futures = [executor.submit(process_single_file, ind, file, doctype) for ind, (file, doctype) in enumerate(zip(files, doc_types))]

            # process results as they finish executing
            for future in as_completed(futures):
                index, data, status = future.result()
                if status != 200:
                    return jsonify(data), status
                # store the result in the results list
                results[index] = data

        # Once all files are processed, return the results
        return jsonify(results), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the files"}), 400

def process_pdf_to_draft(uuid: str, doctype: str, file_path: str) -> str:
    """
    Turns the given PDF file into a JSON formatted string through text extraction, text cleaning, and text parsing
    Args:
        uuid: a str representing the documents's id
        filetype: a str representing the type of document
        file_path: a str representing the path to the uploaded pdf file
    Returns:
        str: a JSON formatted string representing the parsed text
    """

    results = ""
    # Check if input file exists
    if not os.path.exists(file_path):
        print(f"ERROR: Input file does not exist: {file_path}")
        return ""
    
    # Ensure temp folder exists
    try:
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        print(f"Temp folder created/exists: {TEMP_FOLDER}")
    except Exception as e:
        print(f"ERROR: Cannot create temp folder: {e}")
        return ""
    
    # create path where to extract text to
    extracted_text_file_path = os.path.join(TEMP_FOLDER, uuid + ".txt")
    print(f"Will extract text to: {extracted_text_file_path}")
    
    # call function to extract text
    print("=== Calling extract_text function ===")
    try:
        extract_result = extract_text(file_path, extracted_text_file_path)
        print(f"Extract text result: {extract_result}")
        
        if not extract_result:
            print("ERROR: extract_text returned False")
            return ""
            
    except Exception as e:
        print(f"ERROR: extract_text threw exception: {e}")
        return ""
    
    # Check if extracted text file was created
    if not os.path.exists(extracted_text_file_path):
        print(f"ERROR: Extracted text file was not created: {extracted_text_file_path}")
        return ""
    
    print(f"Extracted text file size: {os.path.getsize(extracted_text_file_path)} bytes")
    
    # call appropriate methods
    try:
        # call openai api for parsing
        print("=== Reading extracted text ===")
        file_text = ""
        with open(extracted_text_file_path, "r", encoding="utf-8", errors="replace") as infile:
            file_text = infile.read()
        
        if not file_text.strip():
            print("ERROR: No text content extracted")
            return ""
        
        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY is not set")
            return ""
        
        results = gpt.request(doctype, OPENAI_API_KEY, file_text).content
        
    except Exception as e:
        print(f"Error during OpenAI API request: {str(e)}")
        return ""
    finally:
        # clean temp files
        if os.path.exists(extracted_text_file_path):
            os.remove(extracted_text_file_path)
            print(f"Cleaned up temp file: {extracted_text_file_path}")
    
    print("=== process_pdf_to_draft completed successfully ===")
    # return json formatted str
    return results

def process_portfolio(index: int, uuid: str, doctype: str, file_path: str) -> tuple[dict, int]:
    """
        Extracts text from a multi‐property (portfolio) PDF, sends it to GPT, parses the multiple JSON objects, and returns them as a list.

        Args:
            index: index for threading
            uuid: a str representing the documents's id
            filetype: a str representing the type of document
            file_path: a str representing the path to the uploaded pdf file

        Returns:
            str: a JSON formatted string representing the parsed text with multiple jsons for the multiple properties
        """

    # Extract text
    txt_path = os.path.join(TEMP_FOLDER, f"{uuid}.txt")
    if not extract_text(file_path, txt_path):
        return {"error": "Text extraction failed"}, 400

    with open(txt_path, 'r', encoding='utf-8') as in_f:
        content = in_f.read()

    try:
        raw = gptPortfolio.request(doctype, OPENAI_API_KEY, content).content
        portfolio_list = json.loads(raw)
    except Exception as e:
        os.remove(txt_path)
        return {"error": f"GPT portfolio parsing failed: {e}"}, 500

    os.remove(txt_path)

    for entry in portfolio_list:
        for k, v in entry.items():
            if v == "":
                entry[k] = None

    draft_path = os.path.join(DRAFT_FOLDER, f"{uuid}.json")
    with open(draft_path, 'w', encoding='utf-8') as f:
        json.dump(portfolio_list, f, ensure_ascii=False)
    return {"unique_id": uuid, "draft_json": portfolio_list}, 200

@app.route('/finalize', methods=['POST'])
def finalize() -> tuple[Response, int]:
    """
    Takes in a list of one or more JSON objects and saves them to the database.
    Each JSON object (JSON for each file) should be formatted as:
    ```
    {
        "filename": {
            field1: data1,
            field2, data2,
            ...
        }
    }
    ```
    As such the overall json sent to the request should be formatted as:
    ```
    [
        { "filename1": { "field1": "data1", "field2": "data2" } },
        { "filename2": { "field1": "data1", "field2": "data2" } },
        { "filename3": { "field1": "data1", "field2": "data2" } },
        ...
    ]
    ```

    Args:
        None

    Returns:
        tuple[Response, int]: Response object and corresponding status code
    """
    try:
        # get data as json
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Request expects a list of JSON objects"}), 400

        response = []

        # process each finalzed json object
        for final_json in data:
            if not isinstance(final_json, dict) or len(final_json) != 1:
                return jsonify(
                    {"error": "Final JSON is not properly formatted or there is more than one filename present"}), 400

            filename, final_data = next(iter(final_json.items()))

            if not isinstance(final_data, dict):
                return jsonify({"error": f"JSON of {filename} is not properly formatted"}), 400

            # save final json to file
            final_data_str = json.dumps(final_data)
            secured_filename = secure_filename(filename)
            final_file_path = os.path.join(FINAL_FOLDER, f"{secured_filename}.json")
            with open(final_file_path, "w", encoding="utf-8") as f:
                f.write(final_data_str)

            try:
                # save final json to database
                database_add(DATABASE_COLLECTION,
                            doc_list=[final_data_str],
                            id_list=[filename],
                            metadata_list=[{'finalized': "True"}])
            except Exception as e:
                print(f"Error saving to database: {str(e)}")
                return jsonify({"error": f"Error saving {filename} to database"}), 500

            response.append({"filename": filename, "status": "finalized"})

        # return response with success
        return jsonify({"message": "All files successfully saved", "data": response}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while finalizing the files"}), 400

if __name__ == '__main__':
    app.run(debug=True)

