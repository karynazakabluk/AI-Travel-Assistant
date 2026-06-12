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



if __name__ == "__main__":
    app.run(debug=True, port=5004)