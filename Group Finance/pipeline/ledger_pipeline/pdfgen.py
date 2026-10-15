"""HTML -> PDF (WeasyPrint; needs pango + a CJK font, both installed by the Dockerfile)."""


def html_to_pdf(html: str) -> bytes:
    from weasyprint import HTML  # imported lazily so tests/preview don't need native libs
    return HTML(string=html).write_pdf()
