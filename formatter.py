import re
import os
import shutil
from bs4 import BeautifulSoup


def parse_html(html_string):
    soup = BeautifulSoup(html_string, 'lxml')
    body = soup.body
    body_children = body.find_all(recursive=False)
    html_content = "".join(str(child) for child in body_children)
    return html_content


def remove_watermark(html_content, UPLOAD_DIRECTORY, TEMP_FOLDER):
    div_pattern = re.compile(r'<div.*?>.*?</div>', re.DOTALL)
    div_tags = div_pattern.findall(html_content)
    if len(div_tags) >= 2:
        html_content = html_content.replace(div_tags[0], '', 1)
        html_content = html_content.replace(div_tags[-1], '', 1)
    p_pattern = re.compile(r'<p.*?>.*?</p>', re.DOTALL)
    p_tag = p_pattern.search(html_content)
    if p_tag:
        html_content = html_content.replace(p_tag.group(0), '', 1)
    html_content = parse_html(html_content)
    html_content = convert_images_path(html_content, UPLOAD_DIRECTORY, TEMP_FOLDER)
    return html_content


def convert_images_path(html_string, UPLOAD_DIRECTORY, TEMP_FOLDER):
    soup = BeautifulSoup(html_string, 'html.parser')
    img_tags = soup.find_all('img')
    for img in img_tags:
        img_url = img.get('src')
        try:
            if os.path.exists(UPLOAD_DIRECTORY + img_url):
                NEW_IMAGE_PATH = "/" + UPLOAD_DIRECTORY.replace(TEMP_FOLDER + "/", "") + "sample.png"
                shutil.move(UPLOAD_DIRECTORY + img_url, NEW_IMAGE_PATH)
                img['src'] = os.getenv("IMAGE_BASE_URL") + NEW_IMAGE_PATH.replace("/data/", "")
                shutil.rmtree(UPLOAD_DIRECTORY)
            else:
                return str(soup)
        except Exception as e:
            print('Error while parsing image path', e)
            return str(soup)
    return str(soup)
