from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "exam_secret_key"


@app.route("/")
def home():
    return render_template(
        "index.html",
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("travel.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()
        connection.close()

        if user:
            session["username"] = user[1]
            session["role"] = user[3]
            return redirect("/")
        else:
            error = "Wrong username or password"

    return render_template(
        "login.html",
        error=error,
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(password) < 6:
            error = "Password must be at least 6 characters long"
            return render_template(
                "register.html",
                error=error,
                username=session.get("username"),
                role=session.get("role")
            )

        if password.isalpha():
            error = "Password must contain at least one number"
            return render_template(
                "register.html",
                error=error,
                username=session.get("username"),
                role=session.get("role")
            )

        connection = sqlite3.connect("travel.db")
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, password, "user"))

            connection.commit()
            connection.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            connection.close()
            error = "Username already exists"

    return render_template(
        "register.html",
        error=error,
        username=session.get("username"),
        role=session.get("role")
    )

@app.route("/book", methods=["POST"])
def book():
    if "username" not in session:
        return redirect("/login")

    destination = request.form["destination"]
    region = request.form["region"]
    price = request.form["price"]
    days = request.form["days"]
    username = session["username"]

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bookings (username, destination, region, price, days)
        VALUES (?, ?, ?, ?, ?)
    """, (username, destination, region, price, days))

    connection.commit()
    connection.close()

    return redirect("/bookings")


@app.route("/bookings")
def bookings():
    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM bookings
        WHERE username = ?
    """, (session["username"],))

    bookings = cursor.fetchall()
    connection.close()

    return render_template(
        "bookings.html",
        bookings=bookings,
        username=session.get("username"),
        role=session.get("role")
    )

@app.route("/delete/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM bookings
        WHERE id = ? AND username = ?
    """, (booking_id, session["username"]))

    connection.commit()
    connection.close()

    return redirect("/bookings")
@app.route("/admin")
def admin():

    if "username" not in session or session["role"] != "admin":
        return redirect("/login")

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE region = 'Europe'")
    europe_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE region = 'Asia'")
    asia_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        bookings=bookings,
        total_bookings=total_bookings,
        europe_bookings=europe_bookings,
        asia_bookings=asia_bookings,
        total_users=total_users,
        username=session.get("username"),
        role=session.get("role")
    )
@app.route("/admin/delete/<int:booking_id>", methods=["POST"])
def admin_delete_booking(booking_id):

    if "username" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM bookings
        WHERE id = ?
    """, (booking_id,))

    connection.commit()
    connection.close()

    return redirect("/admin")
@app.route("/admin/edit/<int:booking_id>", methods=["GET", "POST"])
def admin_edit_booking(booking_id):

    if "username" not in session or session["role"] != "admin":
        return redirect("/login")

    connection = sqlite3.connect("travel.db")
    cursor = connection.cursor()

    if request.method == "POST":
        destination = request.form["destination"]
        region = request.form["region"]
        price = request.form["price"]
        days = request.form["days"]

        cursor.execute("""
            UPDATE bookings
            SET destination = ?, region = ?, price = ?, days = ?
            WHERE id = ?
        """, (destination, region, price, days, booking_id))

        connection.commit()
        connection.close()

        return redirect("/admin")

    cursor.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    )

    booking = cursor.fetchone()

    connection.close()

    if booking is None:
        return redirect("/admin")

    return render_template(
        "admin_edit.html",
        booking=booking,
        username=session.get("username"),
        role=session.get("role")
    )
@app.route("/assistant", methods=["POST"])
def assistant():
    user_text = request.form["travel_request"].lower()

    destinations = [
        {
            "name": "Athens, Greece",
            "region": "Europe",
            "price": 5500,
            "type": ["culture", "history", "city"]
        },
        {
            "name": "Santorini, Greece",
            "region": "Europe",
            "price": 7200,
            "type": ["beach", "summer", "romantic"]
        },
        {
            "name": "Rome, Italy",
            "region": "Europe",
            "price": 5200,
            "type": ["culture", "history", "city", "food"]
        },
        {
            "name": "Ksamil, Albania",
            "region": "Europe",
            "price": 4800,
            "type": ["beach", "summer", "budget"]
        },
        {
            "name": "Tokyo, Japan",
            "region": "Asia",
            "price": 12000,
            "type": ["city", "technology", "culture"]
        },
        {
            "name": "Seoul, South Korea",
            "region": "Asia",
            "price": 9500,
            "type": ["city", "technology", "culture"]
        },
        {
            "name": "Hanoi, Vietnam",
            "region": "Asia",
            "price": 8500,
            "type": ["budget", "culture", "food"]
        },
        {
            "name": "Shanghai, China",
            "region": "Asia",
            "price": 9800,
            "type": ["city", "technology", "culture"]
        }
    ]

    recommendations = []

    for destination in destinations:
        score = 0

        if destination["region"].lower() in user_text:
            score += 2

        if "cheap" in user_text or "budget" in user_text or "affordable" in user_text:
            if destination["price"] <= 8500:
                score += 2

        for travel_type in destination["type"]:
            if travel_type in user_text:
                score += 2

        if destination["name"].split(",")[0].lower() in user_text:
            score += 3

        if score > 0:
            recommendations.append({
                "name": destination["name"],
                "region": destination["region"],
                "price": destination["price"],
                "score": score,
                "reason": "Matches your travel preferences"
            })

    recommendations = sorted(
        recommendations,
        key=lambda x: x["score"],
        reverse=True
    )

    if not recommendations:
        recommendations = [
            {
                "name": "Rome, Italy",
                "region": "Europe",
                "price": 5200,
                "score": 1,
                "reason": "Popular cultural destination"
            },
            {
                "name": "Tokyo, Japan",
                "region": "Asia",
                "price": 12000,
                "score": 1,
                "reason": "Popular city destination"
            },
            {
                "name": "Santorini, Greece",
                "region": "Europe",
                "price": 7200,
                "score": 1,
                "reason": "Popular beach destination"
            }
        ]

    return render_template(
        "assistant.html",
        user_text=user_text,
        recommendations=recommendations[:3],
        username=session.get("username"),
        role = session.get("role")
    )
@app.route("/about")
def about():
    return render_template(
        "about.html",
        username=session.get("username"),
        role=session.get("role")
    )



if __name__ == "__main__":
    app.run(debug=True, port=5004)