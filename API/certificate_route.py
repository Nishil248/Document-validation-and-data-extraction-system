from flask import Blueprint, request, jsonify
import numpy as np
from copy import deepcopy
import traceback

from utils.helper import FileHelper
from utils.database import MongoDBManager
from repository.certificate_parser import CertificateParser



certificate_route = Blueprint("certificate_bp", __name__)

@certificate_route.route('/api/certificate/extract', methods=["POST"])
def process_certificate():
    try:
        # Step 1: Get file
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        helper = FileHelper("Certificate")
        np_img, error = helper.load_file_as_image(file)

        if np_img is None:
            return jsonify({"Error": error}), 400  

        helper.save_image(np_img)

        parser = CertificateParser(np_img)
        extracted_text = parser.extract_text()
        if not extracted_text:
            return jsonify({"error": "Unable to extract text from certificate"}), 422

        result = parser.extract_details(extracted_text)

        # Save to DB
        db = MongoDBManager()
        msg = db.insert_document("Certificate_collection", deepcopy(result))

        return {"Message":msg, "Extracted Details": result}, 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error Traceback:\n", error_trace)          
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
