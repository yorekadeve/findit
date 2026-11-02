from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import mysql.connector
import os
from datetime import date
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def login_required(route_function):
    @wraps(route_function)
    def protected_route(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    return protected_route

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report-lost", methods=["GET", "POST"])
@login_required
def report_lost():
    if request.method == "POST":
        item_name = request.form["item_name"]
        category = request.form["category"]
        color = request.form["color"]
        brand = request.form["brand"]
        description = request.form["description"]
        location = request.form["location"]
        date_lost = request.form["date_lost"]
        contact = request.form["contact"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO lost_items
            (user_id,item_name, category, color, brand, description, location, date_lost, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, (session["user_id"],item_name, category, color, brand, description, location, date_lost, contact))

        conn.commit()
        cursor.close()
        conn.close()

        return "Lost item reported successfully!"

    return render_template("report_lost.html")

@app.route("/report-found", methods=["GET", "POST"])
@login_required
def report_found():
    if request.method == "POST":
        item_name = request.form["item_name"]
        category = request.form["category"]
        color = request.form["color"]
        brand = request.form["brand"]
        description = request.form["description"]
        location = request.form["location"]
        date_found = request.form["date_found"]
        contact = request.form["contact"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO found_items
            (user_id,item_name, category, color, brand, description, location, date_found, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, (session["user_id"],item_name, category, color, brand, description, location, date_found, contact))

        conn.commit()
        cursor.close()
        conn.close()

        return "Found item reported successfully!"

    return render_template("report_found.html")

@app.route("/my-reports")
@login_required
def my_reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM lost_items
        WHERE user_id = %s
    """, (session["user_id"],))
    lost_items = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM found_items
        WHERE user_id = %s
    """, (session["user_id"],))
    found_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "my_reports.html",
        lost_items=lost_items,
        found_items=found_items
    )

@app.route("/delete-lost/<int:item_id>", methods=["POST"])
@login_required
def delete_lost(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM lost_items
        WHERE id = %s AND user_id = %s
    """, (item_id, session["user_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Lost item report deleted successfully.", "success")
    return redirect(url_for("my_reports"))

@app.route("/edit-lost/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_lost(item_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        item_name = request.form["item_name"]
        category = request.form["category"]
        color = request.form["color"]
        brand = request.form["brand"]
        description = request.form["description"]
        location = request.form["location"]
        date_lost = request.form["date_lost"]
        contact = request.form["contact"]

        cursor.execute("""
            UPDATE lost_items
            SET item_name = %s,
                category = %s,
                color = %s,
                brand = %s,
                description = %s,
                location = %s,
                date_lost = %s,
                contact = %s
            WHERE id = %s AND user_id = %s
        """, (
            item_name,
            category,
            color,
            brand,
            description,
            location,
            date_lost,
            contact,
            item_id,
            session["user_id"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Lost item report updated successfully.", "success")
        return redirect(url_for("my_reports"))

    cursor.execute("""
        SELECT * FROM lost_items
        WHERE id = %s AND user_id = %s
    """, (item_id, session["user_id"]))

    item = cursor.fetchone()

    cursor.close()
    conn.close()

    if item is None:
        flash("Report not found.", "warning")
        return redirect(url_for("my_reports"))

    return render_template("edit_lost.html", item=item)

@app.route("/delete-found/<int:item_id>", methods=["POST"])
@login_required
def delete_found(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM found_items
        WHERE id = %s AND user_id = %s
    """, (item_id, session["user_id"]))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Found item report deleted successfully.", "success")
    return redirect(url_for("my_reports"))

@app.route("/edit-found/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_found(item_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        item_name = request.form["item_name"]
        category = request.form["category"]
        color = request.form["color"]
        brand = request.form["brand"]
        description = request.form["description"]
        location = request.form["location"]
        date_found = request.form["date_found"]
        contact = request.form["contact"]

        cursor.execute("""
            UPDATE found_items
            SET item_name = %s,
                category = %s,
                color = %s,
                brand = %s,
                description = %s,
                location = %s,
                date_found = %s,
                contact = %s
            WHERE id = %s AND user_id = %s
        """, (
            item_name,
            category,
            color,
            brand,
            description,
            location,
            date_found,
            contact,
            item_id,
            session["user_id"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Found item report updated successfully.", "success")
        return redirect(url_for("my_reports"))

    cursor.execute("""
        SELECT * FROM found_items
        WHERE id = %s AND user_id = %s
    """, (item_id, session["user_id"]))

    item = cursor.fetchone()

    cursor.close()
    conn.close()

    if item is None:
        flash("Report not found.", "warning")
        return redirect(url_for("my_reports"))

    return render_template("edit_found.html", item=item)

@app.route("/items")
def items():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM lost_items ORDER BY id DESC")
    lost_items = cursor.fetchall()

    cursor.execute("SELECT * FROM found_items ORDER BY id DESC")
    found_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("items.html", lost_items=lost_items, found_items=found_items)

@app.route("/matches", methods=["GET", "POST"])
@login_required
def matches():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        lost_item_id = request.form["lost_item_id"]
        found_item_id = request.form["found_item_id"]
        match_date = date.today()

        cursor.execute("""
            INSERT INTO matches
            (lost_item_id, found_item_id, match_date, status)
            VALUES (%s, %s, %s, %s)
        """, (lost_item_id, found_item_id, match_date, "Pending"))

        conn.commit()

    cursor.execute("SELECT * FROM lost_items ORDER BY id DESC")
    lost_items = cursor.fetchall()

    cursor.execute("SELECT * FROM found_items ORDER BY id DESC")
    found_items = cursor.fetchall()

    cursor.execute("""
        SELECT
            matches.id,
            lost_items.item_name AS lost_item,
            found_items.item_name AS found_item,
            matches.match_date,
            matches.status
        FROM matches
        JOIN lost_items ON matches.lost_item_id = lost_items.id
        JOIN found_items ON matches.found_item_id = found_items.id
        ORDER BY matches.id DESC
    """)
    all_matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "matches.html",
        lost_items=lost_items,
        found_items=found_items,
        all_matches=all_matches
    )

@app.route("/suggestions")
def suggestions():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            lost_items.id AS lost_id,
            lost_items.item_name AS lost_item,
            lost_items.category AS lost_category,
            lost_items.color AS lost_color,
            lost_items.brand AS lost_brand,
            lost_items.location AS lost_location,
            found_items.id AS found_id,
            found_items.item_name AS found_item,
            found_items.category AS found_category,
            found_items.color AS found_color,
            found_items.brand AS found_brand,
            found_items.location AS found_location,
            (
                (lost_items.category = found_items.category) +
                (lost_items.color = found_items.color) +
                (lost_items.brand = found_items.brand) +
                (lost_items.location = found_items.location)
            ) AS match_score
        FROM lost_items
        JOIN found_items
        WHERE lost_items.status = 'Lost'
        AND found_items.status = 'Found'
        HAVING match_score >= 2
        ORDER BY match_score DESC
    """)

    suggested_matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "suggestions.html",
        suggested_matches=suggested_matches
    )

@app.route("/search", methods=["GET", "POST"])
def search():
    found_results = []
    lost_results = []
    searched = False

    if request.method == "POST":
        category = request.form.get("category", "")
        color = request.form.get("color", "")
        brand = request.form.get("brand", "")
        location = request.form.get("location", "")

        searched = True

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM found_items
            WHERE category LIKE %s
            AND color LIKE %s
            AND brand LIKE %s
            AND location LIKE %s
            ORDER BY id DESC
        """, (f"%{category}%", f"%{color}%", f"%{brand}%", f"%{location}%"))

        found_results = cursor.fetchall()

        cursor.execute("""
            SELECT * FROM lost_items
            WHERE category LIKE %s
            AND color LIKE %s
            AND brand LIKE %s
            AND location LIKE %s
            ORDER BY id DESC
        """, (f"%{category}%", f"%{color}%", f"%{brand}%", f"%{location}%"))

        lost_results = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "search.html",
        found_results=found_results,
        lost_results=lost_results,
        searched=searched
    )

@app.route("/confirm-match/<int:match_id>")
def confirm_match(match_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE matches
        SET status = 'Confirmed'
        WHERE id = %s
    """, (match_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("matches"))

@app.route("/return-item/<int:match_id>")
def return_item(match_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT lost_item_id, found_item_id
        FROM matches
        WHERE id = %s
    """, (match_id,))

    match = cursor.fetchone()

    if match:
        lost_item_id = match["lost_item_id"]
        found_item_id = match["found_item_id"]

        cursor.execute("""
            UPDATE matches
            SET status = 'Returned'
            WHERE id = %s
        """, (match_id,))

        cursor.execute("""
            UPDATE lost_items
            SET status = 'Returned'
            WHERE id = %s
        """, (lost_item_id,))

        cursor.execute("""
            UPDATE found_items
            SET status = 'Returned'
            WHERE id = %s
        """, (found_item_id,))

        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("matches"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match."

        password_hash = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (full_name, email, phone, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email, phone, password_hash, "user"))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]

            return redirect(url_for("home"))
        else:
            return "Invalid email or password."

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)