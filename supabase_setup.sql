-- ============================================================
--  SUPABASE SETUP — Cultural Trip Distributed DB Demo
--  Run this in your Supabase SQL Editor
-- ============================================================

-- ── HORIZONTAL FRAGMENTATION ─────────────────────────────────
-- trips_north  →  only North region trips
-- trips_east   →  only East region trips
-- (Simulates: CREATE TABLE Trips_North AS SELECT * WHERE Region='North')

CREATE TABLE IF NOT EXISTS trips_north (
    tripid    SERIAL PRIMARY KEY,
    region    TEXT DEFAULT 'North',
    title     TEXT,
    startdate DATE,
    enddate   DATE
);

CREATE TABLE IF NOT EXISTS trips_east (
    tripid    SERIAL PRIMARY KEY,
    region    TEXT DEFAULT 'East',
    title     TEXT,
    startdate DATE,
    enddate   DATE
);

-- ── VERTICAL FRAGMENTATION ───────────────────────────────────
-- tourist_basic   → public info (TouristID, Name)
-- tourist_contact → sensitive info (TouristID, Nationality, Contact)

CREATE TABLE IF NOT EXISTS tourist_basic (
    touristid SERIAL PRIMARY KEY,
    name      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tourist_contact (
    touristid   INT PRIMARY KEY REFERENCES tourist_basic(touristid),
    nationality TEXT,
    contact     TEXT
);

-- ── MIXED FRAGMENTATION ──────────────────────────────────────
-- bookings_north / bookings_east → horizontal split by region
-- booking_amount                 → vertical split (sensitive financial data)

CREATE TABLE IF NOT EXISTS bookings_north (
    bookingid INT PRIMARY KEY,
    touristid INT REFERENCES tourist_basic(touristid),
    tripid    INT REFERENCES trips_north(tripid)
);

CREATE TABLE IF NOT EXISTS bookings_east (
    bookingid INT PRIMARY KEY,
    touristid INT REFERENCES tourist_basic(touristid),
    tripid    INT REFERENCES trips_east(tripid)
);

CREATE TABLE IF NOT EXISTS booking_amount (
    bookingid INT PRIMARY KEY,
    amount    NUMERIC
);

-- ── SUPPORTING TABLES ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS guides (
    guideid   SERIAL PRIMARY KEY,
    name      TEXT,
    region    TEXT,
    languages TEXT
);

CREATE TABLE IF NOT EXISTS cultural_events (
    eventid SERIAL PRIMARY KEY,
    region  TEXT,
    name    TEXT,
    date    DATE,
    type    TEXT
);

CREATE TABLE IF NOT EXISTS accommodations (
    hotelid SERIAL PRIMARY KEY,
    name    TEXT,
    region  TEXT,
    rating  NUMERIC
);

-- ═══════════════════════════════════════════════════════════════
--  SAMPLE DATA
-- ═══════════════════════════════════════════════════════════════

-- Tourists (public info)
INSERT INTO tourist_basic (touristid, name) VALUES
    (1, 'Ahmed Ben Mohamed'),
    (2, 'Mansouri Leila'),
    (3, 'Karim Slimani')
ON CONFLICT DO NOTHING;

-- Tourists (sensitive info — stored separately)
INSERT INTO tourist_contact (touristid, nationality, contact) VALUES
    (1, 'Algerian',  '0550123456'),
    (2, 'Tunisian',  '002169876543'),
    (3, 'Algerian',  '0661987654')
ON CONFLICT DO NOTHING;

-- Trips — North fragment
INSERT INTO trips_north (tripid, region, title, startdate, enddate) VALUES
    (101, 'North', 'Algiers Heritage Tour',    '2025-06-01', '2025-06-10'),
    (102, 'North', 'Tipaza Roman Ruins',       '2025-07-01', '2025-07-07'),
    (103, 'North', 'Kabylie Mountain Escape',  '2025-08-10', '2025-08-17')
ON CONFLICT DO NOTHING;

-- Trips — East fragment
INSERT INTO trips_east (tripid, region, title, startdate, enddate) VALUES
    (201, 'East', 'Timgad Festival Experience', '2025-08-01', '2025-08-10'),
    (202, 'East', 'Aurès Mountains Trek',        '2025-09-05', '2025-09-12'),
    (203, 'East', 'Setif Plateau Discovery',     '2025-10-01', '2025-10-06')
ON CONFLICT DO NOTHING;

-- Bookings (mixed fragmentation)
INSERT INTO bookings_north (bookingid, touristid, tripid) VALUES
    (301, 1, 101),
    (302, 3, 102)
ON CONFLICT DO NOTHING;

INSERT INTO bookings_east (bookingid, touristid, tripid) VALUES
    (401, 2, 201),
    (402, 1, 202)
ON CONFLICT DO NOTHING;

-- Amounts stored separately (vertical split)
INSERT INTO booking_amount (bookingid, amount) VALUES
    (301, 80000),
    (302, 65000),
    (401, 75000),
    (402, 90000)
ON CONFLICT DO NOTHING;

-- Guides
INSERT INTO guides (name, region, languages) VALUES
    ('Nasser Samir',   'North', 'Arabic, French'),
    ('Youcef Meziani', 'East',  'Arabic, French, Tamazight'),
    ('Sara Belkacem',  'North', 'Arabic, English, French')
ON CONFLICT DO NOTHING;

-- Cultural Events
INSERT INTO cultural_events (region, name, date, type) VALUES
    ('East',  'Timgad International Music Festival', '2025-08-05', 'Music'),
    ('North', 'Algiers Cultural Week',               '2025-06-05', 'Culture'),
    ('East',  'Aurès Photography Exhibition',        '2025-09-08', 'Art'),
    ('North', 'Tipaza Archaeological Day',           '2025-07-04', 'History')
ON CONFLICT DO NOTHING;

-- Accommodations
INSERT INTO accommodations (name, region, rating) VALUES
    ('El Djazair Hotel',   'North', 5),
    ('Tipaza Seaside Inn', 'North', 4),
    ('Timgad Lodge',       'East',  4),
    ('Aurès Guesthouse',   'East',  3)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════
--  ENABLE ROW LEVEL SECURITY (recommended for Supabase)
-- ═══════════════════════════════════════════════════════════════
ALTER TABLE trips_north    ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips_east     ENABLE ROW LEVEL SECURITY;
ALTER TABLE tourist_basic  ENABLE ROW LEVEL SECURITY;
ALTER TABLE tourist_contact ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings_north ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings_east  ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_amount ENABLE ROW LEVEL SECURITY;
ALTER TABLE cultural_events ENABLE ROW LEVEL SECURITY;

-- Allow all access via service role key (for backend use)
CREATE POLICY "service_role_all" ON trips_north     FOR ALL USING (true);
CREATE POLICY "service_role_all" ON trips_east      FOR ALL USING (true);
CREATE POLICY "service_role_all" ON tourist_basic   FOR ALL USING (true);
CREATE POLICY "service_role_all" ON tourist_contact FOR ALL USING (true);
CREATE POLICY "service_role_all" ON bookings_north  FOR ALL USING (true);
CREATE POLICY "service_role_all" ON bookings_east   FOR ALL USING (true);
CREATE POLICY "service_role_all" ON booking_amount  FOR ALL USING (true);
CREATE POLICY "service_role_all" ON cultural_events FOR ALL USING (true);
CREATE POLICY "service_role_all" ON guides          FOR ALL USING (true);
CREATE POLICY "service_role_all" ON accommodations  FOR ALL USING (true);