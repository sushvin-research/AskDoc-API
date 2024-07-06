import re


def remove_watermark(html_content):
    div_pattern = re.compile(r'<div.*?>.*?</div>', re.DOTALL)

    # Find all div tags
    div_tags = div_pattern.findall(html_content)

    # If there are at least two div tags, remove the first and last ones
    if len(div_tags) >= 2:
        html_content = html_content.replace(div_tags[0], '', 1)
        html_content = html_content.replace(div_tags[-1], '', 1)

    # Regex pattern to match the first <p> tag and its content
    p_pattern = re.compile(r'<p.*?>.*?</p>', re.DOTALL)

    # Find the first <p> tag
    p_tag = p_pattern.search(html_content)

    # Remove the first <p> tag if it exists
    if p_tag:
        html_content = html_content.replace(p_tag.group(0), '', 1)

    return html_content
