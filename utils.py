from bs4 import BeautifulSoup, Comment
import requests


def get_html(url, headers):
    request = requests.get(url, headers=headers)
    html = BeautifulSoup(request.content, 'html.parser')
    return html


def sanitize(soup):
    tag_blacklist = ['script', 'style', 'img',
                     'object', 'embed', 'iframe', 'svg', 'header', 'footer', 'aside', 'button', 'nav', 'audio', 'video', 'input', 'form', 'textarea']

    # Remove HTML comments
    for comment in soup.findAll(
            text=lambda text: isinstance(text, Comment)):
        comment.extract()
    # remove a tags keeping content
    for a in soup.find_all('a', href=True):
        a.replaceWithChildren()
    for img in soup.find_all('img'):
        img.decompose()
    for svg in soup.find_all('svg'):
        svg.decompose()
    # Remove unwanted tags
    for tag in soup.findAll():
        # Remove blacklisted tags and their contents.
        if tag.name in tag_blacklist:
            tag.decompose()
            break

    return soup


def select_content(soup):
    tags_to_keep = ['h1', 'h2', 'h3', 'h4',
                    'h5', 'h6', 'ul', 'ol', 'br']
    tag_array = list()
    for tag in soup.find_all():
        if tag.name == 'pre':
            tag_array.append(tag)
        if tag.name in tags_to_keep:
            sanitize(tag)
            tag_array.append(tag)
        if tag.name == 'p':
            sanitize(tag)
            tag_array.append(tag)
    return tag_array
