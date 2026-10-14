import html2text


def html_to_md(html: str) -> str:
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.unicode_snob = True
    h.mark_code = True
    h.pad_tables = True
    return h.handle(html).strip()
