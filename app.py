import os
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Setup
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# 2. Cleaning Function
def clean_input(val):
    if not val: return ""
    # Extract URL from Markdown [text](url) if present
    if '](' in val:
        val = val.split('](')[1].split(')')[0]
    # Remove brackets, parentheses, quotes, and whitespace
    val = re.sub(r'[\[\]\(\"\']', '', val).strip()
    # Remove trailing slashes and redundant paths
    if val.endswith('/'): val = val[:-1]
    if "/rest/v1" in val: val = val.split("/rest/v1")[0]
    return val

# 3. Clean and THEN Initialize (Must be in this order)
raw_url = os.environ.get("SUPABASE_URL", "")
raw_key = os.environ.get("SUPABASE_KEY", "")

url = clean_input(raw_url)
key = clean_input(raw_key)

if not url.startswith("http"):
    raise ValueError(f"Invalid URL detected: {url}")

# Initialize the client using the CLEANED variables
supabase: Client = create_client(url, key)

# --- ROUTES ---

@app.route("/")
@app.route("/global")
def global_view():
    n_trips = supabase.table("trips_north").select("*").execute().data or []
    e_trips = supabase.table("trips_east").select("*").execute().data or []
    n_bookings = supabase.table("bookings_north").select("*").execute().data or []
    e_bookings = supabase.table("bookings_east").select("*").execute().data or []
    all_amounts = supabase.table("booking_amount").select("*").execute().data or []
    tourists = supabase.table("tourist_basic").select("*").execute().data or []
    contacts = supabase.table("tourist_contact").select("*").execute().data or []
    events = supabase.table("cultural_events").select("*").execute().data or []

    all_trips = n_trips + e_trips
    all_bookings = n_bookings + e_bookings
    contact_map = {c["touristid"]: c for c in contacts}
    amount_map = {a["bookingid"]: a["amount"] for a in all_amounts}

    full_tourists = [{**t, **contact_map.get(t["touristid"], {})} for t in tourists]
    for b in all_bookings:
        b["amount"] = amount_map.get(b["bookingid"], "N/A")

    return render_template("global.html", all_trips=all_trips, all_bookings=all_bookings, 
                           full_tourists=full_tourists, events=events, 
                           north_count=len(n_trips), east_count=len(e_trips))

@app.route("/north")
def north():
    trips = supabase.table("trips_north").select("*").execute().data or []
    bookings = supabase.table("bookings_north").select("*").execute().data or []
    tourists = supabase.table("tourist_basic").select("*").execute().data or []
    events = supabase.table("cultural_events").select("*").eq("region", "North").execute().data or []
    return render_template("north.html", trips=trips, bookings=bookings, tourists=tourists, events=events)

@app.route("/north/add-trip", methods=["POST"])
def north_add_trip():
    raw_data = {
        "tripid": request.form.get("tripid"),
        "region": "North",
        "startdate": request.form.get("startdate"),
        "enddate": request.form.get("enddate"),
        "title": request.form.get("title"),
    }
    # Filter out empty strings to allow DB defaults (like SERIAL) or handle NULLs properly
    data = {k: v for k, v in raw_data.items() if v}
    supabase.table("trips_north").insert(data).execute()
    return redirect(url_for("north"))

@app.route("/east")
def east():
    trips = supabase.table("trips_east").select("*").execute().data or []
    bookings = supabase.table("bookings_east").select("*").execute().data or []
    tourists = supabase.table("tourist_basic").select("*").execute().data or []
    events = supabase.table("cultural_events").select("*").eq("region", "East").execute().data or []
    return render_template("east.html", trips=trips, bookings=bookings, tourists=tourists, events=events)

@app.route("/east/add-trip", methods=["POST"])
def east_add_trip():
    raw_data = {
        "tripid": request.form.get("tripid"),
        "region": "East",
        "startdate": request.form.get("startdate"),
        "enddate": request.form.get("enddate"),
        "title": request.form.get("title"),
    }
    # Filter out empty strings to allow DB defaults (like SERIAL) or handle NULLs properly
    data = {k: v for k, v in raw_data.items() if v}
    supabase.table("trips_east").insert(data).execute()
    return redirect(url_for("east"))

@app.route("/api/all-trips")
def api_all_trips():
    n = supabase.table("trips_north").select("*").execute().data or []
    e = supabase.table("trips_east").select("*").execute().data or []
    return jsonify({"north": n, "east": e, "total": n + e})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)