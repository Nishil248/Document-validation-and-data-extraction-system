import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image
import io
import os

class FileHelper:
    def __init__(self, doc_type):
        self.folder_map = {
            "Aadhar card": "uploads/Aadhar",
            "PAN card": "uploads/Pan",
            "10th Marksheet": "uploads/Marksheet_10",
            "12th Marksheet": "uploads/Marksheet_12",
            "College Marksheet": "uploads/Marksheet_college",
            "Certificate": "uploads/Certificate"   
        }

        self.prefix_map = {
            "Aadhar card": "aadhar_card",
            "PAN card": "pan_card",
            "10th Marksheet": "marksheet10",
            "12th Marksheet": "marksheet12",
            "College Marksheet": "college_marksheet",
            "Certificate": "certificate"
        }

        if doc_type not in self.folder_map:
            raise ValueError(f"Unknown document type: {doc_type}")

        self.upload_dir = self.folder_map[doc_type]
        self.prefix = self.prefix_map[doc_type]
        os.makedirs(self.upload_dir, exist_ok=True)


    def save_image(self, np_img, extension='jpg'):
        count = len([
            f for f in os.listdir(self.upload_dir)
            if f.startswith(self.prefix)
        ])
        filename = f"{self.prefix}_{count + 1}.{extension}"
        full_path = os.path.join(self.upload_dir, filename)
        cv2.imwrite(full_path, np_img)


    def load_file_as_image(self, file):

        filename_ext = file.filename.split('.')[-1].lower()
        allowed_extensions = ["pdf", "png", "jpg", "jpeg"]

        if filename_ext not in allowed_extensions:
            return None, "Unsupported file format. Only PDF, PNG, JPG, and JPEG are allowed."

        try:
            if filename_ext == "pdf":
                pdf_bytes = file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            else:
                file_bytes = np.frombuffer(file.read(), np.uint8)
                np_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            return np_img, None
        except Exception as e:
            return None, f"Failed to process file: {str(e)}"