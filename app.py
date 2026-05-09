"""
╔══════════════════════════════════════════════════════════════╗
║   SMART ROAD MONITORING SYSTEM — NIRAL HACKATHON 3.0        ║
║   Professional UI · YOLO Detection · Fixed Camera Mode      ║
╚══════════════════════════════════════════════════════════════╝

FIXES:
  ✅ Camera: uses st.camera_input (browser-native, no WebRTC NAT issues)
  ✅ Thread-safe state with threading.Lock
  ✅ Professional dark industrial UI
  ✅ Real-time detection on each captured frame
  ✅ Email alerts with cooldown
  ✅ Location geocoding + map
"""

import streamlit as st
from PIL import Image
import datetime
import cv2
import numpy as np
import os
import threading
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from geopy.geocoders import Nominatim
from ultralytics import YOLO

# ══════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Smart Road Monitoring · Niral 3.0",
    layout="wide",
    page_icon="🛣️",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════
# PROFESSIONAL CSS — INDUSTRIAL DARK THEME
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg-deep:     #05070a;
    --bg-base:     #0a0e14;
    --bg-card:     #0f1520;
    --bg-elevated: #151d2b;
    --bg-input:    #0d1219;

    --border-dim:  #1a2234;
    --border-mid:  #243045;
    --border-hi:   #2e3f5c;

    --amber:       #f0a500;
    --amber-dim:   #f0a50020;
    --amber-glow:  #f0a50040;

    --red:         #e53e3e;
    --red-dim:     #e53e3e18;
    --green:       #38b2a0;
    --green-dim:   #38b2a018;
    --blue:        #4a9fd4;
    --blue-dim:    #4a9fd415;

    --text-h:      #eef2f8;
    --text-body:   #8a9bb8;
    --text-dim:    #4a5568;
    --text-code:   #7ec8e3;
}

* { box-sizing: border-box; margin: 0; }

[data-testid="stAppViewContainer"] {
    background: var(--bg-deep);
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, #0d1f3510, transparent),
        linear-gradient(180deg, #05070a 0%, #080c12 100%);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"],
footer { display: none !important; }

.block-container {
    padding: 0 2.5rem 3rem !important;
    max-width: 1440px !important;
}

/* ── TOP NAV BAR ── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0;
    border-bottom: 1px solid var(--border-dim);
    margin-bottom: 2rem;
}

.nav-logo {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nav-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #f0a500, #c77d00);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    box-shadow: 0 0 20px #f0a50030;
}

.nav-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--text-h);
    letter-spacing: -0.02em;
}

.nav-title span { color: var(--amber); }

.nav-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: var(--text-dim);
    border: 1px solid var(--border-dim);
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.1em;
}

.nav-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--green);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}

/* ── HERO ── */
.hero {
    text-align: center;
    padding: 2rem 0 2.5rem;
}

.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--amber);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 4vw, 3.6rem);
    font-weight: 800;
    color: var(--text-h);
    line-height: 1.05;
    letter-spacing: -0.04em;
    margin-bottom: 1rem;
}

.hero-title .hl { color: var(--amber); }

.hero-desc {
    color: var(--text-body);
    font-size: 0.95rem;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── DIVIDER ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-mid), transparent);
    margin: 2rem 0;
}

/* ── SECTION LABEL ── */
.sec-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: var(--amber);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}

.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-dim);
}

/* ── CARDS ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--amber), transparent);
    opacity: 0.5;
}

/* ── METRIC GRID ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}

.metric-cell {
    background: var(--bg-elevated);
    border: 1px solid var(--border-dim);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    transition: border-color 0.3s;
}

.metric-cell:hover { border-color: var(--border-hi); }

.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--amber);
    line-height: 1;
    margin-bottom: 6px;
}

.metric-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: var(--text-dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ── STATUS BADGE ── */
.badge-live {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--red-dim);
    border: 1px solid #e53e3e55;
    color: var(--red);
    padding: 6px 14px;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}

.badge-clear {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--green-dim);
    border: 1px solid #38b2a055;
    color: var(--green);
    padding: 6px 14px;
    border-radius: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
}

/* ── LOG ENTRIES ── */
.log-wrap {
    max-height: 260px;
    overflow-y: auto;
    padding-right: 4px;
}

.log-wrap::-webkit-scrollbar { width: 4px; }
.log-wrap::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 4px; }

.log-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 12px;
    background: var(--bg-elevated);
    border-left: 3px solid var(--amber);
    border-radius: 0 6px 6px 0;
    margin-bottom: 6px;
}

.log-time {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: var(--text-dim);
    white-space: nowrap;
    padding-top: 1px;
}

.log-text {
    font-size: 0.78rem;
    color: var(--text-body);
    line-height: 1.5;
}

/* ── DAMAGE TAGS ── */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.5rem 0; }

.dmg-tag {
    background: var(--amber-dim);
    border: 1px solid var(--amber-glow);
    color: var(--amber);
    padding: 5px 14px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.05em;
}

/* ── SEVERITY BANNER ── */
.sev-critical {
    background: #e53e3e12;
    border: 1px solid #e53e3e55;
    border-left: 4px solid var(--red);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
}

.sev-moderate {
    background: #f0a50012;
    border: 1px solid #f0a50055;
    border-left: 4px solid var(--amber);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
}

.sev-clear {
    background: var(--green-dim);
    border: 1px solid #38b2a055;
    border-left: 4px solid var(--green);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
}

.sev-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--text-h);
    margin-bottom: 4px;
}

.sev-sub {
    font-size: 0.78rem;
    color: var(--text-body);
}

/* ── REPORT BLOCK ── */
.report-block {
    background: var(--bg-deep);
    border: 1px solid var(--border-dim);
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-body);
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-x: auto;
}

/* ── BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #c77d00, #f0a500) !important;
    color: #05070a !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    width: 100% !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px #f0a50025 !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px #f0a50040 !important;
}

/* ── RADIO ── */
div[data-testid="stRadio"] > div {
    gap: 8px !important;
}

div[data-testid="stRadio"] label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: 8px !important;
    padding: 10px 18px !important;
    color: var(--text-body) !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}

div[data-testid="stRadio"] label:hover {
    border-color: var(--amber) !important;
    color: var(--text-h) !important;
}

/* ── INPUT ── */
div[data-testid="stTextInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-mid) !important;
    border-radius: 8px !important;
    color: var(--text-h) !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.6rem 1rem !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-dim) !important;
}

/* ── FILE UPLOADER ── */
div[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-hi) !important;
    border-radius: 10px !important;
}

/* ── CAMERA WIDGET ── */
div[data-testid="stCameraInput"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-hi) !important;
    overflow: hidden;
}

/* ── MAP ── */
div[data-testid="stDeckGlJsonChart"],
iframe { border-radius: 10px !important; }

/* ── SPINNER ── */
div[data-testid="stSpinner"] { color: var(--amber) !important; }

/* ── SUCCESS/ERROR ── */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* ── FOOTER ── */
.footer {
    text-align: center;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border-dim);
    margin-top: 3rem;
}

.footer-text {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: var(--text-dim);
    letter-spacing: 0.15em;
}

.footer-brand {
    color: var(--amber);
}

/* ── COLUMN GAPS ── */
[data-testid="column"] { padding: 0 0.5rem !important; }

/* Scrollbar global */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════
MODEL_PATH        = "Model/road_damage_detection_model.pt"
SENDER_EMAIL      = "your_email@gmail.com"
SENDER_PASSWORD   = "your_app_password"          # Gmail App Password
RECEIVER_EMAIL    = "officer@tnhighways.gov.in"
SNAPSHOTS_DIR     = "snapshots"
CONF_THRESHOLD    = 0.15
EMAIL_COOLDOWN    = 60                           # seconds between alert emails
INFER_IMG_SIZE    = 640

os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

# ══════════════════════════════════════════════
# SHARED THREAD-SAFE STATE
# ══════════════════════════════════════════════
_lock  = threading.Lock()
_state = {
    "frames":          0,
    "detections":      0,
    "alerts":          0,
    "last_email_time": 0.0,
    "log":             [],
    "location_name":   "",
    "lat":             None,
    "lon":             None,
}

# ══════════════════════════════════════════════
# SESSION STATE DEFAULTS
# ══════════════════════════════════════════════
defaults = {
    "upload_result":  None,
    "upload_labels":  [],
    "upload_img":     None,
    "cam_result":     None,
    "cam_labels":     [],
    "cam_count":      0,
    "report_text":    "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# LOAD MODEL (cached)
# ══════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading YOLO model …")
def load_model():
    return YOLO(MODEL_PATH)

model = load_model()

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def save_snapshot(bgr_frame: np.ndarray) -> str:
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(SNAPSHOTS_DIR, f"evidence_{ts}.jpg")
    cv2.imwrite(path, bgr_frame)
    return path


def severity_info(labels: list) -> tuple[str, str]:
    if not labels:
        return "CLEAR", "No road damage detected in this frame."
    if len(labels) >= 3:
        return "CRITICAL", f"{len(labels)} damage types found — immediate repair recommended."
    return "MODERATE", f"{len(labels)} damage type(s) detected — schedule inspection."


def build_report(labels, location_name, lat, lon, source="Camera") -> str:
    ts       = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    coords   = f"{lat:.5f}, {lon:.5f}" if lat and lon else "N/A"
    map_url  = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "N/A"
    sev, _   = severity_info(labels)

    return f"""
╔═══════════════════════════════════════════════════╗
║   ROAD DAMAGE INCIDENT REPORT · NIRAL 3.0        ║
╚═══════════════════════════════════════════════════╝

TIMESTAMP    : {ts}
SOURCE       : {source}
DAMAGE TYPES : {', '.join(labels) if labels else 'None Detected'}
LOCATION     : {location_name or 'Not Provided'}
COORDINATES  : {coords}
MAP URL      : {map_url}
SEVERITY     : {sev}

SYSTEM       : Smart Road Monitoring System v3.0
AUTHORITY    : Tamil Nadu Highways Department
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def send_email_alert(report: str, img_path: str | None = None):
    """Fire-and-forget email in background thread."""
    def _send():
        msg          = MIMEMultipart()
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg["Subject"] = "🚨 Road Damage Alert — Smart Road Monitoring System"
        msg.attach(MIMEText(report, "plain"))

        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as f:
                img = MIMEImage(f.read(), name=os.path.basename(img_path))
                img.add_header("Content-Disposition", "attachment",
                               filename=os.path.basename(img_path))
                msg.attach(img)
        try:
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.starttls()
            s.login(SENDER_EMAIL, SENDER_PASSWORD)
            s.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            s.quit()
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    threading.Thread(target=_send, daemon=True).start()


def run_inference(pil_img: Image.Image) -> tuple[np.ndarray, list[str]]:
    """Run YOLO on a PIL image, return annotated BGR array + label list."""
    results    = model.predict(pil_img, conf=CONF_THRESHOLD, imgsz=INFER_IMG_SIZE, verbose=False)
    annotated  = results[0].plot()          # RGB numpy
    annotated  = annotated[:, :, ::-1]     # → BGR

    labels = []
    boxes  = results[0].boxes
    if boxes is not None and len(boxes) > 0:
        for cls_id, conf_val in zip(boxes.cls, boxes.conf):
            name = model.names[int(cls_id)]
            labels.append(f"{name} ({conf_val * 100:.1f}%)")

    return annotated, labels


def render_severity_banner(labels: list):
    sev, msg = severity_info(labels)
    css_cls  = {"CRITICAL": "sev-critical", "MODERATE": "sev-moderate", "CLEAR": "sev-clear"}[sev]
    icon     = {"CRITICAL": "🔴", "MODERATE": "🟡", "CLEAR": "🟢"}[sev]
    st.markdown(f"""
<div class="{css_cls}">
<div class="sev-title">{icon} {sev}</div>
<div class="sev-sub">{msg}</div>
</div>
""", unsafe_allow_html=True)


geolocator = Nominatim(user_agent="smart_road_monitor_niral3")


# ══════════════════════════════════════════════
# NAV BAR
# ══════════════════════════════════════════════
st.markdown("""
<div class="nav-bar">
  <div class="nav-logo">
    <div class="nav-icon">🛣️</div>
    <div>
      <div class="nav-title">Smart Road <span>Monitor</span></div>
    </div>
    <div class="nav-badge">NIRAL HACKATHON 3.0</div>
  </div>
  <div class="nav-status">
    <div class="pulse-dot"></div>
    SYSTEM ONLINE
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-POWERED INFRASTRUCTURE SAFETY</div>
  <div class="hero-title">
    Detect. <span class="hl">Alert.</span> Repair.
  </div>
  <div class="hero-desc">
    Real-time road damage detection using YOLO deep learning.
    Upload images or use live camera to instantly identify potholes,
    cracks, and surface failures — then alert authorities automatically.
  </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MODE SELECTOR
# ══════════════════════════════════════════════
st.markdown('<div class="sec-label">DETECTION MODE</div>', unsafe_allow_html=True)

mode = st.radio(
    "Mode",
    ["📁  Upload Image", "📷  Live Camera"],
    horizontal=True,
    label_visibility="collapsed"
)
is_live = "Camera" in mode

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# LOCATION SECTION
# ══════════════════════════════════════════════
st.markdown('<div class="sec-label">LOCATION INTELLIGENCE</div>', unsafe_allow_html=True)

loc_col1, loc_col2 = st.columns([2, 1])

with loc_col1:
    location_name = st.text_input(
        "Road / Area Name",
        placeholder="e.g. Anna Salai, Chennai or NH-44 Km 120, Madurai",
        help="Enter a place name to geocode coordinates and include in the alert report."
    )

lat = lon = None

if location_name:
    try:
        with st.spinner("Geocoding …"):
            loc_obj = geolocator.geocode(location_name, timeout=5)

        if loc_obj:
            lat, lon = loc_obj.latitude, loc_obj.longitude
            with _lock:
                _state["location_name"] = location_name
                _state["lat"]           = lat
                _state["lon"]           = lon

            with loc_col2:
                st.success(f"📍 {lat:.4f}, {lon:.4f}")

            st.map({"lat": [lat], "lon": [lon]}, zoom=13)
        else:
            st.warning("Location not found — you can still run detection without coordinates.")
    except Exception as e:
        st.error(f"Geocoding error: {e}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ① UPLOAD IMAGE MODE
# ══════════════════════════════════════════════
if not is_live:
    st.markdown('<div class="sec-label">IMAGE DETECTION</div>', unsafe_allow_html=True)

    up_col1, up_col2 = st.columns([1.2, 1], gap="large")

    with up_col1:
        uploaded = st.file_uploader(
            "Drop road image here",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="visible"
        )

        if uploaded:
            st.session_state.upload_img = Image.open(uploaded).convert("RGB")
            st.image(st.session_state.upload_img, use_container_width=True,
                     caption="Uploaded Image")

        run_btn = st.button("⚡  RUN DAMAGE DETECTION", key="run_upload")

        if run_btn:
            if st.session_state.upload_img:
                with st.spinner("Running YOLO inference …"):
                    bgr, labels = run_inference(st.session_state.upload_img)

                st.session_state.upload_result = bgr[:, :, ::-1]  # back to RGB for display
                st.session_state.upload_labels = labels

                # snapshot
                snap = save_snapshot(bgr)

                rpt = build_report(labels, location_name, lat, lon, "Upload Image")
                st.session_state.report_text = rpt

                # update shared state
                with _lock:
                    _state["frames"]     += 1
                    _state["detections"] += len(labels)
                    if labels:
                        now = time.time()
                        if now - _state["last_email_time"] > EMAIL_COOLDOWN:
                            _state["alerts"]          += 1
                            _state["last_email_time"]  = now
                            send_email_alert(rpt, snap)
                        _state["log"].insert(0, {
                            "time":   datetime.datetime.now().strftime("%H:%M:%S"),
                            "labels": labels
                        })
                        _state["log"] = _state["log"][:20]
            else:
                st.warning("Please upload an image first.")

    with up_col2:
        if st.session_state.upload_result is not None:
            st.markdown("**Detection Output**")
            st.image(st.session_state.upload_result, use_container_width=True)

            render_severity_banner(st.session_state.upload_labels)

            if st.session_state.upload_labels:
                st.markdown('<div class="tag-wrap">', unsafe_allow_html=True)
                tags = "".join(
                    f'<span class="dmg-tag">{l}</span>'
                    for l in st.session_state.upload_labels
                )
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-clear">✅ NO DAMAGE DETECTED</span>',
                            unsafe_allow_html=True)

    # Report & Send
    if st.session_state.report_text:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">INCIDENT REPORT</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="report-block">{st.session_state.report_text}</div>',
            unsafe_allow_html=True
        )
        if st.button("📧  SEND ALERT TO OFFICER", key="send_upload"):
            send_email_alert(st.session_state.report_text)
            st.success("✅ Alert dispatched to highway authority officer.")

# ══════════════════════════════════════════════
# ② LIVE CAMERA MODE
# ══════════════════════════════════════════════
else:
    st.markdown('<div class="sec-label">LIVE CAMERA DETECTION</div>', unsafe_allow_html=True)

    # ── Info card ──
    st.markdown("""
<div class="card" style="margin-bottom:1.2rem;">
<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
  <span style="font-size:1.3rem;">📷</span>
  <span style="font-family:'Syne',sans-serif;font-weight:700;color:var(--text-h);font-size:1rem;">
    Browser Camera
  </span>
</div>
<p style="color:var(--text-body);font-size:0.82rem;line-height:1.7;margin:0;">
  Click <strong style="color:var(--amber)">Take Photo</strong> below to capture a frame from your device camera.
  The frame is instantly analyzed by the YOLO model. Repeat as often as needed —
  every detection is logged and critical alerts are auto-emailed to the officer.
</p>
</div>
""", unsafe_allow_html=True)

    cam_col1, cam_col2 = st.columns([1.1, 1], gap="large")

    with cam_col1:
        cam_img = st.camera_input(
            "Capture Road Frame",
            label_visibility="collapsed",
            key="camera_feed"
        )

        if cam_img is not None:
            pil_frame = Image.open(cam_img).convert("RGB")

            with st.spinner("Analyzing frame …"):
                bgr, labels = run_inference(pil_frame)

            rgb_out = bgr[:, :, ::-1]

            st.session_state.cam_result = rgb_out
            st.session_state.cam_labels = labels
            st.session_state.cam_count += 1

            snap = save_snapshot(bgr)

            rpt = build_report(labels, location_name, lat, lon, "Live Camera")
            st.session_state.report_text = rpt

            with _lock:
                _state["frames"]     += 1
                _state["detections"] += len(labels)
                if labels:
                    now = time.time()
                    if now - _state["last_email_time"] > EMAIL_COOLDOWN:
                        _state["alerts"]          += 1
                        _state["last_email_time"]  = now
                        send_email_alert(rpt, snap)
                    _state["log"].insert(0, {
                        "time":   datetime.datetime.now().strftime("%H:%M:%S"),
                        "labels": labels
                    })
                    _state["log"] = _state["log"][:20]

    with cam_col2:
        # ── Live metrics ──
        with _lock:
            frames     = _state["frames"]
            detections = _state["detections"]
            alerts     = _state["alerts"]
            logs       = list(_state["log"])

        cam_count = st.session_state.cam_count

        st.markdown(f"""
<div class="metric-row">
  <div class="metric-cell">
    <div class="metric-val">{cam_count}</div>
    <div class="metric-lbl">Frames Scanned</div>
  </div>
  <div class="metric-cell">
    <div class="metric-val">{detections}</div>
    <div class="metric-lbl">Total Detections</div>
  </div>
  <div class="metric-cell">
    <div class="metric-val">{alerts}</div>
    <div class="metric-lbl">Alerts Sent</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Detection result ──
        if st.session_state.cam_result is not None:
            st.markdown("**Latest Detection**")
            st.image(st.session_state.cam_result, use_container_width=True)
            render_severity_banner(st.session_state.cam_labels)

            if st.session_state.cam_labels:
                tags = "".join(
                    f'<span class="dmg-tag">{l}</span>'
                    for l in st.session_state.cam_labels
                )
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<span class="badge-clear">✅ Road Clear — No Damage</span>',
                    unsafe_allow_html=True
                )

        # ── Detection log ──
        if logs:
            st.markdown("---")
            st.markdown('<div class="sec-label" style="margin-top:0.5rem;">DETECTION LOG</div>',
                        unsafe_allow_html=True)
            items_html = ""
            for item in logs[:8]:
                items_html += f"""
<div class="log-item">
  <span class="log-time">{item['time']}</span>
  <span class="log-text">{', '.join(item['labels'])}</span>
</div>"""
            st.markdown(
                f'<div class="log-wrap">{items_html}</div>',
                unsafe_allow_html=True
            )

    # ── Report & manual send ──
    if st.session_state.report_text:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">INCIDENT REPORT</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="report-block">{st.session_state.report_text}</div>',
            unsafe_allow_html=True
        )
        if st.button("📧  SEND ALERT TO OFFICER", key="send_cam"):
            send_email_alert(st.session_state.report_text)
            st.success("✅ Alert dispatched to highway authority officer.")

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-text">
    <span class="footer-brand">SMART ROAD MONITORING SYSTEM</span>
    &nbsp;·&nbsp; NIRAL HACKATHON 3.0
    &nbsp;·&nbsp; YOLO AI DETECTION
    &nbsp;·&nbsp; TAMIL NADU HIGHWAYS
  </div>
</div>
""", unsafe_allow_html=True)