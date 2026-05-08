import os
from dj_database_url import key
from django import urls
from flask import Flask, render_template, request, jsonify, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv

# Only load dotenv if we are running locally
if os.path.exists(".env"):
    load_dotenv()

app = Flask(__name__)

# Use .strip() to remove any accidental hidden spaces or newlines
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()

if not url or not key:
    raise ValueError("Credentials missing! Check Railway Variables.")

supabase: Client = create_client(url, key)

# North agency routes
@app.route("/north")
def north():
    trips     = supabase.table("trips_north").select("*").execute().data or []
    bookings  = supabase.table("bookings_north").select("*").execute().data or []
    tourists  = supabase.table("tourist_basic").select("*").execute().data or []
    events    = supabase.table("cultural_events").select("*").eq("region", "North").execute().data
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

# East agency routes
@app.route("/east")
def east():
    trips     = supabase.table("trips_east").select("*").execute().data or []
    bookings  = supabase.table("bookings_east").select("*").execute().data or []
    tourists  = supabase.table("tourist_basic").select("*").execute().data or []
    events    = supabase.table("cultural_events").select("*").eq("region", "East").execute().data
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

# Global view
@app.route("/")
@app.route("/global")
def global_view():
    north_trips = supabase.table("trips_north").select("*").execute().data or []
    east_trips  = supabase.table("trips_east").select("*").execute().data or []
    all_trips   = north_trips + east_trips

    north_bookings = supabase.table("bookings_north").select("*").execute().data or []
    east_bookings  = supabase.table("bookings_east").select("*").execute().data or []
    all_bookings   = north_bookings + east_bookings

    all_amounts = supabase.table("booking_amount").select("*").execute().data or []
    tourists    = supabase.table("tourist_basic").select("*").execute().data or []
    contacts    = supabase.table("tourist_contact").select("*").execute().data or []
    events      = supabase.table("cultural_events").select("*").execute().data or []

    contact_map = {c["touristid"]: c for c in contacts}
    full_tourists = []
    for t in tourists:
        merged = {**t, **contact_map.get(t["touristid"], {})}
        full_tourists.append(merged)

    amount_map = {a["bookingid"]: a["amount"] for a in all_amounts}
    for b in all_bookings:
        b["amount"] = amount_map.get(b["bookingid"], "N/A")

    return render_template("global.html",
                           all_trips=all_trips,
                           all_bookings=all_bookings,
                           full_tourists=full_tourists,
                           events=events,
                           north_count=len(north_trips),
                           east_count=len(east_trips))

@app.route("/api/all-trips")
def api_all_trips():
    north = supabase.table("trips_north").select("*").execute().data or []
    east  = supabase.table("trips_east").select("*").execute().data or []
    return jsonify({"north": north, "east": east, "total": north + east})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)