import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load environment variables locally
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# 2. Securely fetch and clean credentials
# Using .strip() handles hidden spaces that cause "Invalid URL" errors
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables!")

# 3. Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- NORTH AGENCY ROUTES ---
@app.route("/north")
def north():
    trips    = supabase.table("trips_north").select("*").execute().data or []
    bookings = supabase.table("bookings_north").select("*").execute().data or []
    tourists = supabase.table("tourist_basic").select("*").execute().data or []
    events   = supabase.table("cultural_events").select("*").eq("region", "North").execute().data or []
    return render_template("north.html", 
                           trips=trips, bookings=bookings, 
                           tourists=tourists, events=events)

@app.route("/north/add-trip", methods=["POST"])
def north_add_trip():
    data = {
        "tripid":    request.form.get("tripid"),
        "region":    "North",
        "startdate": request.form.get("startdate"),
        "enddate":   request.form.get("enddate"),
        "title":     request.form.get("title"),
    }
    supabase.table("trips_north").insert(data).execute()
    return redirect(url_for("north"))

@app.route("/north/add-booking", methods=["POST"])
def north_add_booking():
    info = {
        "bookingid":  request.form.get("bookingid"),
        "touristid":  request.form.get("touristid"),
        "tripid":     request.form.get("tripid"),
    }
    amount = {
        "bookingid": request.form.get("bookingid"),
        "amount":    request.form.get("amount"),
    }
    supabase.table("bookings_north").insert(info).execute()
    supabase.table("booking_amount").insert(amount).execute()
    return redirect(url_for("north"))

# --- EAST AGENCY ROUTES ---
@app.route("/east")
def east():
    trips    = supabase.table("trips_east").select("*").execute().data or []
    bookings = supabase.table("bookings_east").select("*").execute().data or []
    tourists = supabase.table("tourist_basic").select("*").execute().data or []
    events   = supabase.table("cultural_events").select("*").eq("region", "East").execute().data or []
    return render_template("east.html", 
                           trips=trips, bookings=bookings, 
                           tourists=tourists, events=events)

@app.route("/east/add-trip", methods=["POST"])
def east_add_trip():
    data = {
        "tripid":    request.form.get("tripid"),
        "region":    "East",
        "startdate": request.form.get("startdate"),
        "enddate":   request.form.get("enddate"),
        "title":     request.form.get("title"),
    }
    supabase.table("trips_east").insert(data).execute()
    return redirect(url_for("east"))

@app.route("/east/add-booking", methods=["POST"])
def east_add_booking():
    info = {
        "bookingid":  request.form.get("bookingid"),
        "touristid":  request.form.get("touristid"),
        "tripid":     request.form.get("tripid"),
    }
    amount = {
        "bookingid": request.form.get("bookingid"),
        "amount":    request.form.get("amount"),
    }
    supabase.table("bookings_east").insert(info).execute()
    supabase.table("booking_amount").insert(amount).execute()
    return redirect(url_for("east"))

# --- GLOBAL VIEW ---
@app.route("/")
@app.route("/global")
def global_view():
    # Fetch all data with safety fallbacks to empty lists
    n_trips = supabase.table("trips_north").select("*").execute().data or []
    e_trips = supabase.table("trips_east").select("*").execute().data or []
    all_trips = n_trips + e_trips

    n_bookings = supabase.table("bookings_north").select("*").execute().data or []
    e_bookings = supabase.table("bookings_east").select("*").execute().data or []
    all_bookings = n_bookings + e_bookings

    all_amounts = supabase.table("booking_amount").select("*").execute().data or []
    tourists    = supabase.table("tourist_basic").select("*").execute().data or []
    contacts    = supabase.table("tourist_contact").select("*").execute().data or []
    events      = supabase.table("cultural_events").select("*").execute().data or []

    # Map contacts and amounts for easy lookup
    contact_map = {c["touristid"]: c for c in contacts}
    amount_map = {a["bookingid"]: a["amount"] for a in all_amounts}

    full_tourists = []
    for t in tourists:
        merged = {**t, **contact_map.get(t["touristid"], {})}
        full_tourists.append(merged)

    for b in all_bookings:
        b["amount"] = amount_map.get(b["bookingid"], "N/A")

    return render_template("global.html",
                           all_trips=all_trips,
                           all_bookings=all_bookings,
                           full_tourists=full_tourists,
                           events=events,
                           north_count=len(n_trips),
                           east_count=len(e_trips))

@app.route("/api/all-trips")
def api_all_trips():
    n = supabase.table("trips_north").select("*").execute().data or []
    e = supabase.table("trips_east").select("*").execute().data or []
    return jsonify({"north": n, "east": e, "total": n + e})

if __name__ == "__main__":
    # Railway assigns a port via environment variable
    port = int(os.environ.get("PORT", 5000))
    # In production, debug should usually be False, but keep it True for now to see errors
    app.run(host="0.0.0.0", port=port, debug=True)