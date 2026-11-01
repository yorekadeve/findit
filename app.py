from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from datetime import date
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report-lost", methods=["GET", "POST"])
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
            (item_name, category, color, brand, description, location, date_lost, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (item_name, category, color, brand, description, location, date_lost, contact))

        conn.commit()
        cursor.close()
        conn.close()

        return "Lost item reported successfully!"

    return render_template("report_lost.html")

@app.route("/report-found", methods=["GET", "POST"])
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
            (item_name, category, color, brand, description, location, date_found, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (item_name, category, color, brand, description, location, date_found, contact))

        conn.commit()
        cursor.close()
        conn.close()

        return "Found item reported successfully!"

    return render_template("report_found.html")

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

if __name__ == "__main__":
    app.run(debug=True)