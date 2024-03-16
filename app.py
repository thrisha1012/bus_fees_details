from flask import Flask, redirect, url_for, render_template, request, session
import mysql.connector
import datetime
import random  # for generating random numbers

app = Flask(__name__)
app.secret_key = 'ehorizon project'

# Function to connect to the MySQL database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='soorya',
            database='busfee'
        )
        print("Database connected successfully")
        return conn
    except Exception as e:
        print("Error connecting to database:", str(e))
        raise

# Function to check if a user exists in the database
def user_exists(rollno, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE rollno=%s AND password=%s", (rollno, password))
    user = cur.fetchone()
    conn.close()
    return user
def fetch_bus_detailss(busno,stop):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM busdetails WHERE busnumber=%s AND busstop=%s", (busno, stop))
    bus = cur.fetchone()
    conn.close()
    return bus
# Function to add a new user to the database
# Function to add a new user to the database
def add_user(rollno, password, firstname, lastname, email, busnumber, busstop):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO user (rollno, password, firstname, lastname, email, busnumber, busstop) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (rollno, password, firstname, lastname, email, busnumber, busstop))
    conn.commit()
    conn.close()
# Function to create a new transaction ID
def create_transaction_id(rollno):

    # Generate a timestamp with current date and time
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Extract the last three digits of the roll number
    rollno_last_three = rollno[-3:]

    # Generate a random number between 100 and 999
    random_number = random.randint(100, 999)

    # Combine timestamp, date, and last three digits of the roll number to create the transaction ID
    transaction_id = f"{timestamp}_{rollno_last_three}_{random_number}"

    return transaction_id

# Function to add a new transaction to the database
# def add_transaction(transaction_id, rollno, amount, status):
#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO transactions (transaction_id, rollno, amount, status) VALUES (%s, %s, %s, %s)",
#                 (transaction_id, rollno, amount, status))
#     conn.commit()
#     conn.close()
def fetch_bus_details(bus_number):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM busdetails WHERE busnumber= %s", (bus_number,))
    bus_details = cur.fetchall()
    conn.close()
    print(bus_details,bus_number,end=" ")
    return bus_details

def fetch_transaction_details(rollno):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE rollno = %s", (rollno,))
    transaction_details = cur.fetchall()
    conn.close()
    return transaction_details
def fetch_user_details(rollno):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE rollno = %s", (rollno,))
    user_details = cur.fetchone()  # Use fetchone to retrieve a single row
    conn.close()
    print("Got the following details from DB:", user_details)
    return user_details
def fetch_all_bus_details():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM busdetails")
    bus_details = cur.fetchall()
    conn.close()
    return bus_details

@app.route("/show_transport", methods=["GET", "POST"])
def bus_details():
    # Fetch bus numbers from the busdetails table
    bus_numbers = fetch_bus_numbers()

    # Fetch bus details based on filtering options
    if request.method == "POST":
        bus_number_filter = request.form.get("bus_number")
        if bus_number_filter:
            bus_details = fetch_bus_details(bus_number_filter)
        else:
            bus_details = fetch_all_bus_details()
    else:
        print("fetched all bus details")
        bus_details = fetch_all_bus_details()
    print("These are the bus details", bus_details)
    return render_template("transport.html", bus_numbers=bus_numbers, bus_details=bus_details)

@app.route('/transport')
def transport():
    return render_template('transport.html')
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        rollno = request.form["rollno"]
        password = request.form["password"]
        user = user_exists(rollno, password)
        if user:
            # Store user information in session
            session['rollno'] = rollno
            session['firstname'] = user[2]  # Assuming the firstname is stored at index 2
            session['stat'] = user[6]

            # Fetch user details
            user_details = fetch_user_details(rollno)

            # Fetch bus details
            bus_details = fetch_bus_detailss(user_details[7], user_details[8])
            print("The bus details of the student",bus_details)
            if bus_details:
                amount = bus_details[2]  # Assuming 'amount' is the column name for the amount in bus_details
                session['amount'] = amount
                print("The amount is ",amount)
            else:
                # If bus details not found, set amount to 0 or any default value
                session['amount'] = 0

            print(user[6])
            return render_template("home.html", user_details=user_details)
        else:
            error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/facility")
def facility():
    return  render_template("busfacility.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        rollno = request.form.get("rollno")
        password = request.form.get("password")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        busno = request.form.get("busnumber")  # Change 'busno' to 'busnumber'
        busstop = request.form.get("busstop")

        # Check if any required field is missing
        if None in [rollno, password, firstname, lastname, email, busno, busstop]:
            error_message = "One or more required fields are missing."
            return render_template("login.html", error=error_message)

        try:
            add_user(rollno, password, firstname, lastname, email, busno, busstop)
            session['rollno'] = rollno
            return redirect(url_for("home"))
        except Exception as e:
            error_message = "Error occurred while registering user: {}".format(str(e))
            return render_template("login.html", error=error_message)
    return render_template("login.html")

from flask import jsonify, request

# Function to update the status field in the user table
def update_user_status(rollno):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("UPDATE user SET stat = TRUE WHERE rollno = %s", (rollno,))
        cur.execute("UPDATE transactions SET status = TRUE WHERE rollno = %s", (rollno,))
        conn.commit()
        conn.close()
        print(f"User status updated for rollno {rollno}")
    except Exception as e:
        print("Error updating user status:", str(e))

@app.route("/payment_success", methods=["POST"])
def payment_success():
    print("payment_success called")
    try:
        data = request.get_json()
        payer_name = data.get("payerName")
        # Retrieve the rollno from the session
        rollno = session.get("rollno")
        # Process the success message and update the user status
        if rollno:
            update_user_status(rollno)
        print(f"Payment successful for {payer_name}")
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error processing payment success:", str(e))
        return jsonify({"status": "error"})


# Route for creating a new transaction ID and storing transaction details
@app.route("/create_transaction_id", methods=["GET"])
def create_transaction_id_endpoint():
    print("create_transaction_id_endpoint called")
    try:
        print("create_transaction_id_endpoint called in try block")
        # Retrieve rollno from session
        rollno = session.get("rollno")
        print(rollno)
        if not rollno:
            return jsonify({"error": "Roll number not found in session"}), 400

        # Generate transaction ID
        transaction_id = create_transaction_id(rollno)
        print("transction id is"+transaction_id)
        # Add transaction details to the database
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (transaction_id, rollno, amount, status) VALUES (%s, %s, %s, %s)",
                    (transaction_id, rollno, 10, False))  # Assuming amount is 10 and status is initially False
        conn.commit()
        conn.close()

        return jsonify({"transaction_id": transaction_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/home")
def home():
    rollno = session.get("rollno")
    if rollno:
        user_details = fetch_user_details(rollno)
        return render_template("home.html", user_details=user_details)
    else:
        # Redirect to login if the roll number is not available in the session
        return redirect(url_for("login"))
@app.route("/payment")
def payment():
    rollno = session.get("rollno")
    if rollno:
        user_details = fetch_user_details(rollno)
        session['stat'] = user_details[6]
        transaction_details = fetch_transaction_details(rollno)  # Fetch transaction details
        print(transaction_details)
        return render_template("payment.html", user_details=user_details, transaction_details=transaction_details)
    else:
        # Redirect to login if the roll number is not available in the session
        return redirect(url_for("login"))
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")



# Fetch students based on filtering options
def fetch_students(bus_number_filter=None, paid_status_filter=None):
    print("In fetch_students",bus_number_filter,paid_status_filter)
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    query = "SELECT * FROM user WHERE 1"
    params = []

    if bus_number_filter:
        query += " AND busnumber = %s"
        params.append(bus_number_filter)

    if paid_status_filter == "paid":
        query += " AND stat = 1"
    elif paid_status_filter == "not_paid":
        query += " AND stat = 0"

    cur.execute(query, params)
    students = cur.fetchall()

    conn.close()
    return students


# Fetch unique bus numbers from the users table
def fetch_bus_numbers():
    conn = connect_db()
    cur = conn.cursor()

    # Execute query to fetch unique bus numbers
    cur.execute("SELECT DISTINCT busnumber FROM user")
    bus_numbers = [row[0] for row in cur.fetchall()]  # Extracting the first element of each row
    print(bus_numbers)
    conn.close()
    return bus_numbers

# Function to handle the admin panel route
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Fetch bus numbers from the busdetails table
    bus_numbers = fetch_bus_numbers()

    # Fetch students data based on filtering options
    if request.method == "POST":
        bus_number_filter = request.form.get("bus_number")
        paid_status_filter = request.form.get("paid_status")
        print("deatils from the form ", bus_number_filter, paid_status_filter,end=" ")
        students = fetch_students(bus_number_filter, paid_status_filter)
    else:
        students = fetch_students()
        print("THE STUDENT LIST :",students)
    return render_template("admin.html", bus_numbers=bus_numbers, students=students)
@app.route("/student_get", methods=["GET", "POST"])
def student():
    # Fetch students data based on filtering options
    if request.method == "POST":
        rollno = request.form.get("roll_number")

        print(rollno)
        student = fetch_user_details(rollno)

    return render_template("student.html",student=student)
@app.route("/student")
def detail():
    return render_template('student.html')
if __name__ == "__main__":
    app.run(debug=True)
