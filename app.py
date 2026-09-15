import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session,
    render_template_string,
    send_from_directory,
    abort,
    flash
)

from werkzeug.utils import secure_filename


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "AMBUYEE_SECRET_KEY",
    "AMB-CHANGE-THIS-SECRET-BEFORE-PRODUCTION"
)


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "ambuyyee.db"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

MAX_FILE_SIZE = 10 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "pdf"
}


TEACHER_CODE = os.environ.get(
    "AMBUYEE_TEACHER_CODE",
    "AMB-TEACHER-DEMO"
)


DIRECTOR_CODE = os.environ.get(
    "AMBUYEE_DIRECTOR_CODE",
    "AMB-DIRECTOR-DEMO"
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
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


# =========================================================
# TRANSLATIONS
# =========================================================

TRANSLATIONS = {

    "om": {

        "home": "Fuula Jalqabaa",
        "register": "Galmee Barataa",
        "student_login": "Seensa Barataa",
        "teacher_login": "Seensa Barsiisaa",
        "director_login": "Seensa Direktera",

        "school_name":
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee",

        "student_registration":
            "Galmee Barattootaa Online",

        "start_registration":
            "Galmee Jalqabi",

        "student_portal":
            "Student Portal",

        "teacher_portal":
            "Teacher Portal",

        "director_portal":
            "Director Portal",

        "full_name":
            "Maqaa Guutuu",

        "phone":
            "Lakkoofsa Bilbila",

        "national_id":
            "National ID",

        "age":
            "Umurii",

        "gender":
            "Saala",

        "male":
            "Dhiira",

        "female":
            "Dubartii",

        "kebele":
            "Kebele / Ganda",

        "zone":
            "Zone / Zoonii",

        "grade":
            "Kutaa Barnootaa",

        "class":
            "Kutaa",

        "stream":
            "Stream",

        "natural":
            "Natural Science",

        "social":
            "Social Science",

        "card_front":
            "School Card - Fuuldura",

        "card_back":
            "School Card - Duuba",

        "face_photo":
            "Suuraa Fuula Barataa",

        "ministry_document":
            "Ministry Document",

        "payment":
            "Ragaa Kaffaltii",

        "submit":
            "Galmee Ergi",

        "login":
            "Seeni",

        "logout":
            "Ba'i",

        "student_code":
            "Koodii Barataa",

        "registration_code":
            "Koodii Galmee",

        "pending":
            "Eeggat",

        "approved":
            "Fudhatame",

        "rejected":
            "Didame",

        "returned":
            "Deebi'e",

        "total_students":
            "Barattoota Hunda",

        "total_pending":
            "Eeggat",

        "total_approved":
            "Fudhatame",

        "total_rejected":
            "Didame",

        "total_returned":
            "Deebi'e",

        "teacher_dashboard":
            "Teacher Dashboard",

        "director_dashboard":
            "Director Dashboard",

        "student_dashboard":
            "Student Dashboard",

        "search":
            "Barbaadi",

        "filter":
            "Filter",

        "all":
            "Hunda",

        "select_grade":
            "Kutaa Filadhu",

        "select_class":
            "Class Filadhu",

        "select_status":
            "Haala Filadhu",

        "students_by_class":
            "Barattoota Kutaa Kutaan",

        "class_statistics":
            "Lakkoofsa Barattootaa Kutaa Kutaan",

        "boys":
            "Dhiira",

        "girls":
            "Dubartii",

        "count":
            "Lakkoofsa",

        "view":
            "Ilaali",

        "approve":
            "Fudhu",

        "reject":
            "Didi",

        "return":
            "Deebisi",

        "message":
            "Ergaa",

        "send_message":
            "Ergaa Ergi",

        "download_pdf":
            "PDF Buufadhu",

        "class_pdf":
            "PDF Kutaa Kana Buufadhu",

        "no_students":
            "Barataan hin argamne.",

        "student_details":
            "Odeeffannoo Barataa",

        "success":
            "Baga gammaddan! Galmeen keessan milkaa'eera.",

        "wrong_code":
            "Koodiin sirrii miti.",

        "required":
            "Dirqama",

        "status":
            "Haala",

        "about":
            "Waa'ee Mana Barumsaa",

        "about_text":
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee keessatti "
            "tajaajila barnootaa qulqullina qabu, sirna galmee ifa "
            "ta'e fi bulchiinsa barattootaa ammayyaa diriirsuuf "
            "hojjetamaa jira. Sirni kun barattoonni mana isaanii "
            "irraa galmee online akka guutan, sanadoota barbaachisan "
            "akka ergan, barsiisotni odeeffannoo akka mirkaneessan "
            "fi hoggansi mana barumsaa haala barattootaa "
            "statisticaan akka hordofu gargaara.",

        "founder":
            "Founder — Ammaar Naziif"
    },


    "am": {

        "home": "መነሻ ገጽ",
        "register": "የተማሪ ምዝገባ",
        "student_login": "የተማሪ መግቢያ",
        "teacher_login": "የመምህር መግቢያ",
        "director_login": "የዳይሬክተር መግቢያ",

        "school_name":
            "አምቡዬ 2ኛ ደረጃ ትምህርት ቤት",

        "student_registration":
            "የተማሪዎች የመስመር ላይ ምዝገባ",

        "start_registration":
            "ምዝገባ ጀምር",

        "student_portal":
            "የተማሪ ፖርታል",

        "teacher_portal":
            "የመምህር ፖርታል",

        "director_portal":
            "የዳይሬክተር ፖርታል",

        "full_name":
            "ሙሉ ስም",

        "phone":
            "ስልክ ቁጥር",

        "national_id":
            "ብሔራዊ መታወቂያ",

        "age":
            "ዕድሜ",

        "gender":
            "ፆታ",

        "male":
            "ወንድ",

        "female":
            "ሴት",

        "kebele":
            "ቀበሌ",

        "zone":
            "ዞን",

        "grade":
            "ክፍል",

        "class":
            "ክላስ",

        "stream":
            "የትምህርት ዘርፍ",

        "natural":
            "Natural Science",

        "social":
            "Social Science",

        "card_front":
            "የተማሪ መታወቂያ - ፊት",

        "card_back":
            "የተማሪ መታወቂያ - ጀርባ",

        "face_photo":
            "የተማሪ ፎቶ",

        "ministry_document":
            "የሚኒስቴር ሰነድ",

        "payment":
            "የክፍያ ማረጋገጫ",

        "submit":
            "ምዝገባ ላክ",

        "login":
            "ግባ",

        "logout":
            "ውጣ",

        "student_code":
            "የተማሪ ኮድ",

        "registration_code":
            "የምዝገባ ኮድ",

        "pending":
            "በመጠባበቅ ላይ",

        "approved":
            "ተቀባይነት አግኝቷል",

        "rejected":
            "ተቀባይነት አላገኘም",

        "returned":
            "ተመልሷል",

        "total_students":
            "ጠቅላላ ተማሪዎች",

        "total_pending":
            "በመጠባበቅ ላይ",

        "total_approved":
            "የተቀበሉ",

        "total_rejected":
            "የተከለከሉ",

        "total_returned":
            "የተመለሱ",

        "teacher_dashboard":
            "የመምህር Dashboard",

        "director_dashboard":
            "የዳይሬክተር Dashboard",

        "student_dashboard":
            "የተማሪ Dashboard",

        "search":
            "ፈልግ",

        "filter":
            "ማጣሪያ",

        "all":
            "ሁሉም",

        "select_grade":
            "ክፍል ምረጥ",

        "select_class":
            "ክላስ ምረጥ",

        "select_status":
            "ሁኔታ ምረጥ",

        "students_by_class":
            "ተማሪዎች በክላስ",

        "class_statistics":
            "የክላስ ተማሪዎች ቁጥር",

        "boys":
            "ወንዶች",

        "girls":
            "ሴቶች",

        "count":
            "ቁጥር",

        "view":
            "እይ",

        "approve":
            "ተቀበል",

        "reject":
            "ከልክል",

        "return":
            "መልስ",

        "message":
            "መልዕክት",

        "send_message":
            "መልዕክት ላክ",

        "download_pdf":
            "PDF አውርድ",

        "class_pdf":
            "የዚህን ክላስ PDF አውርድ",

        "no_students":
            "ተማሪ አልተገኘም።",

        "student_details":
            "የተማሪ መረጃ",

        "success":
            "እንኳን ደስ አለዎት! ምዝገባዎ ተሳክቷል።",

        "wrong_code":
            "ኮዱ ትክክል አይደለም።",

        "required":
            "አስፈላጊ",

        "status":
            "ሁኔታ",

        "about":
            "ስለ ትምህርት ቤቱ",

        "about_text":
            "አምቡዬ 2ኛ ደረጃ ትምህርት ቤት ጥራት ያለው "
            "የትምህርት አገልግሎት፣ ግልጽ የምዝገባ ስርዓት "
            "እና ዘመናዊ የተማሪ አስተዳደር ለማቋቋም "
            "እየሰራ ነው።",

        "founder":
            "Founder — Ammaar Naziif"
    },


    "en": {

        "home": "Home",
        "register": "Student Registration",
        "student_login": "Student Login",
        "teacher_login": "Teacher Login",
        "director_login": "Director Login",

        "school_name":
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee",

        "student_registration":
            "Online Student Registration",

        "start_registration":
            "Start Registration",

        "student_portal":
            "Student Portal",

        "teacher_portal":
            "Teacher Portal",

        "director_portal":
            "Director Portal",

        "full_name":
            "Full Name",

        "phone":
            "Phone Number",

        "national_id":
            "National ID",

        "age":
            "Age",

        "gender":
            "Gender",

        "male":
            "Male",

        "female":
            "Female",

        "kebele":
            "Kebele",

        "zone":
            "Zone",

        "grade":
            "Grade",

        "class":
            "Class",

        "stream":
            "Stream",

        "natural":
            "Natural Science",

        "social":
            "Social Science",

        "card_front":
            "School Card - Front",

        "card_back":
            "School Card - Back",

        "face_photo":
            "Student Face Photo",

        "ministry_document":
            "Ministry Document",

        "payment":
            "Payment Proof",

        "submit":
            "Submit Registration",

        "login":
            "Login",

        "logout":
            "Logout",

        "student_code":
            "Student Code",

        "registration_code":
            "Registration Code",

        "pending":
            "Pending",

        "approved":
            "Approved",

        "rejected":
            "Rejected",

        "returned":
            "Returned",

        "total_students":
            "Total Students",

        "total_pending":
            "Pending",

        "total_approved":
            "Approved",

        "total_rejected":
            "Rejected",

        "total_returned":
            "Returned",

        "teacher_dashboard":
            "Teacher Dashboard",

        "director_dashboard":
            "Director Dashboard",

        "student_dashboard":
            "Student Dashboard",

        "search":
            "Search",

        "filter":
            "Filter",

        "all":
            "All",

        "select_grade":
            "Select Grade",

        "select_class":
            "Select Class",

        "select_status":
            "Select Status",

        "students_by_class":
            "Students by Class",

        "class_statistics":
            "Class Statistics",

        "boys":
            "Boys",

        "girls":
            "Girls",

        "count":
            "Count",

        "view":
            "View",

        "approve":
            "Approve",

        "reject":
            "Reject",

        "return":
            "Return",

        "message":
            "Message",

        "send_message":
            "Send Message",

        "download_pdf":
            "Download PDF",

        "class_pdf":
            "Download Class PDF",

        "no_students":
            "No students found.",

        "student_details":
            "Student Details",

        "success":
            "Congratulations! Your registration was successful.",

        "wrong_code":
            "The code is incorrect.",

        "required":
            "Required",

        "status":
            "Status",

        "about":
            "About the School",

        "about_text":
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee is working "
            "to provide quality education, transparent registration "
            "and modern student management. This system allows "
            "students to register online, submit required documents, "
            "teachers to verify information and school leadership "
            "to monitor student statistics.",

        "founder":
            "Founder — Ammaar Naziif"
    }
}


def get_lang():

    lang = request.args.get("lang")

    if lang in TRANSLATIONS:
        session["lang"] = lang

    return session.get(
        "lang",
        "om"
    )


def t(key):

    lang = get_lang()

    return TRANSLATIONS.get(
        lang,
        TRANSLATIONS["om"]
    ).get(
        key,
        key
    )


@app.context_processor
def inject_globals():

    return {
        "t": t,
        "lang": get_lang()
    }


# =========================================================
# HELPERS
# =========================================================

def hash_code(code):

    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def allowed_file(filename):

    if not filename or "." not in filename:
        return False

    ext = filename.rsplit(
        ".",
        1
    )[1].lower()

    return ext in ALLOWED_EXTENSIONS


def save_uploaded(file, prefix):

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    original = secure_filename(
        file.filename
    )

    if "." not in original:
        return None

    ext = original.rsplit(
        ".",
        1
    )[1].lower()

    filename = (
        prefix
        + "_"
        + secrets.token_hex(10)
        + "."
        + ext
    )

    path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    file.save(path)

    return filename


def generate_registration_code():

    while True:

        code = (
            "AMB-"
            + secrets.token_hex(5).upper()
        )

        conn = get_db()

        row = conn.execute(
            """
            SELECT id
            FROM students
            WHERE registration_code=?
            """,
            (code,)
        ).fetchone()

        conn.close()

        if not row:
            return code


def student_logged():

    return "student_id" in session


def teacher_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if session.get(
            "teacher_logged"
        ) is not True:

            return redirect(
                url_for("teacher_login")
            )

        return fn(*args, **kwargs)

    return wrapper


def director_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if session.get(
            "director_logged"
        ) is not True:

            return redirect(
                url_for("director_login")
            )

        return fn(*args, **kwargs)

    return wrapper


# =========================================================
# STATUS HELPERS
# =========================================================

def status_text(status):

    mapping = {
        "pending": t("pending"),
        "approved": t("approved"),
        "rejected": t("rejected"),
        "returned": t("returned")
    }

    return mapping.get(
        status,
        status
    )


@app.context_processor
def status_globals():

    return {
        "status_text": status_text
    }


# =========================================================
# PROFESSIONAL DESIGN
# =========================================================

BASE_STYLE = """

<style>

:root {
    --bg: #050a12;
    --bg2: #091321;
    --card: rgba(15, 27, 44, .92);
    --card2: #101e31;
    --border: rgba(214, 174, 87, .18);
    --gold: #d8b463;
    --gold2: #f0d38d;
    --text: #f5f7fa;
    --muted: #9ba8ba;
    --blue: #1b3150;
    --green: #25865b;
    --red: #a63f47;
    --orange: #b56e2f;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {

    margin: 0;

    font-family:
        Arial,
        "Noto Sans",
        sans-serif;

    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(216,180,99,.12),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(31,77,125,.15),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #040911,
            #081321 50%,
            #050a12
        );

    color: var(--text);

    min-height: 100vh;
}

a {
    text-decoration: none;
}

.nav {

    position: sticky;

    top: 0;

    z-index: 100;

    background:
        rgba(5, 11, 19, .92);

    backdrop-filter:
        blur(16px);

    border-bottom:
        1px solid
        rgba(216,180,99,.18);

    padding:
        14px 5%;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 15px;

    flex-wrap: wrap;
}

.logo {

    color: var(--gold2);

    font-size: 20px;

    font-weight: 800;

    letter-spacing: 1px;

    display: flex;

    align-items: center;

    gap: 8px;
}

.logo::before {

    content: "";

    width: 9px;

    height: 9px;

    border-radius: 50%;

    background: var(--gold);

    box-shadow:
        0 0 15px
        rgba(216,180,99,.7);
}

.navlinks {

    display: flex;

    gap: 5px;

    flex-wrap: wrap;

    align-items: center;
}

.navlinks a {

    color: #dbe2eb;

    padding:
        8px 11px;

    border-radius: 8px;

    font-size: 13px;

    transition: .2s;
}

.navlinks a:hover {

    color: var(--gold2);

    background:
        rgba(216,180,99,.09);
}

.container {

    width: 92%;

    max-width: 1280px;

    margin:
        32px auto;
}

.hero {

    position: relative;

    overflow: hidden;

    padding:
        70px 42px;

    border-radius: 26px;

    background:

        linear-gradient(
            135deg,
            rgba(17,32,53,.98),
            rgba(8,18,31,.96)
        );

    border:
        1px solid
        rgba(216,180,99,.20);

    box-shadow:
        0 30px 80px
        rgba(0,0,0,.35);
}

.hero::before {

    content: "";

    position: absolute;

    width: 300px;

    height: 300px;

    right: -100px;

    top: -130px;

    border-radius: 50%;

    background:
        rgba(216,180,99,.10);

    filter: blur(10px);
}

.hero::after {

    content: "";

    position: absolute;

    width: 180px;

    height: 180px;

    left: -80px;

    bottom: -100px;

    border-radius: 50%;

    background:
        rgba(50,105,170,.12);
}

.hero h1 {

    position: relative;

    z-index: 1;

    color: var(--gold2);

    font-size:
        clamp(30px, 5vw, 52px);

    line-height: 1.1;

    margin:
        0 0 15px;
}

.hero h2 {

    position: relative;

    z-index: 1;

    font-size: 25px;

    margin:
        0 0 15px;
}

.hero p {

    position: relative;

    z-index: 1;

    color: #b9c4d2;

    line-height: 1.9;

    max-width: 850px;
}

.btn {

    display: inline-block;

    padding:
        11px 17px;

    border-radius: 9px;

    background:
        linear-gradient(
            135deg,
            #e2c477,
            #bd9445
        );

    color: #111;

    border: none;

    cursor: pointer;

    font-weight: 800;

    margin: 4px;

    transition:
        transform .2s,
        box-shadow .2s,
        opacity .2s;

    box-shadow:
        0 7px 20px
        rgba(216,180,99,.12);
}

.btn:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 10px 25px
        rgba(216,180,99,.20);

    opacity: .95;
}

.btn.dark {

    background:
        #122238;

    color: #f4f7fa;

    border:
        1px solid
        #2e435d;

    box-shadow: none;
}

.btn.green {

    background:
        linear-gradient(
            135deg,
            #299464,
            #176b46
        );

    color: white;
}

.btn.red {

    background:
        linear-gradient(
            135deg,
            #b34d53,
            #823139
        );

    color: white;
}

.btn.orange {

    background:
        linear-gradient(
            135deg,
            #c17a36,
            #8e501f
        );

    color: white;
}

.card {

    background:
        linear-gradient(
            145deg,
            rgba(16,31,50,.96),
            rgba(10,22,37,.96)
        );

    border:
        1px solid
        var(--border);

    border-radius: 18px;

    padding: 23px;

    margin-bottom: 20px;

    box-shadow:
        0 18px 45px
        rgba(0,0,0,.20);
}

.card h1,
.card h2 {

    color: var(--gold2);
}

.card h1 {

    margin-top: 0;
}

.grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(210px, 1fr)
        );

    gap: 15px;
}

.stat {

    position: relative;

    overflow: hidden;

    background:
        linear-gradient(
            145deg,
            #11243b,
            #0b192b
        );

    border:
        1px solid
        rgba(216,180,99,.14);

    border-radius: 15px;

    padding: 21px;
}

.stat::after {

    content: "";

    position: absolute;

    width: 75px;

    height: 75px;

    right: -25px;

    top: -25px;

    border-radius: 50%;

    background:
        rgba(216,180,99,.07);
}

.stat h3 {

    color: var(--muted);

    margin-top: 0;

    font-size: 14px;
}

.stat strong {

    font-size: 34px;

    color: var(--gold2);
}

input,
select,
textarea {

    width: 100%;

    padding: 13px 14px;

    background:
        rgba(4,12,22,.90);

    border:
        1px solid
        #30455f;

    color: white;

    border-radius: 9px;

    margin-top: 7px;

    margin-bottom: 17px;

    outline: none;

    transition:
        border .2s,
        box-shadow .2s;
}

input:focus,
select:focus,
textarea:focus {

    border-color:
        var(--gold);

    box-shadow:
        0 0 0 3px
        rgba(216,180,99,.08);
}

select option {

    background: #0c1828;

    color: white;
}

textarea {

    min-height: 115px;

    resize: vertical;
}

label {

    font-weight: 700;

    color: #dce3eb;
}

input[type="file"] {

    padding: 10px;

    cursor: pointer;
}

table {

    width: 100%;

    border-collapse: collapse;

    min-width: 800px;
}

th,
td {

    padding: 12px;

    border-bottom:
        1px solid
        #26384e;

    text-align: left;
}

th {

    color: var(--gold2);

    background:
        #12243a;

    font-size: 13px;
}

tbody tr {

    transition: background .15s;
}

tbody tr:hover {

    background:
        rgba(216,180,99,.045);
}

.table-wrap {

    overflow-x: auto;

    border-radius: 12px;
}

.badge {

    display: inline-block;

    padding:
        5px 10px;

    border-radius: 30px;

    font-size: 11px;

    font-weight: 800;

    text-transform: uppercase;
}

.badge.pending {

    background:
        rgba(161,124,42,.25);

    color:
        #e6c66e;
}

.badge.approved {

    background:
        rgba(37,134,91,.22);

    color:
        #62d59d;
}

.badge.rejected {

    background:
        rgba(166,63,71,.25);

    color:
        #f08088;
}

.badge.returned {

    background:
        rgba(181,110,47,.24);

    color:
        #e5a35e;
}

.preview {

    width: 230px;

    max-width: 100%;

    max-height: 280px;

    object-fit: cover;

    border-radius: 14px;

    border:
        1px solid
        rgba(216,180,99,.25);

    box-shadow:
        0 15px 35px
        rgba(0,0,0,.30);
}

.alert {

    background:
        linear-gradient(
            135deg,
            #142d47,
            #102238
        );

    border:
        1px solid
        #36597a;

    padding: 14px 16px;

    border-radius: 10px;

    margin-bottom: 16px;

    color: #dce8f5;
}

.success-box {

    text-align: center;

    padding: 40px 20px;
}

.code-box {

    display: inline-block;

    padding:
        15px 25px;

    margin:
        10px 0 20px;

    border-radius: 12px;

    background:
        #071321;

    border:
        1px solid
        rgba(216,180,99,.35);

    color:
        var(--gold2);

    font-size: 25px;

    font-weight: 900;

    letter-spacing: 2px;
}

.section-title {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 10px;

    flex-wrap: wrap;
}

.muted {

    color:
        var(--muted);
}

footer {

    margin-top: 55px;

    padding:
        30px 20px;

    text-align: center;

    color:
        #8492a5;

    border-top:
        1px solid
        rgba(216,180,99,.13);

    line-height: 1.8;
}

.footer-gold {

    color:
        var(--gold);
}

@media(max-width: 700px) {

    .nav {

        padding:
            12px 4%;

    }

    .navlinks {

        width: 100%;
    }

    .navlinks a {

        font-size: 12px;

        padding:
            7px 8px;
    }

    .container {

        width: 94%;

        margin-top: 20px;
    }

    .hero {

        padding:
            42px 22px;
    }

    .hero h1 {

        font-size: 31px;
    }

    .card {

        padding:
            17px;
    }

    .stat strong {

        font-size: 29px;
    }
}

</style>
"""


# =========================================================
# PAGE WRAPPER
# =========================================================

def page(title, body):

    return render_template_string(

        """
        <!doctype html>

        <html lang="{{ lang }}">

        <head>

            <meta charset="utf-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1"
            >

            <meta
                name="theme-color"
                content="#050a12"
            >

            <title>{{ title }} | Ambuyyee</title>

        """ + BASE_STYLE + """

        </head>

        <body>

        <nav class="nav">

            <a
                class="logo"
                href="{{ url_for('home') }}"
            >
                AMBUYEE
            </a>

            <div class="navlinks">

                <a href="{{ url_for('home') }}">
                    {{ t('home') }}
                </a>

                <a href="{{ url_for('register') }}">
                    {{ t('register') }}
                </a>

                <a href="{{ url_for('student_login') }}">
                    {{ t('student_login') }}
                </a>

                <a href="{{ url_for('teacher_login') }}">
                    {{ t('teacher_login') }}
                </a>

                <a href="{{ url_for('director_login') }}">
                    {{ t('director_login') }}
                </a>

                <a href="?lang=om">OR</a>

                <a href="?lang=am">አማ</a>

                <a href="?lang=en">EN</a>

            </div>

        </nav>


        <main class="container">

            {% with messages =
                get_flashed_messages()
            %}

                {% if messages %}

                    {% for message in messages %}

                        <div class="alert">
                            {{ message }}
                        </div>

                    {% endfor %}

                {% endif %}

            {% endwith %}


            """ + body + """


        </main>


        <footer>

            <div class="footer-gold">
                {{ t('school_name') }}
            </div>

            <div>
                {{ t('founder') }}
            </div>

        </footer>


        </body>

        </html>
        """,

        title=title
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    body = """

    <section class="hero">

        <h1>
            {{ t('school_name') }}
        </h1>

        <h2>
            {{ t('student_registration') }}
        </h2>

        <p>
            {{ t('about_text') }}
        </p>

        <br>

        <a
            class="btn"
            href="{{ url_for('register') }}"
        >
            {{ t('start_registration') }}
        </a>

        <a
            class="btn dark"
            href="{{ url_for('student_login') }}"
        >
            {{ t('student_portal') }}
        </a>

        <a
            class="btn dark"
            href="{{ url_for('teacher_login') }}"
        >
            {{ t('teacher_portal') }}
        </a>

        <a
            class="btn dark"
            href="{{ url_for('director_login') }}"
        >
            {{ t('director_portal') }}
        </a>

    </section>


    <div class="card">

        <h2>
            {{ t('about') }}
        </h2>

        <p class="muted">
            {{ t('about_text') }}
        </p>

    </div>

    """

    return page(
        t("home"),
        body
    )


# =========================================================
# STUDENT REGISTRATION
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        national_id = request.form.get(
            "national_id",
            ""
        ).strip()

        age = request.form.get(
            "age",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        kebele = request.form.get(
            "kebele",
            ""
        ).strip()

        zone = request.form.get(
            "zone",
            ""
        ).strip()

        grade = request.form.get(
            "grade",
            ""
        ).strip()

        class_name = request.form.get(
            "class_name",
            ""
        ).strip()

        stream = request.form.get(
            "stream",
            ""
        ).strip()

        student_code = request.form.get(
            "student_code",
            ""
        ).strip()


        card_front = request.files.get(
            "card_front"
        )

        card_back = request.files.get(
            "card_back"
        )

        face_photo = request.files.get(
            "face_photo"
        )

        ministry = request.files.get(
            "ministry_document"
        )

        payment = request.files.get(
            "payment_screenshot"
        )


        required_values = [

            full_name,
            phone,
            national_id,
            age,
            gender,
            kebele,
            zone,
            grade,
            class_name,
            student_code

        ]


        if not all(required_values):

            flash(
                t("required")
            )

            return redirect(
                url_for("register")
            )


        if len(student_code) < 6:

            flash(
                "Student code must contain "
                "at least 6 characters."
            )

            return redirect(
                url_for("register")
            )


        try:

            age_int = int(age)

        except ValueError:

            flash(
                "Age must be a number."
            )

            return redirect(
                url_for("register")
            )


        if age_int < 1 or age_int > 100:

            flash(
                "Please enter a valid age."
            )

            return redirect(
                url_for("register")
            )


        if grade not in [
            "9",
            "10",
            "11",
            "12"
        ]:

            flash(
                "Invalid grade."
            )

            return redirect(
                url_for("register")
            )


        if class_name not in [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F"
        ]:

            flash(
                "Invalid class."
            )

            return redirect(
                url_for("register")
            )


        if grade in ["11", "12"]:

            if stream not in [
                "Natural Science",
                "Social Science"
            ]:

                flash(
                    "Please select a stream."
                )

                return redirect(
                    url_for("register")
                )


        if grade == "9":

            if (
                not ministry
                or not ministry.filename
            ):

                flash(
                    "Ministry document is required for Grade 9."
                )

                return redirect(
                    url_for("register")
                )


            if (
                not payment
                or not payment.filename
            ):

                flash(
                    "Payment screenshot is required for Grade 9."
                )

                return redirect(
                    url_for("register")
                )


        if (
            not card_front
            or not card_front.filename
        ):

            flash(
                "School card front is required."
            )

            return redirect(
                url_for("register")
            )


        if (
            not card_back
            or not card_back.filename
        ):

            flash(
                "School card back is required."
            )

            return redirect(
                url_for("register")
            )


        if (
            not face_photo
            or not face_photo.filename
        ):

            flash(
                "Face photo is required."
            )

            return redirect(
                url_for("register")
            )


        # Validate files before saving

        required_files = [
            card_front,
            card_back,
            face_photo
        ]

        for file in required_files:

            if not allowed_file(
                file.filename
            ):

                flash(
                    "One or more files have "
                    "an unsupported format."
                )

                return redirect(
                    url_for("register")
                )


        if ministry and ministry.filename:

            if not allowed_file(
                ministry.filename
            ):

                flash(
                    "Invalid ministry document."
                )

                return redirect(
                    url_for("register")
                )


        if payment and payment.filename:

            if not allowed_file(
                payment.filename
            ):

                flash(
                    "Invalid payment file."
                )

                return redirect(
                    url_for("register")
                )


        reg_code = generate_registration_code()

        prefix = reg_code.replace(
            "-",
            "_"
        )


        front_name = save_uploaded(
            card_front,
            prefix + "_front"
        )

        back_name = save_uploaded(
            card_back,
            prefix + "_back"
        )

        face_name = save_uploaded(
            face_photo,
            prefix + "_face"
        )


        ministry_name = None

        payment_name = None


        if ministry and ministry.filename:

            ministry_name = save_uploaded(
                ministry,
                prefix + "_ministry"
            )


        if payment and payment.filename:

            payment_name = save_uploaded(
                payment,
                prefix + "_payment"
            )


        if not all([
            front_name,
            back_name,
            face_name
        ]):

            flash(
                "One or more uploaded files are invalid."
            )

            return redirect(
                url_for("register")
            )


        conn = get_db()


        try:

            conn.execute(
                """

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
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?
                )

                """,

                (

                    reg_code,
                    phone,
                    hash_code(student_code),
                    full_name,
                    national_id,
                    age_int,
                    gender,
                    kebele,
                    zone,
                    grade,
                    class_name,
                    stream,
                    front_name,
                    back_name,
                    face_name,
                    ministry_name,
                    payment_name,
                    "pending",
                    "",
                    datetime.now().isoformat(),
                    datetime.now().isoformat()

                )
            )


            conn.commit()


        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "Registration could not be completed."
            )

            return redirect(
                url_for("register")
            )


        conn.close()


        body = """

        <div class="card success-box">

            <h1>
                {{ t('success') }}
            </h1>

            <p class="muted">
                {{ t('registration_code') }}
            </p>

            <div class="code-box">
                {{ reg_code }}
            </div>

            <p>
                Keep this registration code safe.
                You will need it when you log in.
            </p>

            <a
                class="btn"
                href="{{ url_for('student_login') }}"
            >
                {{ t('student_login') }}
            </a>

        </div>

        """


        return page(

            t("success"),

            render_template_string(
                body,
                reg_code=reg_code
            )

        )


    # =====================================================
    # REGISTRATION FORM
    # =====================================================

    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <h1>
                    {{ t('register') }}
                </h1>

                <p class="muted">
                    Fill in all required information carefully.
                </p>

            </div>

        </div>


        <form
            method="POST"
            enctype="multipart/form-data"
        >


            <div class="grid">

                <div>

                    <label>
                        {{ t('full_name') }} *
                    </label>

                    <input
                        name="full_name"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('phone') }} *
                    </label>

                    <input
                        name="phone"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('national_id') }} *
                    </label>

                    <input
                        name="national_id"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('age') }} *
                    </label>

                    <input
                        name="age"
                        type="number"
                        min="1"
                        max="100"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('gender') }} *
                    </label>

                    <select
                        name="gender"
                        required
                    >

                        <option value="">
                            --
                        </option>

                        <option value="Male">
                            {{ t('male') }}
                        </option>

                        <option value="Female">
                            {{ t('female') }}
                        </option>

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('kebele') }} *
                    </label>

                    <input
                        name="kebele"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('zone') }} *
                    </label>

                    <input
                        name="zone"
                        required
                    >

                </div>


                <div>

                    <label>
                        {{ t('grade') }} *
                    </label>

                    <select
                        name="grade"
                        required
                    >

                        <option value="">
                            --
                        </option>

                        <option value="9">
                            Grade 9
                        </option>

                        <option value="10">
                            Grade 10
                        </option>

                        <option value="11">
                            Grade 11
                        </option>

                        <option value="12">
                            Grade 12
                        </option>

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('class') }} *
                    </label>

                    <select
                        name="class_name"
                        required
                    >

                        <option value="">
                            --
                        </option>

                        <option>A</option>
                        <option>B</option>
                        <option>C</option>
                        <option>D</option>
                        <option>E</option>
                        <option>F</option>

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('stream') }}
                    </label>

                    <select
                        name="stream"
                    >

                        <option value="">
                            --
                        </option>

                        <option value="Natural Science">
                            {{ t('natural') }}
                        </option>

                        <option value="Social Science">
                            {{ t('social') }}
                        </option>

                    </select>

                </div>

            </div>


            <div class="card">

                <h2>
                    Login Security
                </h2>

                <label>
                    {{ t('student_code') }} *
                </label>

                <input
                    name="student_code"
                    type="password"
                    minlength="6"
                    required
                >

                <p class="muted">
                    Use at least 6 characters.
                    Remember this code for your future login.
                </p>

            </div>


            <div class="card">

                <h2>
                    Required Documents
                </h2>


                <label>
                    {{ t('card_front') }} *
                </label>

                <input
                    type="file"
                    name="card_front"
                    accept=".jpg,.jpeg,.png,.pdf"
                    required
                >


                <label>
                    {{ t('card_back') }} *
                </label>

                <input
                    type="file"
                    name="card_back"
                    accept=".jpg,.jpeg,.png,.pdf"
                    required
                >


                <label>
                    {{ t('face_photo') }} *
                </label>

                <input
                    type="file"
                    name="face_photo"
                    accept=".jpg,.jpeg,.png"
                    required
                >


                <label>
                    {{ t('ministry_document') }}
                </label>

                <input
                    type="file"
                    name="ministry_document"
                    accept=".jpg,.jpeg,.png,.pdf"
                >


                <label>
                    {{ t('payment') }}
                </label>

                <input
                    type="file"
                    name="payment_screenshot"
                    accept=".jpg,.jpeg,.png,.pdf"
                >

            </div>


            <button
                class="btn"
                type="submit"
            >
                {{ t('submit') }}
            </button>


        </form>

    </div>

    """

    return page(
        t("register"),
        body
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route(
    "/student/login",
    methods=["GET", "POST"]
)
def student_login():

    if request.method == "POST":

        registration_code = request.form.get(
            "registration_code",
            ""
        ).strip()

        student_code = request.form.get(
            "student_code",
            ""
        ).strip()


        conn = get_db()


        student = conn.execute(
            """

            SELECT *

            FROM students

            WHERE registration_code=?

            AND code_hash=?

            """,

            (
                registration_code,
                hash_code(student_code)
            )

        ).fetchone()


        conn.close()


        if not student:

            flash(
                t("wrong_code")
            )

            return redirect(
                url_for("student_login")
            )


        session.clear()

        session["student_id"] = student["id"]

        return redirect(
            url_for("student_dashboard")
        )


    body = """

    <div
        class="card"
        style="max-width:550px;margin:40px auto;"
    >

        <h1>
            {{ t('student_login') }}
        </h1>

        <p class="muted">
            Enter your registration code and student code.
        </p>


        <form method="POST">

            <label>
                {{ t('registration_code') }}
            </label>

            <input
                name="registration_code"
                placeholder="AMB-XXXXXXXXXX"
                required
            >


            <label>
                {{ t('student_code') }}
            </label>

            <input
                type="password"
                name="student_code"
                required
            >


            <button
                class="btn"
                type="submit"
            >
                {{ t('login') }}
            </button>

        </form>

    </div>

    """

    return page(
        t("student_login"),
        body
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/student/dashboard")
def student_dashboard():

    if not student_logged():

        return redirect(
            url_for("student_login")
        )


    conn = get_db()


    student = conn.execute(
        """

        SELECT *

        FROM students

        WHERE id=?

        """,

        (
            session["student_id"],
        )

    ).fetchone()


    conn.close()


    if not student:

        session.clear()

        return redirect(
            url_for("student_login")
        )


    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <p
                    class="muted"
                    style="margin-bottom:5px;"
                >
                    {{ t('student_dashboard') }}
                </p>

                <h1>
                    {{ student['full_name'] }}
                </h1>

            </div>

            <a
                class="btn dark"
                href="{{ url_for('student_logout') }}"
            >
                {{ t('logout') }}
            </a>

        </div>


        <div class="grid">

            <div class="stat">

                <h3>
                    {{ t('registration_code') }}
                </h3>

                <strong
                    style="font-size:20px;"
                >
                    {{ student['registration_code'] }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('grade') }}
                </h3>

                <strong>
                    {{ student['grade'] }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('class') }}
                </h3>

                <strong>
                    {{ student['class_name'] }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('status') }}
                </h3>

                <span
                    class="badge
                    {{ student['status'] }}"
                >
                    {{ status_text(student['status']) }}
                </span>

            </div>

        </div>

    </div>


    <div class="card">

        <h2>
            {{ t('student_details') }}
        </h2>


        <div class="grid">

            <div>
                <p>
                    <strong>
                        {{ t('full_name') }}:
                    </strong>
                    {{ student['full_name'] }}
                </p>

                <p>
                    <strong>
                        {{ t('phone') }}:
                    </strong>
                    {{ student['phone'] }}
                </p>

                <p>
                    <strong>
                        {{ t('national_id') }}:
                    </strong>
                    {{ student['national_id'] }}
                </p>

                <p>
                    <strong>
                        {{ t('age') }}:
                    </strong>
                    {{ student['age'] }}
                </p>
            </div>


            <div>

                <p>
                    <strong>
                        {{ t('gender') }}:
                    </strong>
                    {{ student['gender'] }}
                </p>

                <p>
                    <strong>
                        {{ t('kebele') }}:
                    </strong>
                    {{ student['kebele'] }}
                </p>

                <p>
                    <strong>
                        {{ t('zone') }}:
                    </strong>
                    {{ student['zone'] }}
                </p>

                <p>
                    <strong>
                        {{ t('stream') }}:
                    </strong>
                    {{ student['stream'] or '-' }}
                </p>

            </div>

        </div>

    </div>


    {% if student['teacher_message'] %}

    <div class="card">

        <h2>
            {{ t('message') }}
        </h2>

        <div class="alert">

            {{ student['teacher_message'] }}

        </div>

    </div>

    {% endif %}


    <div class="card">

        <h2>
            {{ t('face_photo') }}
        </h2>

        <img
            class="preview"
            src="{{ url_for(
                'uploaded_file',
                filename=student['face_photo']
            ) }}"
        >

    </div>

    """

    return page(

        t("student_dashboard"),

        render_template_string(
            body,
            student=student
        )

    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/student/logout")
def student_logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# TEACHER LOGIN
# =========================================================

@app.route(
    "/teacher/login",
    methods=["GET", "POST"]
)
def teacher_login():

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()


        if code != TEACHER_CODE:

            flash(
                t("wrong_code")
            )

            return redirect(
                url_for("teacher_login")
            )


        session.clear()

        session["teacher_logged"] = True

        return redirect(
            url_for("teacher_dashboard")
        )


    body = """

    <div
        class="card"
        style="max-width:550px;margin:40px auto;"
    >

        <h1>
            {{ t('teacher_login') }}
        </h1>

        <p class="muted">
            Authorized teacher access only.
        </p>


        <form method="POST">

            <label>
                Teacher Code
            </label>

            <input
                type="password"
                name="code"
                required
            >


            <button
                class="btn"
                type="submit"
            >
                {{ t('login') }}
            </button>

        </form>

    </div>

    """

    return page(
        t("teacher_login"),
        body
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@app.route("/teacher/dashboard")
@teacher_required
def teacher_dashboard():

    grade = request.args.get(
        "grade",
        ""
    ).strip()

    class_name = request.args.get(
        "class_name",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()


    conn = get_db()


    total = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]


    pending = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='pending'
        """
    ).fetchone()[0]


    approved = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='approved'
        """
    ).fetchone()[0]


    rejected = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='rejected'
        """
    ).fetchone()[0]


    returned = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='returned'
        """
    ).fetchone()[0]


    # =====================================================
    # CLASS STATISTICS
    # =====================================================

    class_stats = []


    for g in [
        "9",
        "10",
        "11",
        "12"
    ]:

        for c in [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F"
        ]:


            total_c = conn.execute(
                """
                SELECT COUNT(*)
                FROM students
                WHERE grade=?
                AND class_name=?
                """,
                (g, c)
            ).fetchone()[0]


            boys = conn.execute(
                """
                SELECT COUNT(*)
                FROM students

                WHERE grade=?

                AND class_name=?

                AND gender IN (
                    'Male',
                    'male',
                    'Dhiira',
                    'ወንድ'
                )
                """,
                (g, c)
            ).fetchone()[0]


            girls = conn.execute(
                """
                SELECT COUNT(*)
                FROM students

                WHERE grade=?

                AND class_name=?

                AND gender IN (
                    'Female',
                    'female',
                    'Dubartii',
                    'ሴት'
                )
                """,
                (g, c)
            ).fetchone()[0]


            class_stats.append({

                "grade": g,

                "class": c,

                "total": total_c,

                "boys": boys,

                "girls": girls

            })


    # =====================================================
    # FILTERED STUDENTS
    # =====================================================

    query = """

        SELECT *

        FROM students

        WHERE 1=1

    """


    params = []


    if grade:

        query += """
            AND grade=?
        """

        params.append(
            grade
        )


    if class_name:

        query += """
            AND class_name=?
        """

        params.append(
            class_name
        )


    if status:

        query += """
            AND status=?
        """

        params.append(
            status
        )


    if search:

        query += """

            AND (

                full_name LIKE ?

                OR national_id LIKE ?

                OR phone LIKE ?

                OR registration_code LIKE ?

            )

        """

        term = (
            "%"
            + search
            + "%"
        )

        params.extend([
            term,
            term,
            term,
            term
        ])


    query += """

        ORDER BY
            full_name COLLATE NOCASE ASC

    """


    students = conn.execute(
        query,
        params
    ).fetchall()


    conn.close()


    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <p class="muted">
                    AMBUYEE • STAFF
                </p>

                <h1>
                    {{ t('teacher_dashboard') }}
                </h1>

            </div>


            <a
                class="btn dark"
                href="{{ url_for('teacher_logout') }}"
            >
                {{ t('logout') }}
            </a>

        </div>


        <div class="grid">

            <div class="stat">

                <h3>
                    {{ t('total_students') }}
                </h3>

                <strong>
                    {{ total }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_pending') }}
                </h3>

                <strong>
                    {{ pending }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_approved') }}
                </h3>

                <strong>
                    {{ approved }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_rejected') }}
                </h3>

                <strong>
                    {{ rejected }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_returned') }}
                </h3>

                <strong>
                    {{ returned }}
                </strong>

            </div>

        </div>

    </div>


    <!-- CLASS STATISTICS -->

    <div class="card">

        <div class="section-title">

            <h2>
                {{ t('class_statistics') }}
            </h2>

            <span class="muted">
                Grade 9 — 12
            </span>

        </div>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>
                            {{ t('grade') }}
                        </th>

                        <th>
                            {{ t('class') }}
                        </th>

                        <th>
                            {{ t('count') }}
                        </th>

                        <th>
                            {{ t('boys') }}
                        </th>

                        <th>
                            {{ t('girls') }}
                        </th>

                        <th>
                            PDF
                        </th>

                    </tr>

                </thead>


                <tbody>

                {% for row in class_stats %}

                    <tr>

                        <td>
                            Grade {{ row.grade }}
                        </td>

                        <td>
                            Class {{ row.class }}
                        </td>

                        <td>
                            <strong>
                                {{ row.total }}
                            </strong>
                        </td>

                        <td>
                            {{ row.boys }}
                        </td>

                        <td>
                            {{ row.girls }}
                        </td>

                        <td>

                            <a
                                class="btn"
                                href="{{ url_for(
                                    'teacher_pdf',
                                    grade=row.grade,
                                    class_name=row.class
                                ) }}"
                            >
                                PDF
                            </a>

                        </td>

                    </tr>

                {% endfor %}

                </tbody>

            </table>

        </div>

    </div>


    <!-- FILTER -->

    <div class="card">

        <h2>
            {{ t('filter') }}
        </h2>


        <form method="GET">

            <div class="grid">

                <div>

                    <label>
                        {{ t('select_grade') }}
                    </label>

                    <select name="grade">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        {% for g in [
                            '9',
                            '10',
                            '11',
                            '12'
                        ] %}

                            <option
                                value="{{ g }}"
                                {% if grade == g %}
                                    selected
                                {% endif %}
                            >
                                Grade {{ g }}
                            </option>

                        {% endfor %}

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('select_class') }}
                    </label>

                    <select name="class_name">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        {% for c in [
                            'A',
                            'B',
                            'C',
                            'D',
                            'E',
                            'F'
                        ] %}

                            <option
                                value="{{ c }}"
                                {% if class_name == c %}
                                    selected
                                {% endif %}
                            >
                                Class {{ c }}
                            </option>

                        {% endfor %}

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('select_status') }}
                    </label>

                    <select name="status">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        <option
                            value="pending"
                            {% if status == 'pending' %}
                                selected
                            {% endif %}
                        >
                            {{ t('pending') }}
                        </option>

                        <option
                            value="approved"
                            {% if status == 'approved' %}
                                selected
                            {% endif %}
                        >
                            {{ t('approved') }}
                        </option>

                        <option
                            value="rejected"
                            {% if status == 'rejected' %}
                                selected
                            {% endif %}
                        >
                            {{ t('rejected') }}
                        </option>

                        <option
                            value="returned"
                            {% if status == 'returned' %}
                                selected
                            {% endif %}
                        >
                            {{ t('returned') }}
                        </option>

                    </select>

                </div>

            </div>


            <label>
                {{ t('search') }}
            </label>

            <input
                name="search"
                value="{{ search }}"
                placeholder="Name / National ID / Phone / Registration Code"
            >


            <button
                class="btn"
                type="submit"
            >
                {{ t('search') }}
            </button>


            <a
                class="btn dark"
                href="{{ url_for('teacher_dashboard') }}"
            >
                Reset
            </a>

        </form>

    </div>


    <!-- STUDENT LIST -->

    <div class="card">

        <div class="section-title">

            <div>

                <h2>
                    {{ t('students_by_class') }}
                </h2>

                <p class="muted">
                    {{ students|length }}
                    students • alphabetical order
                </p>

            </div>

        </div>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>
                            {{ t('full_name') }}
                        </th>

                        <th>
                            {{ t('national_id') }}
                        </th>

                        <th>
                            {{ t('gender') }}
                        </th>

                        <th>
                            {{ t('phone') }}
                        </th>

                        <th>
                            {{ t('grade') }}
                        </th>

                        <th>
                            {{ t('class') }}
                        </th>

                        <th>
                            {{ t('status') }}
                        </th>

                        <th>
                            {{ t('view') }}
                        </th>

                    </tr>

                </thead>


                <tbody>

                {% for student in students %}

                    <tr>

                        <td>
                            {{ loop.index }}
                        </td>

                        <td>
                            <strong>
                                {{ student['full_name'] }}
                            </strong>
                        </td>

                        <td>
                            {{ student['national_id'] }}
                        </td>

                        <td>
                            {{ student['gender'] }}
                        </td>

                        <td>
                            {{ student['phone'] }}
                        </td>

                        <td>
                            {{ student['grade'] }}
                        </td>

                        <td>
                            {{ student['class_name'] }}
                        </td>

                        <td>

                            <span
                                class="badge
                                {{ student['status'] }}"
                            >
                                {{ status_text(
                                    student['status']
                                ) }}
                            </span>

                        </td>

                        <td>

                            <a
                                class="btn"
                                href="{{ url_for(
                                    'teacher_student',
                                    student_id=student['id']
                                ) }}"
                            >
                                {{ t('view') }}
                            </a>

                        </td>

                    </tr>

                {% else %}

                    <tr>

                        <td colspan="9">

                            {{ t('no_students') }}

                        </td>

                    </tr>

                {% endfor %}

                </tbody>

            </table>

        </div>

    </div>

    """


    return page(

        t("teacher_dashboard"),

        render_template_string(

            body,

            total=total,

            pending=pending,

            approved=approved,

            rejected=rejected,

            returned=returned,

            class_stats=class_stats,

            students=students,

            grade=grade,

            class_name=class_name,

            status=status,

            search=search

        )

    )


# =========================================================
# TEACHER STUDENT DETAIL
# =========================================================

@app.route(
    "/teacher/student/<int:student_id>"
)
@teacher_required
def teacher_student(student_id):

    conn = get_db()


    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE id=?
        """,
        (student_id,)
    ).fetchone()


    conn.close()


    if not student:

        abort(404)


    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <p class="muted">
                    {{ t('student_details') }}
                </p>

                <h1>
                    {{ student['full_name'] }}
                </h1>

            </div>

            <span
                class="badge
                {{ student['status'] }}"
            >
                {{ status_text(
                    student['status']
                ) }}
            </span>

        </div>


        <div class="grid">

            <div>

                <p>
                    <strong>
                        {{ t('registration_code') }}:
                    </strong>
                    {{ student['registration_code'] }}
                </p>

                <p>
                    <strong>
                        {{ t('phone') }}:
                    </strong>
                    {{ student['phone'] }}
                </p>

                <p>
                    <strong>
                        {{ t('national_id') }}:
                    </strong>
                    {{ student['national_id'] }}
                </p>

                <p>
                    <strong>
                        {{ t('age') }}:
                    </strong>
                    {{ student['age'] }}
                </p>

            </div>


            <div>

                <p>
                    <strong>
                        {{ t('gender') }}:
                    </strong>
                    {{ student['gender'] }}
                </p>

                <p>
                    <strong>
                        {{ t('grade') }}:
                    </strong>
                    {{ student['grade'] }}
                </p>

                <p>
                    <strong>
                        {{ t('class') }}:
                    </strong>
                    {{ student['class_name'] }}
                </p>

                <p>
                    <strong>
                        {{ t('stream') }}:
                    </strong>
                    {{ student['stream'] or '-' }}
                </p>

            </div>

        </div>

    </div>


    <!-- FACE -->

    <div class="card">

        <h2>
            {{ t('face_photo') }}
        </h2>

        <img
            class="preview"
            src="{{ url_for(
                'uploaded_file',
                filename=student['face_photo']
            ) }}"
        >

    </div>


    <!-- DOCUMENTS -->

    <div class="card">

        <h2>
            Documents
        </h2>


        <a
            class="btn"
            href="{{ url_for(
                'uploaded_file',
                filename=student['card_front']
            ) }}"
            target="_blank"
        >
            {{ t('card_front') }}
        </a>


        <a
            class="btn"
            href="{{ url_for(
                'uploaded_file',
                filename=student['card_back']
            ) }}"
            target="_blank"
        >
            {{ t('card_back') }}
        </a>


        {% if student['ministry_document'] %}

            <a
                class="btn"
                href="{{ url_for(
                    'uploaded_file',
                    filename=student['ministry_document']
                ) }}"
                target="_blank"
            >
                {{ t('ministry_document') }}
            </a>

        {% endif %}


        {% if student['payment_screenshot'] %}

            <a
                class="btn"
                href="{{ url_for(
                    'uploaded_file',
                    filename=student['payment_screenshot']
                ) }}"
                target="_blank"
            >
                {{ t('payment') }}
            </a>

        {% endif %}

    </div>


    <!-- STATUS -->

    <div class="card">

        <h2>
            Update Student Status
        </h2>


        <form
            method="POST"
            action="{{ url_for(
                'teacher_update_student',
                student_id=student['id']
            ) }}"
        >

            <button
                class="btn green"
                name="status"
                value="approved"
            >
                {{ t('approve') }}
            </button>


            <button
                class="btn red"
                name="status"
                value="rejected"
            >
                {{ t('reject') }}
            </button>


            <button
                class="btn orange"
                name="status"
                value="returned"
            >
                {{ t('return') }}
            </button>

        </form>

    </div>


    <!-- MESSAGE -->

    <div class="card">

        <h2>
            {{ t('message') }}
        </h2>


        {% if student['teacher_message'] %}

            <div class="alert">
                {{ student['teacher_message'] }}
            </div>

        {% endif %}


        <form
            method="POST"
            action="{{ url_for(
                'teacher_message',
                student_id=student['id']
            ) }}"
        >

            <textarea
                name="message"
                placeholder="Write a message to the student..."
                required
            ></textarea>


            <button
                class="btn"
                type="submit"
            >
                {{ t('send_message') }}
            </button>

        </form>

    </div>


    <a
        class="btn dark"
        href="{{ url_for('teacher_dashboard') }}"
    >
        ← {{ t('teacher_dashboard') }}
    </a>

    """


    return page(

        t("student_details"),

        render_template_string(
            body,
            student=student
        )

    )


# =========================================================
# TEACHER UPDATE STATUS
# =========================================================

@app.route(
    "/teacher/student/<int:student_id>/update",
    methods=["POST"]
)
@teacher_required
def teacher_update_student(student_id):

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    if new_status not in [
        "approved",
        "rejected",
        "returned"
    ]:

        abort(400)


    conn = get_db()


    conn.execute(
        """

        UPDATE students

        SET
            status=?,
            updated_at=?

        WHERE id=?

        """,

        (
            new_status,
            datetime.now().isoformat(),
            student_id
        )
    )


    conn.commit()

    conn.close()


    return redirect(
        url_for(
            "teacher_student",
            student_id=student_id
        )
    )


# =========================================================
# TEACHER MESSAGE
# =========================================================

@app.route(
    "/teacher/student/<int:student_id>/message",
    methods=["POST"]
)
@teacher_required
def teacher_message(student_id):

    message = request.form.get(
        "message",
        ""
    ).strip()


    if not message:

        flash(
            "Message cannot be empty."
        )

        return redirect(
            url_for(
                "teacher_student",
                student_id=student_id
            )
        )


    conn = get_db()


    conn.execute(
        """

        UPDATE students

        SET
            teacher_message=?,
            updated_at=?

        WHERE id=?

        """,

        (
            message,
            datetime.now().isoformat(),
            student_id
        )
    )


    conn.commit()

    conn.close()


    return redirect(
        url_for(
            "teacher_student",
            student_id=student_id
        )
    )


# =========================================================
# TEACHER PDF
# =========================================================

@app.route("/teacher/pdf")
@teacher_required
def teacher_pdf():

    grade = request.args.get(
        "grade",
        ""
    ).strip()

    class_name = request.args.get(
        "class_name",
        ""
    ).strip()


    if grade not in [
        "9",
        "10",
        "11",
        "12"
    ]:

        abort(400)


    if class_name not in [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F"
    ]:

        abort(400)


    conn = get_db()


    students = conn.execute(
        """

        SELECT *

        FROM students

        WHERE grade=?

        AND class_name=?

        ORDER BY
            full_name COLLATE NOCASE ASC

        """,

        (
            grade,
            class_name
        )

    ).fetchall()


    conn.close()


    try:

        from reportlab.lib import colors

        from reportlab.lib.pagesizes import (
            A4,
            landscape
        )

        from reportlab.lib.styles import (
            getSampleStyleSheet
        )

        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer
        )

        from reportlab.lib.enums import (
            TA_CENTER
        )

    except ImportError:

        flash(
            "ReportLab is not installed."
        )

        return redirect(
            url_for("teacher_dashboard")
        )


    pdf_name = (
        "Ambuyyee_Grade_"
        + grade
        + "_Class_"
        + class_name
        + ".pdf"
    )


    pdf_path = os.path.join(
        UPLOAD_DIR,
        pdf_name
    )


    doc = SimpleDocTemplate(

        pdf_path,

        pagesize=landscape(A4),

        rightMargin=25,

        leftMargin=25,

        topMargin=25,

        bottomMargin=25

    )


    styles = getSampleStyleSheet()


    title_style = styles["Title"]

    title_style.alignment = TA_CENTER


    elements = []


    elements.append(

        Paragraph(
            "Mana Barumsaa Sadarkaa 2ffaa Ambuyyee",
            title_style
        )

    )


    elements.append(

        Paragraph(

            "Student List - Grade "
            + grade
            + " - Class "
            + class_name,

            styles["Heading2"]

        )

    )


    elements.append(
        Spacer(1, 15)
    )


    data = [[

        "#",

        "Full Name",

        "National ID",

        "Gender",

        "Phone",

        "Grade",

        "Class",

        "Status"

    ]]


    for index, student in enumerate(
        students,
        start=1
    ):

        data.append([

            str(index),

            student["full_name"],

            student["national_id"],

            student["gender"],

            student["phone"],

            student["grade"],

            student["class_name"],

            student["status"]

        ])


    table = Table(
        data,
        repeatRows=1
    )


    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#16283f")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f1f4f7")
                ]
            )

        ])

    )


    elements.append(
        table
    )


    doc.build(
        elements
    )


    return send_from_directory(

        UPLOAD_DIR,

        pdf_name,

        as_attachment=True

    )


# =========================================================
# TEACHER LOGOUT
# =========================================================

@app.route("/teacher/logout")
def teacher_logout():

    session.pop(
        "teacher_logged",
        None
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# DIRECTOR LOGIN
# =========================================================

@app.route(
    "/director/login",
    methods=["GET", "POST"]
)
def director_login():

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()


        if code != DIRECTOR_CODE:

            flash(
                t("wrong_code")
            )

            return redirect(
                url_for("director_login")
            )


        session.clear()

        session["director_logged"] = True


        return redirect(
            url_for("director_dashboard")
        )


    body = """

    <div
        class="card"
        style="max-width:550px;margin:40px auto;"
    >

        <h1>
            {{ t('director_login') }}
        </h1>

        <p class="muted">
            Authorized director access only.
        </p>


        <form method="POST">

            <label>
                Director Code
            </label>

            <input
                type="password"
                name="code"
                required
            >


            <button
                class="btn"
                type="submit"
            >
                {{ t('login') }}
            </button>

        </form>

    </div>

    """


    return page(
        t("director_login"),
        body
    )


# =========================================================
# DIRECTOR DASHBOARD
# =========================================================

@app.route("/director/dashboard")
@director_required
def director_dashboard():

    conn = get_db()


    total = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]


    pending = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='pending'
        """
    ).fetchone()[0]


    approved = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='approved'
        """
    ).fetchone()[0]


    rejected = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='rejected'
        """
    ).fetchone()[0]


    returned = conn.execute(
        """
        SELECT COUNT(*)
        FROM students
        WHERE status='returned'
        """
    ).fetchone()[0]


    # =====================================================
    # GRADE STATISTICS
    # =====================================================

    grade_stats = []


    for g in [
        "9",
        "10",
        "11",
        "12"
    ]:


        total_g = conn.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE grade=?
            """,
            (g,)
        ).fetchone()[0]


        boys_g = conn.execute(
            """
            SELECT COUNT(*)
            FROM students

            WHERE grade=?

            AND gender IN (
                'Male',
                'male',
                'Dhiira',
                'ወንድ'
            )
            """,
            (g,)
        ).fetchone()[0]


        girls_g = conn.execute(
            """
            SELECT COUNT(*)
            FROM students

            WHERE grade=?

            AND gender IN (
                'Female',
                'female',
                'Dubartii',
                'ሴት'
            )
            """,
            (g,)
        ).fetchone()[0]


        grade_stats.append({

            "grade": g,

            "total": total_g,

            "boys": boys_g,

            "girls": girls_g

        })


    # =====================================================
    # CLASS STATISTICS
    # =====================================================

    class_stats = []


    for g in [
        "9",
        "10",
        "11",
        "12"
    ]:

        for c in [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F"
        ]:


            total_c = conn.execute(
                """
                SELECT COUNT(*)
                FROM students
                WHERE grade=?
                AND class_name=?
                """,
                (g, c)
            ).fetchone()[0]


            boys = conn.execute(
                """
                SELECT COUNT(*)
                FROM students

                WHERE grade=?

                AND class_name=?

                AND gender IN (
                    'Male',
                    'male',
                    'Dhiira',
                    'ወንድ'
                )
                """,
                (g, c)
            ).fetchone()[0]


            girls = conn.execute(
                """
                SELECT COUNT(*)
                FROM students

                WHERE grade=?

                AND class_name=?

                AND gender IN (
                    'Female',
                    'female',
                    'Dubartii',
                    'ሴት'
                )
                """,
                (g, c)
            ).fetchone()[0]


            class_stats.append({

                "grade": g,

                "class": c,

                "total": total_c,

                "boys": boys,

                "girls": girls

            })


    conn.close()


    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <p class="muted">
                    AMBUYEE • MANAGEMENT
                </p>

                <h1>
                    {{ t('director_dashboard') }}
                </h1>

            </div>


            <a
                class="btn dark"
                href="{{ url_for('director_logout') }}"
            >
                {{ t('logout') }}
            </a>

        </div>


        <div class="grid">

            <div class="stat">

                <h3>
                    {{ t('total_students') }}
                </h3>

                <strong>
                    {{ total }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_pending') }}
                </h3>

                <strong>
                    {{ pending }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_approved') }}
                </h3>

                <strong>
                    {{ approved }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_rejected') }}
                </h3>

                <strong>
                    {{ rejected }}
                </strong>

            </div>


            <div class="stat">

                <h3>
                    {{ t('total_returned') }}
                </h3>

                <strong>
                    {{ returned }}
                </strong>

            </div>

        </div>

    </div>


    <!-- GRADE STATISTICS -->

    <div class="card">

        <h2>
            Grade Statistics
        </h2>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>
                            {{ t('grade') }}
                        </th>

                        <th>
                            {{ t('count') }}
                        </th>

                        <th>
                            {{ t('boys') }}
                        </th>

                        <th>
                            {{ t('girls') }}
                        </th>

                    </tr>

                </thead>


                <tbody>

                {% for row in grade_stats %}

                    <tr>

                        <td>
                            Grade {{ row.grade }}
                        </td>

                        <td>
                            <strong>
                                {{ row.total }}
                            </strong>
                        </td>

                        <td>
                            {{ row.boys }}
                        </td>

                        <td>
                            {{ row.girls }}
                        </td>

                    </tr>

                {% endfor %}

                </tbody>

            </table>

        </div>

    </div>


    <!-- CLASS STATISTICS -->

    <div class="card">

        <h2>
            {{ t('class_statistics') }}
        </h2>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>
                            {{ t('grade') }}
                        </th>

                        <th>
                            {{ t('class') }}
                        </th>

                        <th>
                            {{ t('count') }}
                        </th>

                        <th>
                            {{ t('boys') }}
                        </th>

                        <th>
                            {{ t('girls') }}
                        </th>

                    </tr>

                </thead>


                <tbody>

                {% for row in class_stats %}

                    <tr>

                        <td>
                            Grade {{ row.grade }}
                        </td>

                        <td>
                            Class {{ row.class }}
                        </td>

                        <td>
                            <strong>
                                {{ row.total }}
                            </strong>
                        </td>

                        <td>
                            {{ row.boys }}
                        </td>

                        <td>
                            {{ row.girls }}
                        </td>

                    </tr>

                {% endfor %}

                </tbody>

            </table>

        </div>

    </div>


    <div class="card">

        <h2>
            {{ t('student_details') }}
        </h2>

        <a
            class="btn"
            href="{{ url_for('director_students') }}"
        >
            View All Students
        </a>

    </div>

    """


    return page(

        t("director_dashboard"),

        render_template_string(

            body,

            total=total,

            pending=pending,

            approved=approved,

            rejected=rejected,

            returned=returned,

            grade_stats=grade_stats,

            class_stats=class_stats

        )

    )


# =========================================================
# DIRECTOR STUDENTS
# =========================================================

@app.route("/director/students")
@director_required
def director_students():

    search = request.args.get(
        "search",
        ""
    ).strip()

    grade = request.args.get(
        "grade",
        ""
    ).strip()

    class_name = request.args.get(
        "class_name",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()


    query = """

        SELECT *

        FROM students

        WHERE 1=1

    """


    params = []


    if grade:

        query += """
            AND grade=?
        """

        params.append(
            grade
        )


    if class_name:

        query += """
            AND class_name=?
        """

        params.append(
            class_name
        )


    if status:

        query += """
            AND status=?
        """

        params.append(
            status
        )


    if search:

        query += """

            AND (

                full_name LIKE ?

                OR national_id LIKE ?

                OR phone LIKE ?

                OR registration_code LIKE ?

            )

        """

        term = (
            "%"
            + search
            + "%"
        )

        params.extend([

            term,
            term,
            term,
            term

        ])


    query += """

        ORDER BY
            full_name COLLATE NOCASE ASC

    """


    conn = get_db()


    students = conn.execute(
        query,
        params
    ).fetchall()


    conn.close()


    body = """

    <div class="card">

        <div class="section-title">

            <div>

                <p class="muted">
                    AMBUYEE • MANAGEMENT
                </p>

                <h1>
                    All Students
                </h1>

            </div>

            <a
                class="btn dark"
                href="{{ url_for('director_dashboard') }}"
            >
                ← Dashboard
            </a>

        </div>


        <form method="GET">

            <label>
                {{ t('search') }}
            </label>

            <input
                name="search"
                value="{{ search }}"
                placeholder="Name / National ID / Phone / Registration Code"
            >


            <div class="grid">

                <div>

                    <label>
                        {{ t('grade') }}
                    </label>

                    <select name="grade">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        <option
                            value="9"
                            {% if request.args.get('grade') == '9' %}
                                selected
                            {% endif %}
                        >
                            Grade 9
                        </option>

                        <option
                            value="10"
                            {% if request.args.get('grade') == '10' %}
                                selected
                            {% endif %}
                        >
                            Grade 10
                        </option>

                        <option
                            value="11"
                            {% if request.args.get('grade') == '11' %}
                                selected
                            {% endif %}
                        >
                            Grade 11
                        </option>

                        <option
                            value="12"
                            {% if request.args.get('grade') == '12' %}
                                selected
                            {% endif %}
                        >
                            Grade 12
                        </option>

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('class') }}
                    </label>

                    <select name="class_name">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        {% for c in [
                            'A',
                            'B',
                            'C',
                            'D',
                            'E',
                            'F'
                        ] %}

                            <option
                                value="{{ c }}"
                                {% if request.args.get('class_name') == c %}
                                    selected
                                {% endif %}
                            >
                                Class {{ c }}
                            </option>

                        {% endfor %}

                    </select>

                </div>


                <div>

                    <label>
                        {{ t('status') }}
                    </label>

                    <select name="status">

                        <option value="">
                            {{ t('all') }}
                        </option>

                        <option
                            value="pending"
                            {% if status == 'pending' %}
                                selected
                            {% endif %}
                        >
                            {{ t('pending') }}
                        </option>

                        <option
                            value="approved"
                            {% if status == 'approved' %}
                                selected
                            {% endif %}
                        >
                            {{ t('approved') }}
                        </option>

                        <option
                            value="rejected"
                            {% if status == 'rejected' %}
                                selected
                            {% endif %}
                        >
                            {{ t('rejected') }}
                        </option>

                        <option
                            value="returned"
                            {% if status == 'returned' %}
                                selected
                            {% endif %}
                        >
                            {{ t('returned') }}
                        </option>

                    </select>

                </div>

            </div>


            <button
                class="btn"
                type="submit"
            >
                {{ t('search') }}
            </button>

        </form>

    </div>


    <div class="card">

        <div class="section-title">

            <h2>
                {{ students|length }}
                {{ t('total_students') }}
            </h2>

            <span class="muted">
                Alphabetical order
            </span>

        </div>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>

                        <th>#</th>

                        <th>
                            {{ t('full_name') }}
                        </th>

                        <th>
                            {{ t('phone') }}
                        </th>

                        <th>
                            {{ t('grade') }}
                        </th>

                        <th>
                            {{ t('class') }}
                        </th>

                        <th>
                            {{ t('gender') }}
                        </th>

                        <th>
                            {{ t('status') }}
                        </th>

                    </tr>

                </thead>


                <tbody>

                {% for student in students %}

                    <tr>

                        <td>
                            {{ loop.index }}
                        </td>

                        <td>
                            <strong>
                                {{ student['full_name'] }}
                            </strong>
                        </td>

                        <td>
                            {{ student['phone'] }}
                        </td>

                        <td>
                            {{ student['grade'] }}
                        </td>

                        <td>
                            {{ student['class_name'] }}
                        </td>

                        <td>
                            {{ student['gender'] }}
                        </td>

                        <td>

                            <span
                                class="badge
                                {{ student['status'] }}"
                            >
                                {{ status_text(
                                    student['status']
                                ) }}
                            </span>

                        </td>

                    </tr>

                {% else %}

                    <tr>

                        <td colspan="7">
                            {{ t('no_students') }}
                        </td>

                    </tr>

                {% endfor %}

                </tbody>

            </table>

        </div>

    </div>

    """


    return page(

        "All Students",

        render_template_string(

            body,

            students=students,

            search=search,

            grade=grade,

            class_name=class_name,

            status=status

        )

    )


# =========================================================
# DIRECTOR LOGOUT
# =========================================================

@app.route("/director/logout")
def director_logout():

    session.pop(
        "director_logged",
        None
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# PROTECTED UPLOADS
# =========================================================

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    # -----------------------------------------------------
    # Teacher / Director can access uploaded documents.
    # Student can access only their own uploaded documents.
    # -----------------------------------------------------

    if session.get(
        "teacher_logged"
    ) or session.get(
        "director_logged"
    ):

        return send_from_directory(
            UPLOAD_DIR,
            filename
        )


    student_id = session.get(
        "student_id"
    )


    if not student_id:

        abort(403)


    conn = get_db()


    student = conn.execute(
        """
        SELECT
            card_front,
            card_back,
            face_photo,
            ministry_document,
            payment_screenshot
        FROM students
        WHERE id=?
        """,
        (student_id,)
    ).fetchone()


    conn.close()


    if not student:

        abort(403)


    allowed_student_files = {

        student["card_front"],

        student["card_back"],

        student["face_photo"],

        student["ministry_document"],

        student["payment_screenshot"]

    }


    if filename not in allowed_student_files:

        abort(403)


    return send_from_directory(
        UPLOAD_DIR,
        filename
    )


# =========================================================
# ERROR 413
# =========================================================

@app.errorhandler(413)
def too_large(error):

    return page(

        "File Too Large",

        """

        <div class="card">

            <h1>
                File Too Large
            </h1>

            <p class="muted">
                Maximum upload size is 10 MB.
            </p>

            <a
                class="btn"
                href="{{ url_for('register') }}"
            >
                {{ t('register') }}
            </a>

        </div>

        """

    ), 413


# =========================================================
# ERROR 404
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return page(

        "Not Found",

        """

        <div
            class="card"
            style="text-align:center;"
        >

            <h1>
                404
            </h1>

            <p class="muted">
                Page not found.
            </p>

            <a
                class="btn"
                href="{{ url_for('home') }}"
            >
                {{ t('home') }}
            </a>

        </div>

        """

    ), 404


# =========================================================
# ERROR 403
# =========================================================

@app.errorhandler(403)
def forbidden(error):

    return page(

        "Access Denied",

        """

        <div
            class="card"
            style="text-align:center;"
        >

            <h1>
                Access Denied
            </h1>

            <p class="muted">
                You do not have permission to access this file.
            </p>

            <a
                class="btn"
                href="{{ url_for('home') }}"
            >
                {{ t('home') }}
            </a>

        </div>

        """

    ), 403


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("")
    print("==============================================")
    print(" AMBUYEE STUDENT REGISTRATION SYSTEM")
    print("==============================================")
    print("")
    print("Student Registration:")
    print("http://127.0.0.1:8080/register")
    print("")
    print("Student Login:")
    print("http://127.0.0.1:8080/student/login")
    print("")
    print("Teacher Login:")
    print("http://127.0.0.1:8080/teacher/login")
    print("")
    print("Director Login:")
    print("http://127.0.0.1:8080/director/login")
    print("")
    print("Teacher Demo Code:")
    print(TEACHER_CODE)
    print("")
    print("Director Demo Code:")
    print(DIRECTOR_CODE)
    print("")
    print("Database:")
    print(DB_PATH)
    print("")
    print("Uploads:")
    print(UPLOAD_DIR)
    print("==============================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    )
