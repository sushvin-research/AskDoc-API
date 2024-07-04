from docx import Document
from htmldocx import HtmlToDocx
from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests

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


@app.post("/convert/docxtohtml/")
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
