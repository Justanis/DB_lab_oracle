from flask import Flask, render_template, request, redirect
import oracledb

app = Flask(__name__)

# --- DB CONNECTION ---
DB_USER = "SYS"
DB_PASS = "anisdb"
DB_HOST = "localhost"
DB_PORT = "1522"
DB_SID  = "free"

def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASS,
        dsn=f"{DB_HOST}:{DB_PORT}/{DB_SID}",
        mode=oracledb.AUTH_MODE_SYSDBA
    )
# --- HOME: show all customers ---
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT person_id, full_name, email, phone_number FROM Customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template("index.html", customers=customers)

# --- ADD CUSTOMER ---
@app.route("/add", methods=["POST"])
def add_customer():
    pid   = request.form["person_id"]
    # Non-negative check
    if int(pid) <= 0:
        return "Error: ID must be a positive number!", 400
    name  = request.form["full_name"]
    email = request.form["email"]
    phone = request.form["phone_number"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Customers VALUES (
            Customer_t(:1, :2, :3, :4)
        )
    """, [pid, name, email, phone])
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)