import os

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

from formatter import remove_watermark

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name='images')
load_dotenv()


class DocxData(BaseModel):
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
async def createDocx(docxdata: DocxData):
    print(check_images_in_html(docxdata.htmlContent))
    try:
        html = docxdata.htmlContent
        filename = docxdata.filename
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

        html_content = remove_watermark(html_content, UPLOAD_DIRECTORY, TEMP_FOLDER)

        return JSONResponse(content={"documentData": html_content, "message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "There was an error uploading the file"}, status_code=400)
