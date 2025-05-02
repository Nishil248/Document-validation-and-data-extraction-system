from flask import Blueprint, request, jsonify
import numpy as np
import traceback

from utils.Text_extraction import TextExtractor
from utils.Validation import ValidateDocument
from utils.helper import FileHelper
from repository.aadhar_parser import AadharParser
from utils.database import MongoDBManager

from copy import deepcopy

aadhar_route = Blueprint("aadhar_bp", __name__)

@aadhar_route.route('/api/aadhar/extract', methods=['POST'])
def process_aadhar():
    try:
        if request.method == 'POST':

            # Step 1: Get file
            file = request.files.get("file")
            if not file:
                return jsonify({"error": "No file uploaded"}), 400

            # Step 2: Convert to image using FileHelper
            helper = FileHelper("Aadhar card")
            np_img, error = helper.load_file_as_image(file)

            if np_img is None:
                return jsonify({"Error": error}), 400  

            # Step 3: Extract text using YOLO + OCR
            extractor = TextExtractor("Models/Aadhar_Trained/weights/best.pt")
            extracted = extractor.extract_text(np_img)

            # Step 4: Validate extracted text
            validator = ValidateDocument()
            is_valid, msg = validator.validate_aadhar_card(extracted)
            if not is_valid:
                return jsonify({"error": msg}), 422

            # Step 5: Save file using helper
            helper.save_image(np_img)

            # Step 6: Parse the text
            parser = AadharParser(extracted)
            result = {
                "Name": parser.extract_name(),
                "DOB": parser.extract_dob(),
                "Gender": parser.extract_gender(),
                "Aadhar Number": parser.extract_aadhar_number()
            }

            # Save to MongoDB
            db = MongoDBManager()
            msg = db.insert_document("aadhar_collection", deepcopy(result))

            return {"Message": msg, "Extracted Data": result}, 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error Traceback:\n", error_trace)  
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500