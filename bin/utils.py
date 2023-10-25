from kivymd.app import MDApp

import bcrypt
import json


def signup_user(app: MDApp):
    # Get account name and check
    inputs = {
        "account": app.root.ids["signup_account"].text,
        "email": app.root.ids["signup_email"].text,
        "password": app.root.ids["signup_password"].ids["password"].text,
    }
    errors = form_validator(inputs)
    # Check if signup is successfull or not
    if errors != "":
        app.root.ids["notification_text"].text = errors
        return
    else:
        query = f"""
            INSERT INTO users (username, email, password)
            VALUES('{inputs["account"]}','{inputs["email"]}',"{get_hashed_password(inputs["password"])}")
        """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            app.root.ids["root_screen_manager"].current = "login"
            # Notify user
            app.root.ids["notification_text"].text = "User created successfully!"
        except Exception:
            print("Registration failed")


def check_login_user(app: MDApp):
    # Get account name and check
    inputs = {
        "account": app.root.ids["login_user"].text,
        "password": app.root.ids["login_password"].ids["password"].text,
    }
    # Validate inputs
    errors = form_validator(inputs)
    if errors != "":
        app.root.ids["notification_text"].text = errors
        return None
    else:
        # Fetch user
        query = f"SELECT * FROM users WHERE username = '{inputs['account']}'"
        user = app.cursor.execute(query).fetchone()
        # Is user exist check psw
        if user is not None:
            if check_password(inputs["password"], user[3]):
                # Create file to cache user logged
                with open("logged_user.json", "w") as fp:
                    json.dump(user, fp)
                return user
    app.root.ids["notification_text"].text = "Username or password missmatch"
    return None


def check_user(app: MDApp, user_dict: dict) -> bool:
    query = f"SELECT * FROM users WHERE id = {user_dict[0]} AND email = '{user_dict[1]}' AND username = '{user_dict[2]}'"
    user = app.cursor.execute(query).fetchone()
    # Is user exist check psw
    if user is not None:
        return True
    return False


def form_validator(form_inputs: dict) -> str:
    """Given a dict of inputs, check if they are empty and return erros

    Args:
        form_inputs (dict): Inputs

    Returns:
        str: Errors string
    """
    errors = []
    for idx in form_inputs:
        if form_inputs[idx] == "":
            errors.append(f"Missing {idx.capitalize()}")
    return "\n".join(errors)


def get_hashed_password(plain_text_password: str) -> str:
    """Given a text password, returns the hashed version of it

    Args:
        plain_text_password (str): Text password

    Returns:
        str: Hashed psw
    """
    # (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode()


def check_password(plain_text_password: str, hashed_password: str) -> bool:
    """Given a text password and hashed password check if they match

    Args:
        plain_text_password (str): Text password
        hashed_password (str): Hashed password

    Returns:
        bool: Whether the password matches or not
    """
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(
        bytes(plain_text_password, "utf-8"), bytes(hashed_password, "utf-8")
    )
