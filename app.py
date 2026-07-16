from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, date, timedelta
import sqlite3, hashlib

app = Flask(__name__)
app.secret_key = "salon_secret_2026"
DB = "salon.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def hp(p): return hashlib.md5(p.encode()).hexdigest()
def today(): return date.today().strftime("%d/%m/%Y")
def now(): return datetime.now().strftime("%d/%m/%Y %H:%M")

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE,
        password TEXT, role TEXT DEFAULT 'customer', phone TEXT, joined TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY, name TEXT, category TEXT,
        duration INTEGER, price REAL, description TEXT,
        image_emoji TEXT, status TEXT DEFAULT 'Active')''')

    c.execute('''CREATE TABLE IF NOT EXISTS stylists (
        id TEXT PRIMARY KEY, name TEXT, specialization TEXT,
        phone TEXT, experience INTEGER, rating REAL,
        image_emoji TEXT, available_days TEXT, status TEXT DEFAULT 'Active')''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY, user_id TEXT, customer_name TEXT,
        customer_phone TEXT, stylist_id TEXT, stylist_name TEXT,
        service_id TEXT, service_name TEXT, service_price REAL,
        appt_date TEXT, appt_time TEXT, duration INTEGER,
        status TEXT DEFAULT 'Confirmed', notes TEXT, booked_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY, user_id TEXT, customer_name TEXT,
        stylist_id TEXT, stylist_name TEXT, appointment_id TEXT,
        rating INTEGER, comment TEXT, created_at TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY, name TEXT, category TEXT,
        price REAL, stock INTEGER, description TEXT,
        image_emoji TEXT, status TEXT DEFAULT 'Active')''')

    # Users
    if not c.execute("SELECT * FROM users WHERE email='owner@glamour.com'").fetchone():
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
            ("U001","Salon Owner","owner@glamour.com",hp("owner123"),"admin","9999999999",today()))
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
            ("U002","Alina Khan","alina@email.com",hp("user123"),"customer","9876543210",today()))
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
            ("U003","Rony Sharma","rony@email.com",hp("user123"),"customer","9812345678",today()))

    # Services
    if not c.execute("SELECT * FROM services").fetchone():
        services = [
            ("SV001","Hair Cut & Style","Hair",45,499,"Expert cut and blowout styling by our professionals","✂️","Active"),
            ("SV002","Full Hair Color","Hair",120,1999,"Full head color with premium brands like L'Oreal & Wella","🎨","Active"),
            ("SV003","Hair Highlights","Hair",90,2499,"Balayage, ombre or classic highlights","🌟","Active"),
            ("SV004","Keratin Treatment","Hair",180,3999,"Smooth, frizz-free hair for up to 3 months","💆","Active"),
            ("SV005","Facial - Classic","Skin",60,999,"Deep cleansing facial with steam and massage","🧖","Active"),
            ("SV006","Facial - Gold","Skin",75,1999,"Luxury gold facial for glowing skin","✨","Active"),
            ("SV007","Bridal Makeup","Makeup",120,7999,"Complete bridal look with premium products","👰","Active"),
            ("SV008","Party Makeup","Makeup",60,2999,"Glamorous party look for any occasion","💄","Active"),
            ("SV009","Manicure","Nails",45,599,"Classic manicure with nail polish of your choice","💅","Active"),
            ("SV010","Pedicure","Nails",60,799,"Relaxing pedicure with scrub and massage","🦶","Active"),
            ("SV011","Waxing - Full Body","Waxing",90,1499,"Complete body waxing with soft or hard wax","🌸","Active"),
            ("SV012","Threading & Cleanup","Eyebrows",30,299,"Eyebrow threading + face cleanup","👁️","Active"),
        ]
        c.executemany("INSERT INTO services VALUES (?,?,?,?,?,?,?,?)", services)

    # Stylists
    if not c.execute("SELECT * FROM stylists").fetchone():
        stylists = [
            ("ST001","Priya Kapoor","Hair Specialist",  "9811111111",8,4.9,"👩","Mon,Tue,Wed,Thu,Fri,Sat","Active"),
            ("ST002","Meena Nair",  "Makeup Artist",    "9822222222",5,4.8,"👩‍🎨","Mon,Wed,Thu,Fri,Sat,Sun","Active"),
            ("ST003","Reena Singh", "Skin Care Expert", "9833333333",6,4.7,"🧑‍⚕️","Tue,Wed,Thu,Fri,Sat","Active"),
            ("ST004","Kavya Patel", "Nail Technician",  "9844444444",3,4.6,"💅","Mon,Tue,Thu,Fri,Sat,Sun","Active"),
            ("ST005","Anjali Verma","Multi Specialist",  "9855555555",10,4.9,"👩‍💼","Mon,Tue,Wed,Thu,Fri","Active"),
        ]
        c.executemany("INSERT INTO stylists VALUES (?,?,?,?,?,?,?,?,?)", stylists)

    # Products
    if not c.execute("SELECT * FROM products").fetchone():
        products = [
            ("P001","L'Oreal Shampoo","Hair Care",450,25,"Nourishing shampoo for all hair types","🧴","Active"),
            ("P002","Keratin Serum","Hair Care",999,12,"Frizz control and shine serum","✨","Active"),
            ("P003","Rose Face Cream","Skin Care",699,18,"Daily moisturizer with rose extract","🌹","Active"),
            ("P004","SPF 50 Sunscreen","Skin Care",549,30,"Broad spectrum UV protection","☀️","Active"),
            ("P005","Nail Polish Set","Nails",399,20,"Set of 6 trendy colors","💅","Active"),
            ("P006","Wax Kit","Waxing",299,15,"At-home waxing kit","🌸","Active"),
        ]
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", products)

    # Sample appointments
    if not c.execute("SELECT * FROM appointments").fetchone():
        d0 = date.today()
        appts = [
            ("A001","U002","Alina Khan","9876543210","ST001","Priya Kapoor","SV001","Hair Cut & Style",499,
             d0.strftime("%d/%m/%Y"),"10:00 AM",45,"Confirmed","Regular trim please",now()),
            ("A002","U003","Rony Sharma","9812345678","ST002","Meena Nair","SV008","Party Makeup",2999,
             d0.strftime("%d/%m/%Y"),"12:00 PM",60,"Confirmed","Natural look preferred",now()),
            ("A003","U002","Alina Khan","9876543210","ST003","Reena Singh","SV005","Facial - Classic",999,
             (d0+timedelta(days=1)).strftime("%d/%m/%Y"),"11:00 AM",60,"Confirmed","",now()),
            ("A004","U003","Rony Sharma","9812345678","ST001","Priya Kapoor","SV002","Full Hair Color",1999,
             (d0+timedelta(days=2)).strftime("%d/%m/%Y"),"02:00 PM",120,"Confirmed","Dark brown color",now()),
            ("A005","U002","Alina Khan","9876543210","ST004","Kavya Patel","SV009","Manicure",599,
             (d0-timedelta(days=1)).strftime("%d/%m/%Y"),"03:00 PM",45,"Completed","",now()),
        ]
        c.executemany("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", appts)

        reviews = [
            ("R001","U002","Alina Khan","ST001","Priya Kapoor","A005",5,"Amazing work! Best haircut I've ever had. Priya really understands what you want!",now()),
            ("R002","U003","Rony Sharma","ST002","Meena Nair","A002",5,"Meena is an absolute artist! My makeup was perfect for the party.",now()),
        ]
        c.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?,?)", reviews)

    conn.commit()
    conn.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error":"Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index(): return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        d = request.get_json()
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
            (d["email"], hp(d["password"]))).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            return jsonify({"ok":True})
        return jsonify({"ok":False,"msg":"Invalid credentials!"})
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    d = request.get_json()
    if not d.get("name") or not d.get("email") or not d.get("password"):
        return jsonify({"ok":False,"msg":"Fill all fields!"})
    conn = get_db()
    if conn.execute("SELECT * FROM users WHERE email=?", (d["email"],)).fetchone():
        conn.close(); return jsonify({"ok":False,"msg":"Email already registered!"})
    uid = "U"+str(int(datetime.now().timestamp()))
    conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
        (uid,d["name"],d["email"],hp(d["password"]),"customer",d.get("phone",""),today()))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/api/session")
def get_session():
    if "user_id" in session:
        return jsonify({"logged_in":True,"name":session["user_name"],"role":session["user_role"],"id":session["user_id"]})
    return jsonify({"logged_in":False})

@app.route("/api/dashboard")
@login_required
def dashboard():
    conn = get_db()
    today_appts  = conn.execute("SELECT COUNT(*) FROM appointments WHERE appt_date=? AND status='Confirmed'",(today(),)).fetchone()[0]
    total_revenue= conn.execute("SELECT COALESCE(SUM(service_price),0) FROM appointments WHERE status='Completed'").fetchone()[0]
    total_clients= conn.execute("SELECT COUNT(DISTINCT user_id) FROM appointments").fetchone()[0]
    pending      = conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Confirmed'").fetchone()[0]
    todays_appts = [dict(r) for r in conn.execute("SELECT * FROM appointments WHERE appt_date=? ORDER BY appt_time",(today(),)).fetchall()]
    upcoming     = [dict(r) for r in conn.execute("SELECT * FROM appointments WHERE status='Confirmed' ORDER BY appt_date,appt_time LIMIT 5").fetchall()]
    my_appts     = [dict(r) for r in conn.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY rowid DESC LIMIT 5",(session["user_id"],)).fetchall()]
    top_services = [dict(r) for r in conn.execute("SELECT service_name, COUNT(*) as cnt FROM appointments GROUP BY service_name ORDER BY cnt DESC LIMIT 5").fetchall()]
    conn.close()
    return jsonify({"today_appts":today_appts,"total_revenue":total_revenue,"total_clients":total_clients,
        "pending":pending,"todays_appts":todays_appts,"upcoming":upcoming,"my_appts":my_appts,"top_services":top_services})

@app.route("/api/services")
@login_required
def get_services():
    cat = request.args.get("category","All")
    conn = get_db()
    if cat=="All":
        svcs = [dict(r) for r in conn.execute("SELECT * FROM services WHERE status='Active'").fetchall()]
    else:
        svcs = [dict(r) for r in conn.execute("SELECT * FROM services WHERE status='Active' AND category=?",(cat,)).fetchall()]
    conn.close()
    return jsonify(svcs)

@app.route("/api/services/all")
@login_required
def get_all_services():
    conn = get_db()
    svcs = [dict(r) for r in conn.execute("SELECT * FROM services").fetchall()]
    conn.close()
    return jsonify(svcs)

@app.route("/api/services", methods=["POST"])
@login_required
def add_service():
    if session["user_role"]!="admin": return jsonify({"error":"Forbidden"}),403
    d = request.get_json()
    sid = "SV"+str(int(datetime.now().timestamp()))
    conn = get_db()
    conn.execute("INSERT INTO services VALUES (?,?,?,?,?,?,?,?)",
        (sid,d["name"],d["category"],int(d["duration"]),float(d["price"]),
         d.get("description",""),d.get("image_emoji","💅"),"Active"))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/services/<sid>", methods=["PUT"])
@login_required
def update_service(sid):
    if session["user_role"]!="admin": return jsonify({"error":"Forbidden"}),403
    d = request.get_json()
    conn = get_db()
    conn.execute("UPDATE services SET name=?,category=?,duration=?,price=?,description=?,image_emoji=?,status=? WHERE id=?",
        (d["name"],d["category"],int(d["duration"]),float(d["price"]),
         d.get("description",""),d.get("image_emoji","💅"),d.get("status","Active"),sid))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/services/<sid>", methods=["DELETE"])
@login_required
def delete_service(sid):
    if session["user_role"]!="admin": return jsonify({"error":"Forbidden"}),403
    conn = get_db()
    conn.execute("DELETE FROM services WHERE id=?",(sid,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/stylists")
@login_required
def get_stylists():
    conn = get_db()
    stylists = [dict(r) for r in conn.execute("SELECT * FROM stylists WHERE status='Active'").fetchall()]
    conn.close()
    return jsonify(stylists)

@app.route("/api/stylists/all")
@login_required
def get_all_stylists():
    conn = get_db()
    stylists = [dict(r) for r in conn.execute("SELECT * FROM stylists").fetchall()]
    conn.close()
    return jsonify(stylists)

@app.route("/api/appointments", methods=["GET"])
@login_required
def get_appointments():
    conn = get_db()
    if session["user_role"]=="admin":
        appts = [dict(r) for r in conn.execute("SELECT * FROM appointments ORDER BY appt_date DESC,appt_time").fetchall()]
    else:
        appts = [dict(r) for r in conn.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY rowid DESC",(session["user_id"],)).fetchall()]
    conn.close()
    return jsonify(appts)

@app.route("/api/appointments", methods=["POST"])
@login_required
def book_appointment():
    d = request.get_json()
    conn = get_db()
    service = conn.execute("SELECT * FROM services WHERE id=?",(d["service_id"],)).fetchone()
    stylist = conn.execute("SELECT * FROM stylists WHERE id=?",(d["stylist_id"],)).fetchone()
    if not service or not stylist:
        conn.close(); return jsonify({"ok":False,"msg":"Service or stylist not found!"})
    # Check conflict
    conflict = conn.execute(
        "SELECT * FROM appointments WHERE stylist_id=? AND appt_date=? AND appt_time=? AND status='Confirmed'",
        (d["stylist_id"],d["appt_date"],d["appt_time"])).fetchone()
    if conflict:
        conn.close(); return jsonify({"ok":False,"msg":"This slot is already booked! Please choose another time."})
    aid = "A"+str(int(datetime.now().timestamp()))
    conn.execute("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid,session["user_id"],session["user_name"],d.get("phone",""),
         d["stylist_id"],stylist["name"],d["service_id"],service["name"],
         service["price"],d["appt_date"],d["appt_time"],service["duration"],
         "Confirmed",d.get("notes",""),now()))
    conn.commit(); conn.close()
    return jsonify({"ok":True,"booking_id":aid})

@app.route("/api/appointments/<aid>/status", methods=["PUT"])
@login_required
def update_appointment(aid):
    d = request.get_json()
    conn = get_db()
    conn.execute("UPDATE appointments SET status=? WHERE id=?",(d["status"],aid))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/appointments/<aid>/cancel", methods=["PUT"])
@login_required
def cancel_appointment(aid):
    conn = get_db()
    appt = conn.execute("SELECT * FROM appointments WHERE id=?",(aid,)).fetchone()
    if not appt: conn.close(); return jsonify({"ok":False})
    if appt["user_id"]!=session["user_id"] and session["user_role"]!="admin":
        conn.close(); return jsonify({"error":"Forbidden"}),403
    conn.execute("UPDATE appointments SET status='Cancelled' WHERE id=?",(aid,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/reviews", methods=["GET"])
@login_required
def get_reviews():
    conn = get_db()
    reviews = [dict(r) for r in conn.execute("SELECT * FROM reviews ORDER BY rowid DESC").fetchall()]
    conn.close()
    return jsonify(reviews)

@app.route("/api/reviews", methods=["POST"])
@login_required
def add_review():
    d = request.get_json()
    rid = "R"+str(int(datetime.now().timestamp()))
    conn = get_db()
    conn.execute("INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?,?)",
        (rid,session["user_id"],session["user_name"],d["stylist_id"],d["stylist_name"],
         d.get("appointment_id",""),int(d["rating"]),d["comment"],now()))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/products")
@login_required
def get_products():
    conn = get_db()
    products = [dict(r) for r in conn.execute("SELECT * FROM products WHERE status='Active'").fetchall()]
    conn.close()
    return jsonify(products)

@app.route("/api/admin/stats")
@login_required
def admin_stats():
    if session["user_role"]!="admin": return jsonify({"error":"Forbidden"}),403
    conn = get_db()
    stats = {
        "total_appointments": conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        "completed":          conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Completed'").fetchone()[0],
        "revenue":            conn.execute("SELECT COALESCE(SUM(service_price),0) FROM appointments WHERE status='Completed'").fetchone()[0],
        "total_clients":      conn.execute("SELECT COUNT(*) FROM users WHERE role='customer'").fetchone()[0],
        "all_appointments":   [dict(r) for r in conn.execute("SELECT * FROM appointments ORDER BY appt_date DESC,appt_time").fetchall()],
        "all_stylists":       [dict(r) for r in conn.execute("SELECT * FROM stylists").fetchall()],
        "all_services":       [dict(r) for r in conn.execute("SELECT * FROM services").fetchall()],
    }
    conn.close()
    return jsonify(stats)

if __name__ == "__main__":
    init_db()
    print("="*45)
    print("   GLAMOUR SALON - Appointment System")
    print("="*45)
    print("   Open: http://localhost:5000")
    print("   Owner:    owner@glamour.com / owner123")
    print("   Customer: alina@email.com   / user123")
    print("="*45)
    app.run(debug=True)
