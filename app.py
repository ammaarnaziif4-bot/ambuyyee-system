# ============================================================
# AMBUYEE SCHOOL ONLINE STUDENT REGISTRATION SYSTEM
# Mana Barumsaa Sadarkaa 2ffaa Ambuyyee
# Version 1.0
#
# Backend: Flask
# Database: SQLite
# Languages: Afaan Oromoo / Amharic / English
# ============================================================

import os
import re
import sqlite3
import secrets
import hashlib
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
    render_template_string,
    abort
)
from werkzeug.utils import secure_filename


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, "ambuyyee.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# Production keessatti SECRET_KEY kana environment variable irraa
# kennuun gaarii dha.
app.secret_key = os.environ.get(
    "AMBUYEE_SECRET_KEY",
    "CHANGE-THIS-SECRET-KEY-BEFORE-PRODUCTION"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "pdf"
}

GRADES = ["9", "10", "11", "12"]

CLASSES = ["A", "B", "C", "D", "E", "F"]

GENDERS = [
    "Male",
    "Female"
]

STREAMS = [
    "Natural Science",
    "Social Science"
]


# ============================================================
# TRANSLATIONS
# ============================================================

LANG = {

    "om": {

        "site_name": "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee",
        "short_name": "AMB UYYEE SCHOOL",

        "home": "Fuula Jalqabaa",
        "register": "Galmee Barataa",
        "student_login": "Seensa Barataa",
        "teacher_login": "Seensa Barsiisaa",
        "dashboard": "Dashboard",
        "logout": "Ba'i",

        "hero_title": "Galmee Barattootaa Online",
        "hero_text": (
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee keessatti "
            "galmee barattootaa karaa online salphaa fi sirrii ta'een raawwadhu."
        ),

        "start_registration": "Galmee Jalqabi",
        "student_portal": "Student Portal",
        "teacher_portal": "Teacher / Admin Portal",

        "about_title": "Waa'ee Sirnichaa",
        "about_text": (
            "Sirni kun barattoonni mana barumsaa ala jiran "
            "odeeffannoo fi sanadoota barbaachisan online galchanii "
            "galmee isaanii hordofan akka danda'an qophaa'e."
        ),

        "features": "Tajaajiloota Sirnichaa",
        "online_registration": "Galmee Online",
        "secure_documents": "Sanadoota Eegumsa Qaban",
        "student_tracking": "Hordoffii Galmee",
        "teacher_verification": "Mirkaneessa Barsiisaa",
        "statistics": "Lakkoofsa fi Statistics",

        "full_name": "Maqaa Guutuu",
        "phone": "Lakkoofsa Bilbila",
        "national_id": "National ID",
        "age": "Umurii",
        "gender": "Saala",
        "male": "Dhiira",
        "female": "Dubartii",

        "kebele": "Kebele / Ganda",
        "zone": "Zone / Zoonii",
        "grade": "Kutaa Barnootaa",
        "class_name": "Class",
        "stream": "Stream",

        "school_card_front": "Kaardii Mana Barumsaa - Fuula Duraa",
        "school_card_back": "Kaardii Mana Barumsaa - Fuula Duubaa",
        "face_photo": "Suuraa Fuula Barataa",

        "ministry_document": "Ministry Document",
        "payment_screenshot": "Ragaa Kaffaltii",

        "grade9_fee": "Kaffaltii Grade 9: 500 Birr",

        "student_code": "Koodii Barataa",
        "choose_code": "Koodii Mata Keetii Uumi",
        "confirm_code": "Koodii Mirkaneessi",

        "submit": "Galchi / Submit",
        "save": "Olkaa'i",
        "search": "Barbaadi",
        "filter": "Filter",

        "pending": "Eeggataa",
        "approved": "Fudhatame",
        "rejected": "Didame",
        "returned": "Deebi'e",

        "boys": "Dhiira",
        "girls": "Dubartii",
        "total": "Waliigala",

        "status": "Haala Galmee",
        "message": "Ergaa",
        "send_message": "Ergaa Ergi",

        "approve": "Approve",
        "reject": "Reject",
        "return": "Deebisi",

        "login": "Seeni",
        "password": "Password",
        "admin_code": "Koodii Barsiisaa",

        "student_details": "Odeeffannoo Barataa",
        "registration_date": "Guyyaa Galmee",

        "success_registration": (
            "Baga gammaddan! Galmeen keessan milkaa'eera."
        ),

        "invalid_login": "Bilbila ykn koodiin sirrii miti.",
        "required": "Kutaan kun dirqama.",
        "files_required": "Sanadoonni barbaachisan guutuu ta'uu qabu.",
        "code_mismatch": "Koodiin lamaan wal hin simne.",
        "invalid_file": "Faayiliin kun hin hayyamamu.",
        "saved": "Odeeffannoon milkaa'inaan olkaa'ameera.",

        "login_instruction": (
            "Lakkoofsa bilbila fi koodii ati yeroo galmee uumte fayyadami."
        ),

        "no_students": "Barataan argamuu hin dandeenye.",

        "copyright": "© 2026 Mana Barumsaa Sadarkaa 2ffaa Ambuyyee"
    },

    "am": {

        "site_name": "አምቡዬ 2ኛ ደረጃ ትምህርት ቤት",
        "short_name": "AMBUYEE SCHOOL",

        "home": "መነሻ",
        "register": "የተማሪ ምዝገባ",
        "student_login": "የተማሪ መግቢያ",
        "teacher_login": "የመምህር መግቢያ",
        "dashboard": "ዳሽቦርድ",
        "logout": "ውጣ",

        "hero_title": "የተማሪዎች የመስመር ላይ ምዝገባ",
        "hero_text": (
            "በአምቡዬ 2ኛ ደረጃ ትምህርት ቤት "
            "ቀላልና ሙያዊ በሆነ መንገድ ይመዝገቡ።"
        ),

        "start_registration": "ምዝገባ ጀምር",
        "student_portal": "የተማሪ Portal",
        "teacher_portal": "የመምህር / Admin Portal",

        "about_title": "ስለ ስርዓቱ",
        "about_text": (
            "ይህ ስርዓት ከትምህርት ቤቱ ውጭ ያሉ ተማሪዎች "
            "አስፈላጊ መረጃና ሰነዶችን በመስመር ላይ እንዲያስገቡ "
            "እና የምዝገባቸውን ሁኔታ እንዲከታተሉ የተዘጋጀ ነው።"
        ),

        "features": "የስርዓቱ አገልግሎቶች",
        "online_registration": "Online ምዝገባ",
        "secure_documents": "የተጠበቁ ሰነዶች",
        "student_tracking": "የምዝገባ ክትትል",
        "teacher_verification": "የመምህር ማረጋገጫ",
        "statistics": "ስታቲስቲክስ",

        "full_name": "ሙሉ ስም",
        "phone": "ስልክ ቁጥር",
        "national_id": "National ID",
        "age": "ዕድሜ",
        "gender": "ጾታ",
        "male": "ወንድ",
        "female": "ሴት",

        "kebele": "ቀበሌ / ገንዳ",
        "zone": "ዞን",
        "grade": "ክፍል",
        "class_name": "Class",
        "stream": "Stream",

        "school_card_front": "የተማሪ ካርድ - ፊት",
        "school_card_back": "የተማሪ ካርድ - ጀርባ",
        "face_photo": "የተማሪ ፎቶ",

        "ministry_document": "የሚኒስቴር ሰነድ",
        "payment_screenshot": "የክፍያ ማረጋገጫ",

        "grade9_fee": "የ9ኛ ክፍል ክፍያ: 500 ብር",

        "student_code": "የተማሪ ኮድ",
        "choose_code": "የራስዎን ኮድ ይፍጠሩ",
        "confirm_code": "ኮዱን ያረጋግጡ",

        "submit": "ላክ",
        "save": "አስቀምጥ",
        "search": "ፈልግ",
        "filter": "Filter",

        "pending": "በመጠባበቅ ላይ",
        "approved": "ተቀባይነት አግኝቷል",
        "rejected": "ውድቅ ተደርጓል",
        "returned": "ተመልሷል",

        "boys": "ወንዶች",
        "girls": "ሴቶች",
        "total": "ጠቅላላ",

        "status": "የምዝገባ ሁኔታ",
        "message": "መልዕክት",
        "send_message": "መልዕክት ላክ",

        "approve": "Approve",
        "reject": "Reject",
        "return": "መልስ",

        "login": "ግባ",
        "password": "Password",
        "admin_code": "የመምህር ኮድ",

        "student_details": "የተማሪ መረጃ",
        "registration_date": "የምዝገባ ቀን",

        "success_registration": (
            "እንኳን ደስ አለዎት! ምዝገባዎ በትክክል ተሳክቷል።"
        ),

        "invalid_login": "ስልክ ቁጥሩ ወይም ኮዱ ትክክል አይደለም።",
        "required": "ይህ ክፍል ያስፈልጋል።",
        "files_required": "አስፈላጊ ሰነዶች ሙሉ መሆን አለባቸው።",
        "code_mismatch": "ኮዶቹ አይመሳሰሉም።",
        "invalid_file": "ይህ ፋይል አይፈቀድም።",
        "saved": "መረጃው በትክክል ተቀምጧል።",

        "login_instruction": (
            "በምዝገባ ጊዜ የፈጠሩትን ስልክ ቁጥርና ኮድ ይጠቀሙ።"
        ),

        "no_students": "ተማሪ አልተገኘም።",

        "copyright": "© 2026 አምቡዬ 2ኛ ደረጃ ትምህርት ቤት"
    },

    "en": {

        "site_name": "Ambuyyee Secondary School",
        "short_name": "AMBUYEE SCHOOL",

        "home": "Home",
        "register": "Student Registration",
        "student_login": "Student Login",
        "teacher_login": "Teacher Login",
        "dashboard": "Dashboard",
        "logout": "Logout",

        "hero_title": "Online Student Registration",
        "hero_text": (
            "Register at Ambuyyee Secondary School through "
            "a simple, secure and professional online system."
        ),

        "start_registration": "Start Registration",
        "student_portal": "Student Portal",
        "teacher_portal": "Teacher / Admin Portal",

        "about_title": "About the System",
        "about_text": (
            "This system allows students outside the school "
            "to submit required information and documents online "
            "and track their registration status."
        ),

        "features": "System Features",
        "online_registration": "Online Registration",
        "secure_documents": "Protected Documents",
        "student_tracking": "Registration Tracking",
        "teacher_verification": "Teacher Verification",
        "statistics": "Statistics",

        "full_name": "Full Name",
        "phone": "Phone Number",
        "national_id": "National ID",
        "age": "Age",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",

        "kebele": "Kebele / Ganda",
        "zone": "Zone",
        "grade": "Grade",
        "class_name": "Class",
        "stream": "Stream",

        "school_card_front": "School Card - Front",
        "school_card_back": "School Card - Back",
        "face_photo": "Student Face Photo",

        "ministry_document": "Ministry Document",
        "payment_screenshot": "Payment Screenshot",

        "grade9_fee": "Grade 9 Registration Fee: 500 Birr",

        "student_code": "Student Code",
        "choose_code": "Create Your Own Code",
        "confirm_code": "Confirm Code",

        "submit": "Submit",
        "save": "Save",
        "search": "Search",
        "filter": "Filter",

        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "returned": "Returned",

        "boys": "Boys",
        "girls": "Girls",
        "total": "Total",

        "status": "Registration Status",
        "message": "Message",
        "send_message": "Send Message",

        "approve": "Approve",
        "reject": "Reject",
        "return": "Return",

        "login": "Login",
        "password": "Password",
        "admin_code": "Teacher Code",

        "student_details": "Student Details",
        "registration_date": "Registration Date",

        "success_registration": (
            "Congratulations! Your registration was submitted successfully."
        ),

        "invalid_login": "Phone number or code is incorrect.",
        "required": "This field is required.",
        "files_required": "Required documents must be provided.",
        "code_mismatch": "The two codes do not match.",
        "invalid_file": "This file type is not allowed.",
        "saved": "Information saved successfully.",

        "login_instruction": (
            "Use the phone number and personal code you created during registration."
        ),

        "no_students": "No student was found.",

        "copyright": "© 2026 Ambuyyee Secondary School"
    }
}


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            registration_code TEXT UNIQUE NOT NULL,

            phone TEXT NOT NULL,
            code_hash TEXT NOT NULL,

            full_name TEXT NOT NULL,
            national_id TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,

            kebele TEXT NOT NULL,
            zone TEXT NOT NULL,

            grade TEXT NOT NULL,
            class_name TEXT NOT NULL,

            stream TEXT,

            card_front TEXT NOT NULL,
            card_back TEXT NOT NULL,
            face_photo TEXT NOT NULL,

            ministry_document TEXT,
            payment_screenshot TEXT,

            status TEXT NOT NULL DEFAULT 'pending',

            teacher_message TEXT DEFAULT '',

            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# SECURITY HELPERS
# ============================================================

def hash_code(code):
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def verify_code(code, saved_hash):
    return secrets.compare_digest(
        hash_code(code),
        saved_hash
    )


def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_upload(file, prefix):

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    original = secure_filename(file.filename)

    extension = original.rsplit(".", 1)[1].lower()

    unique_name = (
        prefix
        + "_"
        + secrets.token_hex(12)
        + "."
        + extension
    )

    path = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    file.save(path)

    return unique_name


def generate_registration_code():

    while True:

        code = (
            "AMB-"
            + secrets.token_hex(5).upper()
        )

        conn = get_db()

        existing = conn.execute(
            "SELECT id FROM students WHERE registration_code = ?",
            (code,)
        ).fetchone()

        conn.close()

        if not existing:
            return code


# ============================================================
# LANGUAGE
# ============================================================

def current_lang():

    language = session.get("lang", "om")

    if language not in LANG:
        language = "om"

    return language


@app.context_processor
def inject_globals():

    return {
        "t": LANG[current_lang()],
        "current_lang": current_lang()
    }


@app.route("/language/<language>")
def change_language(language):

    if language in LANG:
        session["lang"] = language

    return redirect(
        request.referrer or url_for("home")
    )


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(
                url_for("admin_login")
            )

        return function(*args, **kwargs)

    return wrapper


def student_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("student_id"):
            return redirect(
                url_for("student_login")
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# GLOBAL HTML / CSS
# ============================================================

BASE_HTML = """

<!DOCTYPE html>

<html lang="{{ current_lang }}">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>{{ title }} | Ambuyyee School</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #07111f,
            #0d1b2e,
            #101827
        );

    color: #f4f7fb;
    min-height: 100vh;
}

a {
    text-decoration: none;
    color: inherit;
}

.navbar {
    width: 100%;
    padding: 18px 5%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    background: rgba(5, 12, 23, .92);

    border-bottom:
        1px solid rgba(255,255,255,.08);

    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 800;
}

.logo {
    width: 45px;
    height: 45px;
    border-radius: 13px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #d8b25c,
            #fff0aa
        );

    color: #08111e;
    font-weight: 900;
    box-shadow:
        0 8px 25px rgba(216,178,92,.18);
}

.brand-text {
    max-width: 260px;
    line-height: 1.25;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.nav-links a,
.lang-btn {
    padding: 9px 12px;
    border-radius: 9px;
    color: #dce6f3;
    font-size: 14px;
}

.nav-links a:hover,
.lang-btn:hover {
    background: rgba(255,255,255,.07);
    color: #fff;
}

.langs {
    display: flex;
    gap: 4px;
    margin-left: 6px;
}

.lang-btn.active {
    background: #d8b25c;
    color: #07111f;
    font-weight: 800;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
}

.hero {
    padding: 90px 0 70px;
    text-align: center;
}

.hero h1 {
    font-size: clamp(35px, 7vw, 72px);
    line-height: 1.05;
    margin-bottom: 22px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #d8b25c,
            #ffffff
        );

    -webkit-background-clip: text;
    color: transparent;
}

.hero p {
    max-width: 760px;
    margin: auto;
    color: #aebbd0;
    font-size: 18px;
    line-height: 1.8;
}

.buttons {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 32px;
}

.btn {
    border: none;
    cursor: pointer;

    padding: 13px 20px;
    border-radius: 11px;

    font-weight: 800;
    font-size: 14px;
}

.btn-primary {
    background: #d8b25c;
    color: #07111f;
}

.btn-primary:hover {
    background: #f0cf79;
}

.btn-dark {
    background: #17263a;
    color: #fff;
    border: 1px solid rgba(255,255,255,.08);
}

.btn-danger {
    background: #9f3040;
    color: white;
}

.btn-success {
    background: #217a52;
    color: white;
}

.btn-warning {
    background: #9a7525;
    color: white;
}

.section {
    padding: 60px 0;
}

.section-title {
    text-align: center;
    margin-bottom: 35px;
}

.section-title h2 {
    font-size: 32px;
    margin-bottom: 10px;
}

.section-title p {
    color: #9eabc0;
}

.cards {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));

    gap: 18px;
}

.card {
    background:
        rgba(255,255,255,.045);

    border:
        1px solid rgba(255,255,255,.08);

    border-radius: 18px;
    padding: 25px;

    box-shadow:
        0 15px 50px rgba(0,0,0,.16);
}

.card h3 {
    margin-bottom: 10px;
}

.card p {
    color: #aab8cb;
    line-height: 1.65;
}

.icon {
    font-size: 30px;
    margin-bottom: 15px;
}

.form-wrapper {
    max-width: 900px;
    margin: 45px auto;
}

.form-card {
    background:
        rgba(255,255,255,.045);

    border:
        1px solid rgba(255,255,255,.09);

    border-radius: 22px;
    padding: 30px;

    box-shadow:
        0 20px 70px rgba(0,0,0,.25);
}

.form-card h1 {
    margin-bottom: 8px;
}

.form-card > p {
    color: #aebbd0;
    margin-bottom: 28px;
    line-height: 1.6;
}

.form-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 18px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.full {
    grid-column: 1 / -1;
}

label {
    font-weight: 700;
    font-size: 14px;
    color: #dbe4f1;
}

input,
select,
textarea {
    width: 100%;

    padding: 13px 14px;

    background: #0c1828;
    color: #fff;

    border:
        1px solid rgba(255,255,255,.12);

    border-radius: 10px;
    outline: none;
}

input:focus,
select:focus,
textarea:focus {
    border-color: #d8b25c;
}

textarea {
    min-height: 130px;
    resize: vertical;
}

.file-note {
    color: #8493a8;
    font-size: 12px;
}

.hidden {
    display: none !important;
}

.alert {
    padding: 14px 16px;
    border-radius: 10px;
    margin-bottom: 15px;
    background: rgba(216,178,92,.12);
    border: 1px solid rgba(216,178,92,.25);
}

.stats {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(160px, 1fr));

    gap: 15px;
    margin-bottom: 25px;
}

.stat {
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.08);
}

.stat-number {
    font-size: 32px;
    font-weight: 900;
    color: #d8b25c;
}

.stat-label {
    color: #aebbd0;
    margin-top: 5px;
}

.table-wrapper {
    overflow-x: auto;
    background: rgba(255,255,255,.035);
    border-radius: 16px;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 900px;
}

th,
td {
    padding: 14px;
    border-bottom:
        1px solid rgba(255,255,255,.07);

    text-align: left;
}

th {
    color: #d8b25c;
    font-size: 13px;
}

td {
    color: #dce5f0;
    font-size: 14px;
}

.badge {
    display: inline-block;
    padding: 6px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
}

.badge-pending {
    background: #72591e;
    color: #ffe9a5;
}

.badge-approved {
    background: #185d40;
    color: #b8ffdb;
}

.badge-rejected {
    background: #71303a;
    color: #ffc5cc;
}

.badge-returned {
    background: #4d5360;
    color: #dfe5ef;
}

.filters {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(170px, 1fr));

    gap: 12px;
    margin-bottom: 22px;
}

.grade-stat-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(240px, 1fr));

    gap: 15px;
}

.grade-box {
    padding: 18px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 15px;
}

.grade-box h3 {
    margin-bottom: 14px;
    color: #d8b25c;
}

.class-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,.05);
    color: #b7c4d5;
}

.detail-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 15px;
}

.detail-item {
    padding: 15px;
    background: rgba(255,255,255,.035);
    border-radius: 12px;
}

.detail-item span {
    display: block;
    color: #8392a7;
    font-size: 12px;
    margin-bottom: 5px;
}

.detail-item strong {
    color: #fff;
}

.document-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(200px, 1fr));

    gap: 15px;
    margin-top: 20px;
}

.document-card {
    background: rgba(255,255,255,.035);
    border-radius: 14px;
    padding: 14px;
}

.document-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 10px;
}

.document-card iframe {
    width: 100%;
    height: 220px;
    border: none;
    border-radius: 10px;
}

.footer {
    margin-top: 70px;
    padding: 30px 5%;
    text-align: center;
    color: #7e8da2;
    border-top: 1px solid rgba(255,255,255,.07);
}

.mobile-space {
    height: 10px;
}

@media(max-width: 750px) {

    .navbar {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }

    .nav-links {
        width: 100%;
    }

    .form-grid,
    .detail-grid {
        grid-template-columns: 1fr;
    }

    .full {
        grid-column: auto;
    }

    .form-card {
        padding: 20px;
    }

    .hero {
        padding-top: 55px;
    }

}

</style>

</head>

<body>

<nav class="navbar">

    <a class="brand" href="{{ url_for('home') }}">

        <div class="logo">
            A
        </div>

        <div class="brand-text">
            {{ t.site_name }}
        </div>

    </a>

    <div class="nav-links">

        <a href="{{ url_for('home') }}">
            {{ t.home }}
        </a>

        <a href="{{ url_for('register') }}">
            {{ t.register }}
        </a>

        <a href="{{ url_for('student_login') }}">
            {{ t.student_login }}
        </a>

        <a href="{{ url_for('admin_login') }}">
            {{ t.teacher_login }}
        </a>

        <div class="langs">

            <a
                class="lang-btn {% if current_lang == 'om' %}active{% endif %}"
                href="{{ url_for('change_language', language='om') }}"
            >
                Afaan Oromoo
            </a>

            <a
                class="lang-btn {% if current_lang == 'am' %}active{% endif %}"
                href="{{ url_for('change_language', language='am') }}"
            >
                አማ
            </a>

            <a
                class="lang-btn {% if current_lang == 'en' %}active{% endif %}"
                href="{{ url_for('change_language', language='en') }}"
            >
                EN
            </a>

        </div>

    </div>

</nav>


{% with messages = get_flashed_messages() %}

    {% if messages %}

        <div class="container" style="margin-top:20px;">

            {% for message in messages %}

                <div class="alert">
                    {{ message }}
                </div>

            {% endfor %}

        </div>

    {% endif %}

{% endwith %}


{% block_content %}{% endblock %}


<footer class="footer">

    {{ t.copyright }}

</footer>

</body>

</html>

"""


def render_page(content, title="Ambuyyee School", **context):

    html = BASE_HTML.replace(
        "{% block_content %}{% endblock %}",
        content
    )

    return render_template_string(
        html,
        title=title,
        **context
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    content = """

<section class="hero">

    <div class="container">

        <h1>
            {{ t.hero_title }}
        </h1>

        <p>
            {{ t.hero_text }}
        </p>

        <div class="buttons">

            <a
                class="btn btn-primary"
                href="{{ url_for('register') }}"
            >
                {{ t.start_registration }}
            </a>

            <a
                class="btn btn-dark"
                href="{{ url_for('student_login') }}"
            >
                {{ t.student_portal }}
            </a>

            <a
                class="btn btn-dark"
                href="{{ url_for('admin_login') }}"
            >
                {{ t.teacher_portal }}
            </a>

        </div>

    </div>

</section>


<section class="section">

    <div class="container">

        <div class="section-title">

            <h2>
                {{ t.features }}
            </h2>

        </div>


        <div class="cards">

            <div class="card">

                <div class="icon">📝</div>

                <h3>
                    {{ t.online_registration }}
                </h3>

                <p>
                    {{ t.about_text }}
                </p>

            </div>


            <div class="card">

                <div class="icon">🔐</div>

                <h3>
                    {{ t.secure_documents }}
                </h3>

                <p>
                    Student cards, photos and required documents
                    are stored through the application backend.
                </p>

            </div>


            <div class="card">

                <div class="icon">📊</div>

                <h3>
                    {{ t.statistics }}
                </h3>

                <p>
                    Teachers can see students by grade,
                    class and gender.
                </p>

            </div>


            <div class="card">

                <div class="icon">👨‍🏫</div>

                <h3>
                    {{ t.teacher_verification }}
                </h3>

                <p>
                    Submitted registration can be reviewed
                    before approval.
                </p>

            </div>

        </div>

    </div>

</section>


<section class="section">

    <div class="container">

        <div class="section-title">

            <h2>
                {{ t.about_title }}
            </h2>

            <p>
                {{ t.about_text }}
            </p>

        </div>

    </div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["home"]
    )


# ============================================================
# STUDENT REGISTRATION
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        phone = request.form.get(
            "phone", ""
        ).strip()

        national_id = request.form.get(
            "national_id", ""
        ).strip()

        age_text = request.form.get(
            "age", ""
        ).strip()

        gender = request.form.get(
            "gender", ""
        ).strip()

        kebele = request.form.get(
            "kebele", ""
        ).strip()

        zone = request.form.get(
            "zone", ""
        ).strip()

        grade = request.form.get(
            "grade", ""
        ).strip()

        class_name = request.form.get(
            "class_name", ""
        ).strip()

        stream = request.form.get(
            "stream", ""
        ).strip()

        personal_code = request.form.get(
            "personal_code", ""
        ).strip()

        confirm_code = request.form.get(
            "confirm_code", ""
        ).strip()


        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not all([
            full_name,
            phone,
            national_id,
            age_text,
            gender,
            kebele,
            zone,
            grade,
            class_name,
            personal_code,
            confirm_code
        ]):

            flash(
                LANG[current_lang()]["required"]
            )

            return redirect(
                url_for("register")
            )


        try:
            age = int(age_text)
        except ValueError:

            flash(
                LANG[current_lang()]["required"]
            )

            return redirect(
                url_for("register")
            )


        if age < 5 or age > 100:

            flash(
                LANG[current_lang()]["required"]
            )

            return redirect(
                url_for("register")
            )


        if grade not in GRADES:

            abort(400)


        if class_name not in CLASSES:

            abort(400)


        if gender not in GENDERS:

            abort(400)


        if grade in ["11", "12"]:

            if stream not in STREAMS:
                flash(
                    LANG[current_lang()]["required"]
                )
                return redirect(
                    url_for("register")
                )

        else:

            stream = None


        # ----------------------------------------------------
        # PERSONAL CODE
        # ----------------------------------------------------

        if len(personal_code) < 6:

            flash(
                "Koodiin yoo xiqqaate characters 6 qabaachuu qaba."
            )

            return redirect(
                url_for("register")
            )


        if personal_code != confirm_code:

            flash(
                LANG[current_lang()]["code_mismatch"]
            )

            return redirect(
                url_for("register")
            )


        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        card_front = request.files.get(
            "card_front"
        )

        card_back = request.files.get(
            "card_back"
        )

        face_photo = request.files.get(
            "face_photo"
        )

        ministry_document = request.files.get(
            "ministry_document"
        )

        payment_screenshot = request.files.get(
            "payment_screenshot"
        )


        if not card_front or not card_back or not face_photo:

            flash(
                LANG[current_lang()]["files_required"]
            )

            return redirect(
                url_for("register")
            )


        # Grade 9 requires ministry + payment
        if grade == "9":

            if not ministry_document or not payment_screenshot:

                flash(
                    LANG[current_lang()]["files_required"]
                )

                return redirect(
                    url_for("register")
                )


        # ----------------------------------------------------
        # SAVE FILES
        # ----------------------------------------------------

        registration_code = generate_registration_code()


        saved_card_front = save_upload(
            card_front,
            registration_code + "_card_front"
        )

        saved_card_back = save_upload(
            card_back,
            registration_code + "_card_back"
        )

        saved_face = save_upload(
            face_photo,
            registration_code + "_face"
        )


        if not saved_card_front or not saved_card_back or not saved_face:

            flash(
                LANG[current_lang()]["invalid_file"]
            )

            return redirect(
                url_for("register")
            )


        saved_ministry = None
        saved_payment = None


        if grade == "9":

            saved_ministry = save_upload(
                ministry_document,
                registration_code + "_ministry"
            )

            saved_payment = save_upload(
                payment_screenshot,
                registration_code + "_payment"
            )

            if not saved_ministry or not saved_payment:

                flash(
                    LANG[current_lang()]["invalid_file"]
                )

                return redirect(
                    url_for("register")
                )


        # ----------------------------------------------------
        # DATABASE INSERT
        # ----------------------------------------------------

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        code_hash = hash_code(
            personal_code
        )

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO students (
                    registration_code,
                    phone,
                    code_hash,
                    full_name,
                    national_id,
                    age,
                    gender,
                    kebele,
                    zone,
                    grade,
                    class_name,
                    stream,
                    card_front,
                    card_back,
                    face_photo,
                    ministry_document,
                    payment_screenshot,
                    status,
                    teacher_message,
                    created_at,
                    updated_at
                )

                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (

                registration_code,
                phone,
                code_hash,
                full_name,
                national_id,
                age,
                gender,
                kebele,
                zone,
                grade,
                class_name,
                stream,
                saved_card_front,
                saved_card_back,
                saved_face,
                saved_ministry,
                saved_payment,
                "pending",
                "",
                now,
                now

            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "Registration already exists."
            )

            return redirect(
                url_for("register")
            )

        conn.close()


        # ----------------------------------------------------
        # SHOW SUCCESS PAGE
        # ----------------------------------------------------

        return render_page(
            """

            <section class="section">

                <div class="container">

                    <div class="form-card" style="text-align:center;">

                        <div style="font-size:55px;">
                            ✅
                        </div>

                        <h1>
                            {{ t.success_registration }}
                        </h1>

                        <p>
                            {{ t.student_code }}
                        </p>

                        <div
                            style="
                                font-size:28px;
                                font-weight:900;
                                color:#d8b25c;
                                margin:20px 0;
                            "
                        >
                            {{ registration_code }}
                        </div>

                        <p>
                            {{ t.login_instruction }}
                        </p>

                        <div class="buttons">

                            <a
                                href="{{ url_for('student_login') }}"
                                class="btn btn-primary"
                            >
                                {{ t.student_login }}
                            </a>

                            <a
                                href="{{ url_for('home') }}"
                                class="btn btn-dark"
                            >
                                {{ t.home }}
                            </a>

                        </div>

                    </div>

                </div>

            </section>

            """,

            title="Registration Success",

            registration_code=registration_code
        )


    # --------------------------------------------------------
    # GET REGISTRATION PAGE
    # --------------------------------------------------------

    content = """

<section class="section">

<div class="container">

<div class="form-wrapper">

<div class="form-card">

<h1>
    {{ t.register }}
</h1>

<p>
    {{ t.about_text }}
</p>


<form
    method="POST"
    enctype="multipart/form-data"
>


<div class="form-grid">


<div class="form-group full">

<label>
    {{ t.full_name }}
</label>

<input
    type="text"
    name="full_name"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.phone }}
</label>

<input
    type="tel"
    name="phone"
    placeholder="09XXXXXXXX"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.national_id }}
</label>

<input
    type="text"
    name="national_id"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.age }}
</label>

<input
    type="number"
    name="age"
    min="5"
    max="100"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.gender }}
</label>

<select name="gender" required>

<option value="">
    -- Select --
</option>

<option value="Male">
    {{ t.male }}
</option>

<option value="Female">
    {{ t.female }}
</option>

</select>

</div>


<div class="form-group">

<label>
    {{ t.kebele }}
</label>

<input
    type="text"
    name="kebele"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.zone }}
</label>

<input
    type="text"
    name="zone"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.grade }}
</label>

<select
    name="grade"
    id="grade"
    required
>

<option value="">
    -- Select Grade --
</option>

<option value="9">Grade 9</option>
<option value="10">Grade 10</option>
<option value="11">Grade 11</option>
<option value="12">Grade 12</option>

</select>

</div>


<div class="form-group">

<label>
    {{ t.class_name }}
</label>

<select
    name="class_name"
    required
>

<option value="">
    -- Select Class --
</option>

<option value="A">Class A</option>
<option value="B">Class B</option>
<option value="C">Class C</option>
<option value="D">Class D</option>
<option value="E">Class E</option>
<option value="F">Class F</option>

</select>

</div>


<div
    class="form-group full"
    id="stream-box"
>

<label>
    {{ t.stream }}
</label>

<select name="stream">

<option value="">
    -- Select Stream --
</option>

<option value="Natural Science">
    Natural Science
</option>

<option value="Social Science">
    Social Science
</option>

</select>

</div>


<div class="form-group full">

<label>
    {{ t.choose_code }}
</label>

<input
    type="password"
    name="personal_code"
    minlength="6"
    required
>

<div class="file-note">
    Koodii ati filattu yoo xiqqaate characters 6 haa qabaatu.
</div>

</div>


<div class="form-group full">

<label>
    {{ t.confirm_code }}
</label>

<input
    type="password"
    name="confirm_code"
    minlength="6"
    required
>

</div>


<div class="form-group">

<label>
    {{ t.school_card_front }}
</label>

<input
    type="file"
    name="card_front"
    accept=".jpg,.jpeg,.png,.pdf"
    required
>

<div class="file-note">
    JPG, PNG ykn PDF
</div>

</div>


<div class="form-group">

<label>
    {{ t.school_card_back }}
</label>

<input
    type="file"
    name="card_back"
    accept=".jpg,.jpeg,.png,.pdf"
    required
>

<div class="file-note">
    JPG, PNG ykn PDF
</div>

</div>


<div class="form-group full">

<label>
    {{ t.face_photo }}
</label>

<input
    type="file"
    name="face_photo"
    accept=".jpg,.jpeg,.png"
    required
>

<div class="file-note">
    Suura qulqulluu fuula barataa.
</div>

</div>


<div class="form-group full">

<div
    class="card"
    style="
        padding:16px;
        margin:0;
    "
>

<strong>
    {{ t.grade9_fee }}
</strong>

<p style="margin-top:8px;">
    Grade 9 qofaaf Ministry Document fi
    payment screenshot barbaachisa.
</p>

</div>

</div>


<div
    class="form-group"
    id="ministry-box"
>

<label>
    {{ t.ministry_document }}
</label>

<input
    type="file"
    name="ministry_document"
    accept=".jpg,.jpeg,.png,.pdf"
>

</div>


<div
    class="form-group"
    id="payment-box"
>

<label>
    {{ t.payment_screenshot }}
</label>

<input
    type="file"
    name="payment_screenshot"
    accept=".jpg,.jpeg,.png,.pdf"
>

</div>


<div class="form-group full">

<button
    type="submit"
    class="btn btn-primary"
    style="width:100%;"
>
    {{ t.submit }}
</button>

</div>


</div>

</form>

</div>

</div>

</div>

</section>


<script>

const grade = document.getElementById("grade");

const streamBox =
    document.getElementById("stream-box");

const ministryBox =
    document.getElementById("ministry-box");

const paymentBox =
    document.getElementById("payment-box");


function updateGradeFields() {

    const value = grade.value;

    if (value === "11" || value === "12") {

        streamBox.classList.remove("hidden");

    } else {

        streamBox.classList.add("hidden");

    }


    if (value === "9") {

        ministryBox.classList.remove("hidden");
        paymentBox.classList.remove("hidden");

    } else {

        ministryBox.classList.add("hidden");
        paymentBox.classList.add("hidden");

    }

}


grade.addEventListener(
    "change",
    updateGradeFields
);

updateGradeFields();

</script>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["register"]
    )


# ============================================================
# STUDENT LOGIN
# ============================================================

@app.route("/student/login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        phone = request.form.get(
            "phone", ""
        ).strip()

        code = request.form.get(
            "code", ""
        ).strip()


        conn = get_db()

        student = conn.execute("""
            SELECT *
            FROM students
            WHERE phone = ?
            ORDER BY id DESC
            LIMIT 1
        """, (phone,)).fetchone()

        conn.close()


        if student and verify_code(
            code,
            student["code_hash"]
        ):

            session.clear()

            session["student_id"] = student["id"]

            return redirect(
                url_for("student_dashboard")
            )


        flash(
            LANG[current_lang()]["invalid_login"]
        )


    content = """

<section class="section">

<div class="container">

<div class="form-wrapper">

<div class="form-card">

<h1>
    {{ t.student_login }}
</h1>

<p>
    {{ t.login_instruction }}
</p>


<form method="POST">

<div class="form-group">

<label>
    {{ t.phone }}
</label>

<input
    type="tel"
    name="phone"
    required
>

</div>


<div
    class="form-group"
    style="margin-top:18px;"
>

<label>
    {{ t.student_code }}
</label>

<input
    type="password"
    name="code"
    required
>

</div>


<button
    class="btn btn-primary"
    style="
        width:100%;
        margin-top:20px;
    "
>
    {{ t.login }}
</button>

</form>

</div>

</div>

</div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["student_login"]
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():

    student_id = session["student_id"]

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()


    if not student:
        session.clear()
        return redirect(
            url_for("student_login")
        )


    status_class = {
        "pending": "badge-pending",
        "approved": "badge-approved",
        "rejected": "badge-rejected",
        "returned": "badge-returned"
    }.get(
        student["status"],
        "badge-pending"
    )


    status_text = {
        "pending": LANG[current_lang()]["pending"],
        "approved": LANG[current_lang()]["approved"],
        "rejected": LANG[current_lang()]["rejected"],
        "returned": LANG[current_lang()]["returned"]
    }.get(
        student["status"],
        student["status"]
    )


    content = """

<section class="section">

<div class="container">

<div class="section-title">

<h2>
    {{ t.dashboard }}
</h2>

<p>
    {{ student["full_name"] }}
</p>

</div>


<div class="card">

<div class="detail-grid">


<div class="detail-item">

<span>
    {{ t.student_code }}
</span>

<strong>
    {{ student["registration_code"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.status }}
</span>

<strong>

<span class="badge {{ status_class }}">
    {{ status_text }}
</span>

</strong>

</div>


<div class="detail-item">

<span>
    {{ t.full_name }}
</span>

<strong>
    {{ student["full_name"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.phone }}
</span>

<strong>
    {{ student["phone"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.grade }}
</span>

<strong>
    Grade {{ student["grade"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.class_name }}
</span>

<strong>
    Class {{ student["class_name"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.gender }}
</span>

<strong>
    {{ student["gender"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.stream }}
</span>

<strong>
    {{ student["stream"] or "-" }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.kebele }}
</span>

<strong>
    {{ student["kebele"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.zone }}
</span>

<strong>
    {{ student["zone"] }}
</strong>

</div>


</div>


{% if student["teacher_message"] %}

<div
    class="alert"
    style="margin-top:20px;"
>

<strong>
    {{ t.message }}
</strong>

<br><br>

{{ student["teacher_message"] }}

</div>

{% endif %}


<div class="buttons">

<a
    class="btn btn-dark"
    href="{{ url_for('student_logout') }}"
>
    {{ t.logout }}
</a>

</div>

</div>

</div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["dashboard"],
        student=student,
        status_class=status_class,
        status_text=status_text
    )


@app.route("/student/logout")
def student_logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        entered_code = request.form.get(
            "admin_code", ""
        ).strip()


        # IMPORTANT:
        # Production keessatti kana environment variable
        # keessatti ofii keetiin kaa'i.
        admin_code = os.environ.get(
            "AMBUYEE_ADMIN_CODE",
            "AMB-TEACHER-DEMO-CHANGE-ME"
        )


        if secrets.compare_digest(
            entered_code,
            admin_code
        ):

            session.clear()

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )


        flash(
            LANG[current_lang()]["invalid_login"]
        )


    content = """

<section class="section">

<div class="container">

<div class="form-wrapper">

<div class="form-card">

<h1>
    {{ t.teacher_login }}
</h1>

<p>
    Teacher/Admin access only.
</p>


<form method="POST">

<div class="form-group">

<label>
    {{ t.admin_code }}
</label>

<input
    type="password"
    name="admin_code"
    required
>

</div>


<button
    class="btn btn-primary"
    style="
        width:100%;
        margin-top:20px;
    "
>
    {{ t.login }}
</button>

</form>

</div>

</div>

</div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["teacher_login"]
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    grade_filter = request.args.get(
        "grade",
        ""
    ).strip()

    class_filter = request.args.get(
        "class_name",
        ""
    ).strip()

    gender_filter = request.args.get(
        "gender",
        ""
    ).strip()

    status_filter = request.args.get(
        "status",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()


    conn = get_db()


    # --------------------------------------------------------
    # MAIN STUDENT QUERY
    # --------------------------------------------------------

    query = """
        SELECT *
        FROM students
        WHERE 1 = 1
    """

    params = []


    if grade_filter:

        query += " AND grade = ?"
        params.append(grade_filter)


    if class_filter:

        query += " AND class_name = ?"
        params.append(class_filter)


    if gender_filter:

        query += " AND gender = ?"
        params.append(gender_filter)


    if status_filter:

        query += " AND status = ?"
        params.append(status_filter)


    if search:

        query += """
            AND (
                full_name LIKE ?
                OR phone LIKE ?
                OR registration_code LIKE ?
                OR national_id LIKE ?
            )
        """

        search_value = "%" + search + "%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])


    query += """
        ORDER BY id DESC
    """


    students = conn.execute(
        query,
        params
    ).fetchall()


    # --------------------------------------------------------
    # OVERALL STATISTICS
    # --------------------------------------------------------

    total = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]


    pending = conn.execute(
        "SELECT COUNT(*) FROM students WHERE status='pending'"
    ).fetchone()[0]


    approved = conn.execute(
        "SELECT COUNT(*) FROM students WHERE status='approved'"
    ).fetchone()[0]


    rejected = conn.execute(
        "SELECT COUNT(*) FROM students WHERE status='rejected'"
    ).fetchone()[0]


    # --------------------------------------------------------
    # GRADE / CLASS / GENDER STATISTICS
    # --------------------------------------------------------

    statistics = {}


    for grade in GRADES:

        statistics[grade] = {}


        for class_name in CLASSES:

            boys = conn.execute("""
                SELECT COUNT(*)
                FROM students
                WHERE grade = ?
                AND class_name = ?
                AND gender = 'Male'
            """, (
                grade,
                class_name
            )).fetchone()[0]


            girls = conn.execute("""
                SELECT COUNT(*)
                FROM students
                WHERE grade = ?
                AND class_name = ?
                AND gender = 'Female'
            """, (
                grade,
                class_name
            )).fetchone()[0]


            total_class = boys + girls


            statistics[grade][class_name] = {
                "boys": boys,
                "girls": girls,
                "total": total_class
            }


    conn.close()


    content = """

<section class="section">

<div class="container">

<div class="section-title">

<h2>
    {{ t.dashboard }}
</h2>

<p>
    Teacher / Administration Control Center
</p>

</div>


<div class="stats">


<div class="stat">

<div class="stat-number">
    {{ total }}
</div>

<div class="stat-label">
    {{ t.total }}
</div>

</div>


<div class="stat">

<div class="stat-number">
    {{ pending }}
</div>

<div class="stat-label">
    {{ t.pending }}
</div>

</div>


<div class="stat">

<div class="stat-number">
    {{ approved }}
</div>

<div class="stat-label">
    {{ t.approved }}
</div>

</div>


<div class="stat">

<div class="stat-number">
    {{ rejected }}
</div>

<div class="stat-label">
    {{ t.rejected }}
</div>

</div>


</div>


<div class="card">

<h2 style="margin-bottom:20px;">
    {{ t.statistics }}
</h2>


<div class="grade-stat-grid">


{% for grade in grades %}

<div class="grade-box">

<h3>
    Grade {{ grade }}
</h3>


{% for class_name in classes %}

<div class="class-row">

<span>
    Class {{ class_name }}
</span>

<span>
    {{ statistics[grade][class_name]["total"] }}
    |
    {{ t.boys }}:
    {{ statistics[grade][class_name]["boys"] }}
    |
    {{ t.girls }}:
    {{ statistics[grade][class_name]["girls"] }}
</span>

</div>

{% endfor %}

</div>

{% endfor %}


</div>

</div>


<div class="card" style="margin-top:25px;">

<h2 style="margin-bottom:20px;">
    {{ t.filter }}
</h2>


<form method="GET">

<div class="filters">


<input
    type="text"
    name="search"
    value="{{ search }}"
    placeholder="{{ t.search }}"
>


<select name="grade">

<option value="">
    All Grades
</option>

{% for grade in grades %}

<option
    value="{{ grade }}"
    {% if grade_filter == grade %}
        selected
    {% endif %}
>
    Grade {{ grade }}
</option>

{% endfor %}

</select>


<select name="class_name">

<option value="">
    All Classes
</option>

{% for c in classes %}

<option
    value="{{ c }}"
    {% if class_filter == c %}
        selected
    {% endif %}
>
    Class {{ c }}
</option>

{% endfor %}

</select>


<select name="gender">

<option value="">
    All Gender
</option>

<option
    value="Male"
    {% if gender_filter == "Male" %}
        selected
    {% endif %}
>
    {{ t.male }}
</option>

<option
    value="Female"
    {% if gender_filter == "Female" %}
        selected
    {% endif %}
>
    {{ t.female }}
</option>

</select>


<select name="status">

<option value="">
    All Status
</option>

<option
    value="pending"
    {% if status_filter == "pending" %}
        selected
    {% endif %}
>
    {{ t.pending }}
</option>

<option
    value="approved"
    {% if status_filter == "approved" %}
        selected
    {% endif %}
>
    {{ t.approved }}
</option>

<option
    value="rejected"
    {% if status_filter == "rejected" %}
        selected
    {% endif %}
>
    {{ t.rejected }}
</option>

</select>


<button
    class="btn btn-primary"
    type="submit"
>
    {{ t.search }}
</button>


</div>

</form>

</div>


<div class="card" style="margin-top:25px;">

<h2 style="margin-bottom:20px;">
    {{ t.register }}
</h2>


<div class="table-wrapper">

<table>

<thead>

<tr>

<th>ID</th>

<th>
    {{ t.student_code }}
</th>

<th>
    {{ t.full_name }}
</th>

<th>
    {{ t.phone }}
</th>

<th>
    {{ t.grade }}
</th>

<th>
    {{ t.class_name }}
</th>

<th>
    {{ t.gender }}
</th>

<th>
    {{ t.status }}
</th>

<th>
    Action
</th>

</tr>

</thead>


<tbody>


{% for student in students %}

<tr>

<td>
    {{ student["id"] }}
</td>

<td>
    {{ student["registration_code"] }}
</td>

<td>
    {{ student["full_name"] }}
</td>

<td>
    {{ student["phone"] }}
</td>

<td>
    {{ student["grade"] }}
</td>

<td>
    {{ student["class_name"] }}
</td>

<td>
    {{ student["gender"] }}
</td>

<td>

<span class="badge badge-{{ student['status'] }}">
    {{ student["status"] }}
</span>

</td>

<td>

<a
    class="btn btn-dark"
    href="{{ url_for('admin_student_detail', student_id=student['id']) }}"
>
    View
</a>

</td>

</tr>

{% else %}

<tr>

<td colspan="9">

{{ t.no_students }}

</td>

</tr>

{% endfor %}


</tbody>

</table>

</div>

</div>


<div class="buttons">

<a
    href="{{ url_for('admin_logout') }}"
    class="btn btn-dark"
>
    {{ t.logout }}
</a>

</div>


</div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["dashboard"],
        students=students,
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        grades=GRADES,
        classes=CLASSES,
        statistics=statistics,
        grade_filter=grade_filter,
        class_filter=class_filter,
        gender_filter=gender_filter,
        status_filter=status_filter,
        search=search
    )


# ============================================================
# ADMIN STUDENT DETAIL
# ============================================================

@app.route("/admin/student/<int:student_id>")
@admin_required
def admin_student_detail(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()


    if not student:
        abort(404)


    content = """

<section class="section">

<div class="container">

<div class="section-title">

<h2>
    {{ t.student_details }}
</h2>

<p>
    {{ student["registration_code"] }}
</p>

</div>


<div class="card">


<div class="detail-grid">


<div class="detail-item">

<span>
    {{ t.full_name }}
</span>

<strong>
    {{ student["full_name"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.phone }}
</span>

<strong>
    {{ student["phone"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.national_id }}
</span>

<strong>
    {{ student["national_id"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.age }}
</span>

<strong>
    {{ student["age"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.gender }}
</span>

<strong>
    {{ student["gender"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.kebele }}
</span>

<strong>
    {{ student["kebele"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.zone }}
</span>

<strong>
    {{ student["zone"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.grade }}
</span>

<strong>
    Grade {{ student["grade"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.class_name }}
</span>

<strong>
    Class {{ student["class_name"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.stream }}
</span>

<strong>
    {{ student["stream"] or "-" }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.registration_date }}
</span>

<strong>
    {{ student["created_at"] }}
</strong>

</div>


<div class="detail-item">

<span>
    {{ t.status }}
</span>

<strong>
    {{ student["status"] }}
</strong>

</div>


</div>


<h2 style="margin-top:30px;">
    Documents
</h2>


<div class="document-grid">


<div class="document-card">

<h4>
    {{ t.face_photo }}
</h4>

<br>

<img
    src="{{ url_for('uploaded_file', filename=student['face_photo']) }}"
>

</div>


<div class="document-card">

<h4>
    {{ t.school_card_front }}
</h4>

<br>

{% if student["card_front"].lower().endswith(".pdf") %}

<iframe
    src="{{ url_for('uploaded_file', filename=student['card_front']) }}"
></iframe>

{% else %}

<img
    src="{{ url_for('uploaded_file', filename=student['card_front']) }}"
>

{% endif %}

</div>


<div class="document-card">

<h4>
    {{ t.school_card_back }}
</h4>

<br>

{% if student["card_back"].lower().endswith(".pdf") %}

<iframe
    src="{{ url_for('uploaded_file', filename=student['card_back']) }}"
></iframe>

{% else %}

<img
    src="{{ url_for('uploaded_file', filename=student['card_back']) }}"
>

{% endif %}

</div>


{% if student["ministry_document"] %}

<div class="document-card">

<h4>
    {{ t.ministry_document }}
</h4>

<br>

{% if student["ministry_document"].lower().endswith(".pdf") %}

<iframe
    src="{{ url_for('uploaded_file', filename=student['ministry_document']) }}"
></iframe>

{% else %}

<img
    src="{{ url_for('uploaded_file', filename=student['ministry_document']) }}"
>

{% endif %}

</div>

{% endif %}


{% if student["payment_screenshot"] %}

<div class="document-card">

<h4>
    {{ t.payment_screenshot }}
</h4>

<br>

{% if student["payment_screenshot"].lower().endswith(".pdf") %}

<iframe
    src="{{ url_for('uploaded_file', filename=student['payment_screenshot']) }}"
></iframe>

{% else %}

<img
    src="{{ url_for('uploaded_file', filename=student['payment_screenshot']) }}"
>

{% endif %}

</div>

{% endif %}


</div>


<div class="card" style="margin-top:25px;">

<h3>
    {{ t.status }}
</h3>


<form
    method="POST"
    action="{{ url_for('admin_update_student', student_id=student['id']) }}"
>

<div class="buttons"
     style="justify-content:flex-start;">

<button
    name="action"
    value="approved"
    class="btn btn-success"
>
    {{ t.approve }}
</button>


<button
    name="action"
    value="rejected"
    class="btn btn-danger"
>
    {{ t.reject }}
</button>


<button
    name="action"
    value="returned"
    class="btn btn-warning"
>
    {{ t.return }}
</button>

</div>

</form>


<form
    method="POST"
    action="{{ url_for('admin_send_message', student_id=student['id']) }}"
    style="margin-top:20px;"
>

<div class="form-group">

<label>
    {{ t.message }}
</label>

<textarea
    name="message"
    placeholder="{{ t.message }}"
></textarea>

</div>


<button
    class="btn btn-primary"
    style="margin-top:12px;"
>
    {{ t.send_message }}
</button>

</form>


{% if student["teacher_message"] %}

<div class="alert" style="margin-top:20px;">

<strong>
    {{ t.message }}
</strong>

<br><br>

{{ student["teacher_message"] }}

</div>

{% endif %}


</div>


<div class="buttons">

<a
    class="btn btn-dark"
    href="{{ url_for('admin_dashboard') }}"
>
    {{ t.dashboard }}
</a>

</div>


</div>

</div>

</section>

"""

    return render_page(
        content,
        title=LANG[current_lang()]["student_details"],
        student=student
    )


# ============================================================
# ADMIN UPDATE STUDENT STATUS
# ============================================================

@app.route(
    "/admin/student/<int:student_id>/update",
    methods=["POST"]
)
@admin_required
def admin_update_student(student_id):

    action = request.form.get(
        "action",
        ""
    ).strip()


    if action not in [
        "approved",
        "rejected",
        "returned"
    ]:

        abort(400)


    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    conn = get_db()

    conn.execute("""
        UPDATE students
        SET
            status = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        action,
        now,
        student_id
    ))

    conn.commit()
    conn.close()


    flash(
        LANG[current_lang()]["saved"]
    )


    return redirect(
        url_for(
            "admin_student_detail",
            student_id=student_id
        )
    )


# ============================================================
# ADMIN SEND MESSAGE
# ============================================================

@app.route(
    "/admin/student/<int:student_id>/message",
    methods=["POST"]
)
@admin_required
def admin_send_message(student_id):

    message = request.form.get(
        "message",
        ""
    ).strip()


    if not message:

        return redirect(
            url_for(
                "admin_student_detail",
                student_id=student_id
            )
        )


    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    conn = get_db()

    conn.execute("""
        UPDATE students
        SET
            teacher_message = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        message,
        now,
        student_id
    ))

    conn.commit()
    conn.close()


    flash(
        LANG[current_lang()]["saved"]
    )


    return redirect(
        url_for(
            "admin_student_detail",
            student_id=student_id
        )
    )


# ============================================================
# PROTECTED UPLOAD VIEW
# ============================================================

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    # Student only sees own documents indirectly through
    # their dashboard; admin can see documents after login.
    #
    # This route intentionally does NOT expose uploads publicly
    # without authentication.

    if not session.get("admin_logged_in") and not session.get("student_id"):
        abort(403)


    safe_name = os.path.basename(filename)

    return send_from_directory(
        UPLOAD_FOLDER,
        safe_name
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    content = """

<section class="section">

<div class="container">

<div class="form-card" style="text-align:center;">

<div style="font-size:60px;">
    404
</div>

<h1>
    Page Not Found
</h1>

<p>
    The requested page could not be found.
</p>

<div class="buttons">

<a
    class="btn btn-primary"
    href="{{ url_for('home') }}"
>
    {{ t.home }}
</a>

</div>

</div>

</div>

</section>

"""

    return render_page(
        content,
        title="404"
    ), 404


@app.errorhandler(403)
def forbidden(error):

    content = """

<section class="section">

<div class="container">

<div class="form-card" style="text-align:center;">

<div style="font-size:60px;">
    🔐
</div>

<h1>
    Access Denied
</h1>

<p>
    You do not have permission to view this resource.
</p>

</div>

</div>

</section>

"""

    return render_page(
        content,
        title="Access Denied"
    ), 403


@app.errorhandler(413)
def too_large(error):

    flash(
        "File size is too large. Maximum request size is 10 MB."
    )

    return redirect(
        url_for("register")
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print(" AMBUYEE SECONDARY SCHOOL ONLINE SYSTEM")
    print("=" * 65)
    print()
    print("Local website:")
    print("http://127.0.0.1:8080")
    print()
    print("Student registration:")
    print("http://127.0.0.1:8080/register")
    print()
    print("Student login:")
    print("http://127.0.0.1:8080/student/login")
    print()
    print("Teacher/Admin login:")
    print("http://127.0.0.1:8080/admin/login")
    print()
    print("Database:")
    print(DATABASE)
    print()
    print("Uploads:")
    print(UPLOAD_FOLDER)
    print()
    print("IMPORTANT:")
    print("Change AMBUYEE_SECRET_KEY before production.")
    print("Set AMBUYEE_ADMIN_CODE to your own private teacher code.")
    print()
    print("=" * 65)
    print()

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
