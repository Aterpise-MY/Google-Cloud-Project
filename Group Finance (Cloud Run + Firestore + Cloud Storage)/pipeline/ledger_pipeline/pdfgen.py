"""HTML -> PDF (WeasyPrint; needs pango + a CJK font, both installed by the Dockerfile)."""

MAX_HTML_BYTES = 5 * 1024 * 1024  # 5 MB defensive memory cap to prevent container OOM


def html_to_pdf(html: str, max_bytes: int = MAX_HTML_BYTES) -> bytes:
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    encoded_len = len(html.encode("utf-8"))
    if encoded_len > max_bytes:
        raise ValueError(f"HTML payload size ({encoded_len} bytes) exceeds maximum allowed limit ({max_bytes} bytes)")
    from weasyprint import HTML  # imported lazily so tests/preview don't need native libs
    return HTML(string=html).write_pdf()

