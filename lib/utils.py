from kivymd.app import MDApp

import bcrypt
import json

DEFAULT_CATEGORIES = ["Food", "Transportation", "Utilities", "Personal"]


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
    # Reset text
    app.root.ids["notification_text"].text = ""
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


def save_expense(
    app: MDApp, expense: float, category: int, date: str, type: str
) -> bool:
    """Given the app with all user's information and an expense, store it

    Args:
        app (MDApp): The app object
        expense (float): The amount of the expense
        category (int): The category id of the expense
        date (str): Insertion date of the expense
        type (str): Wheter the expense is recurring or not
    """
    if app.user is not None:
        # Check expense type
        recurring = 1 if type == "recurring_expense" else 0
        # Build query
        query = f"""
            INSERT INTO expenses (date, amount, category_id, user_id, recurring)
            VALUES('{date}','{expense}', '{category}','{app.user[0]}', {recurring})
        """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            return True
        except Exception:
            return False


def delete_expense(app: MDApp, ids: list, type: str) -> bool:
    """Given a list of expenses, delete them

    Args:
        app (MDApp): The app object
        ids (list): List of ids of expense
        type (str): Mode of the delete
    Returns:
        bool: Whether the deletion was successfull or not
    """
    if app.user is not None:
        if len(ids) > 0 and type == "recurring":
            query = f"""
                DELETE from expenses WHERE id IN ({",".join(map(str, ids))}) AND user_id = {app.user[0]}
            """
        elif type == "tmp":
            query = f"""
                DELETE from expenses WHERE user_id = {app.user[0]} AND recurring = 0
            """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            return True
        except Exception:
            return False


def save_amount(app: MDApp, income: float) -> bool:
    if app.user is not None:
        # Check if user already has input
        query = f"""
            SELECT * FROM incomes WHERE user_id = {app.user[0]}
        """
        check = app.cursor.execute(query).fetchone()
        # Is user exist check psw
        if check is None:
            query = f"""
                INSERT INTO incomes (income, user_id)
                VALUES('{income}', '{app.user[0]}')
            """
        else:
            query = f"""
                UPDATE incomes SET income = '{income}' WHERE user_id = {app.user[0]}
            """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            return True
        except Exception:
            return False


def save_savings(app: MDApp, savings_pct: float) -> bool:
    if app.user is not None:
        # Check if user already has input
        query = f"""
            SELECT * FROM savings WHERE user_id = {app.user[0]}
        """
        check = app.cursor.execute(query).fetchone()
        # Is user exist check psw
        if check is None:
            query = f"""
                INSERT INTO savings (threshold, user_id)
                VALUES('{savings_pct}', '{app.user[0]}')
            """
        else:
            query = f"""
                UPDATE savings SET threshold = '{savings_pct}' WHERE user_id = {app.user[0]}
            """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            return True
        except Exception:
            return False


def save_category(app: MDApp, category: str, threshold: float) -> bool:
    if app.user is not None:
        # Check if user already has input
        query = f"""
            SELECT * FROM categories WHERE user_id = {app.user[0]} AND name = '{category}'
        """
        check = app.cursor.execute(query).fetchone()
        # Is user exist check psw
        if check is None:
            query = f"""
                INSERT INTO categories (name, threshold, user_id)
                VALUES('{category}', '{threshold}', '{app.user[0]}')
            """
        else:
            query = f"""
                UPDATE categories SET threshold = '{threshold}' WHERE id = {check[0]}
            """
        try:
            app.cursor.execute(query)
            app.conn.commit()
            # Go to login page
            return True
        except Exception:
            return False


def get_category(app: MDApp, category_id: int) -> str:
    if app.user is not None:
        # Check if user already has input
        query = f"""
            SELECT * FROM categories WHERE id = {category_id}
        """
        category = app.cursor.execute(query).fetchone()
        if category is not None:
            return category[1]
    return "None"


def create_expense_tables_data(app: MDApp, expenses: list, type: str) -> list:
    if app.user is None:
        return []
    table_data = []
    for expense in expenses:
        if type == "temp":
            table_data.append(
                [expense[0], expense[1], get_category(app, expense[3]), expense[2]]
            )
        else:
            table_data.append([expense[0], get_category(app, expense[3]), expense[2]])
    return table_data


def fetch_user_data(app: MDApp) -> dict:
    # Init dict
    user_data = {
        "budget": "0€",
        "net_budget": 0,
        "recurring_expenses": [],
        "temp_expenses": [],
        "income": "0€",
        "net_income": 0,
        "net_savings": 0,
        "savings": "(Current Savings: 0%)",
        "savings_threshold": 0,
        "categories": [],
        "category_budgets": {
            "Food": 0,
            "Transportation": 0,
            "Utilities": 0,
            "Personal": 0,
        },
    }
    if app.user is not None:
        user_data.update(retrieve_user_raw_data(app))
        # Update budget
        recurring_sum = sum([tmp[2] for tmp in user_data["recurring_expenses"]])
        temp_sum = sum([tmp[2] for tmp in user_data["temp_expenses"]])
        # Remove recurring expenses from income and update net budget
        user_data["net_budget"] = user_data["net_income"] - recurring_sum
        # Check if the user has savings option set
        if user_data["savings_threshold"] > 0:
            # Update net budget
            user_data["net_savings"] = user_data["net_budget"] * (
                user_data["savings_threshold"] / 100
            )
            user_data["net_budget"] -= user_data["net_savings"]

        # Update category budgets
        for category in DEFAULT_CATEGORIES:
            # Get the id of the category
            category_element = [
                element for element in user_data["categories"] if element[1] == category
            ][0]
            if category_element[2] > 0:
                # Compute budget
                user_data["category_budgets"][category] = user_data["net_budget"] * (
                    category_element[2] / 100
                )
        # Remove monthly expenses
        for expense in user_data["temp_expenses"]:
            # Get category
            expense_category = get_category(app, expense[3])
            # Update budget
            user_data["category_budgets"][expense_category] -= expense[2]
            user_data["net_budget"] -= expense[2]
        # Check
        assert (
            user_data["net_budget"]
            + recurring_sum
            + temp_sum
            + user_data["net_savings"]
            == user_data["net_income"]
        )
        # Update budget text
        user_data["budget"] = f"{user_data['net_budget']}€"
    return user_data


def retrieve_user_raw_data(app: MDApp) -> dict:
    user_data = {}
    # Get net income
    net_income_query = f"SELECT * FROM incomes WHERE user_id = {app.user[0]}"
    income = app.cursor.execute(net_income_query).fetchone()
    if income is not None:
        user_data["income"] = f"{income[1]}€"
        user_data["net_income"] = income[1]
    # Get savings
    net_savings_query = f"SELECT * FROM savings WHERE user_id = {app.user[0]}"
    net_savings = app.cursor.execute(net_savings_query).fetchone()
    if net_savings is not None:
        user_data["savings_threshold"] = net_savings[1]
    else:
        user_data["net_savings"] = 0
    # Get Recurring expenses
    r_expense_query = (
        f"SELECT * FROM expenses WHERE user_id = {app.user[0]} AND recurring = 1"
    )
    r_expense = app.cursor.execute(r_expense_query).fetchall()
    user_data["recurring_expenses"] = [
        [tmp[0], tmp[1], tmp[2], tmp[3]] for tmp in r_expense
    ]
    # Get Temp expenses
    t_expense_query = (
        f"SELECT * FROM expenses WHERE user_id = {app.user[0]} AND recurring = 0"
    )
    t_expense = app.cursor.execute(t_expense_query).fetchall()
    user_data["temp_expenses"] = [[tmp[0], tmp[1], tmp[2], tmp[3]] for tmp in t_expense]
    # Get categories
    categories_query = f"SELECT * FROM categories WHERE user_id = {app.user[0]}"
    user_data["categories"] = app.cursor.execute(categories_query).fetchall()
    # If categories are not initialized, create them
    if len(user_data["categories"]) == 0:
        for category in DEFAULT_CATEGORIES:
            save_category(app, category, 0)
        # Fetch again
        user_data["categories"] = app.cursor.execute(categories_query).fetchall()
    return user_data


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
