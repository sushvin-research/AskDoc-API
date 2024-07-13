import os
import mammoth
from docx import Document
from dotenv import load_dotenv
from htmldocx import HtmlToDocx
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import aspose.words as aw
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from formatter import remove_watermark, p_tags_update, table_tags_update
import pdfkit

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name='images')
load_dotenv()


class DocxData(BaseModel):
    filename: str
    htmlContent: str


class PDFData(BaseModel):
    filename: str
    htmlContent: str


@app.get("/")
async def root():
    return {"message": "AskDoc API is running"}


def check_images_in_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    img_tags = soup.find_all('img')
    image_status = {}

    for img in img_tags:
        img_url = img.get('src')
        try:
            response = requests.head(img_url)
            image_status[img_url] = response.status_code == 200
        except requests.RequestException:
            image_status[img_url] = False

    return image_status


@app.post("/convert/htmltodocx/")
async def createDocx(docx_data: DocxData):
    print(check_images_in_html(docx_data.htmlContent))
    try:
        html = docx_data.htmlContent
        html = table_tags_update(html)
        filename = docx_data.filename
        document = Document()
        new_parser = HtmlToDocx()
        new_parser.add_html_to_document(html, document)
        document.save(filename)
        return {"status": "success", "message": "File created successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/convert/docxtohtml/")
async def create_upload_file(file: UploadFile = File(...), currentUserId: str = Form(...),
                             currentDocumentId: str = Form(...)):
    try:
        TEMP_FOLDER = f".docx_{currentDocumentId}_process_{currentUserId}"
        UPLOAD_DIRECTORY = f"data/document_images/{currentUserId}/{currentDocumentId}/{TEMP_FOLDER}/"
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)
        contents = await file.read()
        with open(UPLOAD_DIRECTORY + file.filename, 'wb') as f:
            f.write(contents)

        doc = aw.Document(UPLOAD_DIRECTORY + file.filename)
        doc.save(UPLOAD_DIRECTORY + "output.html")

        with open(UPLOAD_DIRECTORY + "output.html", 'r') as f:
            html_content = f.read()

        with open(UPLOAD_DIRECTORY + file.filename, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)

        html_content = remove_watermark(html_content, UPLOAD_DIRECTORY, TEMP_FOLDER)

        html_content = p_tags_update(html_content, result.value)

        return JSONResponse(content={"documentData": html_content, "message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "There was an error uploading the file"}, status_code=400)


@app.post("/convert/htmltopdf/")
def convert_html_to_pdf(pdf_data: PDFData):
    html = pdf_data.htmlContent
    html = table_tags_update(html)
    filename = pdf_data.filename
    pdfkit.from_string(html, filename)
    return {"status": "success", "path": filename, "message": "File uploaded successfully"}
