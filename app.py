import os
from functools import wraps

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session

from db import fetch_all, fetch_one, execute
from validators import validate_register, validate_login, validate_title

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")


# ---------- helpers ----------

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, stored_hash):
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


def login_user(user_id, name):
    session.clear()
    session["user_id"] = user_id
    session["name"] = name


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def render_todos(**extra):
    rows = fetch_all(
        "SELECT todo_id, title, is_done, created_at FROM todos "
        "WHERE user_id = %s ORDER BY todo_id DESC",
        (session["user_id"],),
    )
    extra.setdefault("add_value", "")
    extra.setdefault("add_error", "")
    extra.setdefault("edit_id", None)
    extra.setdefault("edit_error", "")
    extra.setdefault("edit_value", "")
    return render_template("todos.html", todos=rows, **extra)


# ---------- pages ----------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("todo_list"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors={}, name="", email="")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = validate_register(name, email, password, confirm)
    if errors:
        return render_template("register.html", errors=errors, name=name, email=email)

    try:
        user_id = execute(
            "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
            (email, name, hash_password(password)),
        )
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:  # duplicate e-mail (UNIQUE)
            return render_template(
                "register.html", errors={"email": "Email Already Exists"},
                name=name, email=email,
            )
        raise

    login_user(user_id, name)
    return redirect(url_for("todo_list"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", errors={}, email="")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = validate_login(email, password)
    if errors:
        return render_template("login.html", errors=errors, email=email)

    user = fetch_one(
        "SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,)
    )
    if user is None or not check_password(password, user["password_hash"]):
        return render_template(
            "login.html", errors={"form": "Invalid email or password"}, email=email
        )

    login_user(user["user_id"], user["name"])
    return redirect(url_for("todo_list"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- to-do ----------

@app.route("/todos")
@login_required
def todo_list():
    return render_todos()


@app.route("/todos/add", methods=["POST"])
@login_required
def add_todo():
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return render_todos(add_value=title, add_error=error)
    execute(
        "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
        (session["user_id"], title),
    )
    return redirect(url_for("todo_list"))


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
@login_required
def edit_todo(todo_id):
    title = request.form.get("title", "").strip()
    error = validate_title(title)
    if error:
        return render_todos(edit_id=todo_id, edit_error=error, edit_value=title)
    execute(
        "UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
        (title, todo_id, session["user_id"]),
    )
    return redirect(url_for("todo_list"))


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@login_required
def toggle_todo(todo_id):
    is_done = 1 if request.form.get("is_done") == "1" else 0
    execute(
        "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
        (is_done, todo_id, session["user_id"]),
    )
    return redirect(url_for("todo_list"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    execute(
        "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
        (todo_id, session["user_id"]),
    )
    return redirect(url_for("todo_list"))


# ---------- friendly errors ----------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", title="Page not found",
                           message="The page you asked for does not exist."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", title="Something went wrong",
                           message="Please try again in a moment."), 500


if __name__ == "__main__":
    app.run(debug=True)