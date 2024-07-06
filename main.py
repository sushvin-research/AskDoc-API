import os
import re

from docx import Document
from htmldocx import HtmlToDocx
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import aspose.words as aw
from fastapi.responses import JSONResponse

from formatter import remove_watermark

app = FastAPI()


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
            # If the response status code is 200, the image exists
            image_status[img_url] = response.status_code == 200
        except requests.RequestException:
            # If there is any issue with the request, assume the image doesn't exist
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


UPLOAD_DIRECTORY = "uploads/"


@app.post("/convert/docxtohtml/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)
        contents = await file.read()
        with open(UPLOAD_DIRECTORY + file.filename, 'wb') as f:
            f.write(contents)

        doc = aw.Document(UPLOAD_DIRECTORY + file.filename)
        doc.save(UPLOAD_DIRECTORY + "output.html")

        with open(UPLOAD_DIRECTORY + "output.html", 'r') as f:
            html_content = f.read()

        html_content = remove_watermark(html_content)

        return JSONResponse(content={"documentData": html_content, "message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"message": "There was an error uploading the file"}, status_code=400)
