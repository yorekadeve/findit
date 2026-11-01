from flask import Flask, render_template, request
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

if __name__ == "__main__":
    app.run(debug=True)