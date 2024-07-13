import re
import os
import shutil
import uuid
from bs4 import BeautifulSoup


def parse_html(html_string):
    soup = BeautifulSoup(html_string, 'lxml')
    body = soup.body
    body_children = body.find_all(recursive=False)
    html_content = "".join(str(child) for child in body_children)
    return html_content


def add_meta_tag(html_string):
    html = BeautifulSoup(html_string, 'lxml')
    head_tag = html.new_tag('head')
    html.html.insert(0, head_tag)
    meta_tag = html.new_tag('meta', charset='utf-8')
    html.head.append(meta_tag)
    return str(html)


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
                IMAGE_EXTENSION = img_url.split('.')[-1]
                IMAGE_NAME = f"{uuid.uuid4()}.{IMAGE_EXTENSION}"
                NEW_IMAGE_PATH = "/" + UPLOAD_DIRECTORY.replace(TEMP_FOLDER + "/", "") + IMAGE_NAME
                shutil.move(UPLOAD_DIRECTORY + img_url, NEW_IMAGE_PATH)
                img['src'] = os.getenv("IMAGE_BASE_URL") + NEW_IMAGE_PATH.replace("/data/", "")
                print(img['src'])
            else:
                return str(soup)
        except Exception as e:
            print('Error while parsing image path', e)
            return str(soup)
    shutil.rmtree(UPLOAD_DIRECTORY)
    return str(soup)


def clean_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    for p in soup.find_all('p'):
        if p.find('img'):
            span_tags = p.find_all('span')
            for span in span_tags:
                if 'style' in span.attrs:
                    del span.attrs['style']
                img_tags = span.find_all('img')
                for img in img_tags:
                    if 'style' in img.attrs:
                        style_rules = img['style'].split(';')
                        new_style_rules = [rule for rule in style_rules if not rule.strip().startswith('position')]
                        img['style'] = ';'.join(new_style_rules)
    return str(soup)


def p_tags_update(html_string_1, html_string_2):
    html_string_1 = clean_html(html_string_1)
    soup1 = BeautifulSoup(html_string_1, 'html.parser')
    soup2 = BeautifulSoup(html_string_2, 'html.parser')

    p_tags1 = [p for p in soup1.find_all('p') if not p.find_parent('table') and not p.find('img') and p.text.strip()]
    p_tags2 = [p for p in soup2.find_all('p') if not p.find_parent('table')]

    for i, (p_tag1, p_tag2) in enumerate(zip(p_tags1, p_tags2)):
        if p_tag1.has_attr('style'):
            p_tag2['style'] = p_tag1['style']
        p_tag1.replace_with(p_tag2)

    modified_html1 = str(soup1)
    return modified_html1


def table_tags_update(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    for table in soup.find_all('table'):
        table['style'] = 'border: 1px solid black; border-collapse: collapse;'
    for td in soup.find_all('td'):
        td['style'] = 'border: 1px solid black; border-collapse: collapse;'
    styled_html = str(soup)
    return styled_html
