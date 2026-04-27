import streamlit as st
from PIL import Image
import datetime
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from geopy.geocoders import Nominatim

# ─── PAGE CONFIG ─────────────────────────────
st.set_page_config(page_title="Road Damage Detection", layout="wide", page_icon="🚧")

# ─── UI STYLE ───────────────────────────────
# UI CHANGE: Complete design overhaul — industrial-command aesthetic
# with amber/orange accent system, custom typography, animated elements.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg-base:      #080c10;
    --bg-surface:   #0d1117;
    --bg-elevated:  #161b22;
    --bg-hover:     #1c2330;
    --border:       #21262d;
    --border-glow:  #f59e0b44;
    --accent:       #f59e0b;
    --accent-dim:   #b45309;
    --accent-glow:  #f59e0b22;
    --danger:       #ef4444;
    --success:      #22c55e;
    --success-glow: #22c55e22;
    --text-primary: #e6edf3;
    --text-secondary: #7d8590;
    --text-muted:   #484f58;
}

/* ── Global Reset ── */
* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: var(--bg-base);
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── Main container ── */
.block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Hero Header ── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 2rem;
    position: relative;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    transform: translateX(-50%);
    width: 120px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.hero-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    background: var(--accent-glow);
    border: 1px solid var(--border-glow);
    padding: 4px 14px;
    border-radius: 2px;
    margin-bottom: 1rem;
    text-transform: uppercase;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.04em;
    margin: 0.3rem 0;
    line-height: 1.1;
}
.hero-title span {
    color: var(--accent);
}
.hero-sub {
    font-size: 0.9rem;
    color: var(--text-secondary);
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
}

/* ── Section Cards ── */
.section-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.section-card:hover {
    border-color: var(--accent-dim);
}
.section-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--accent), transparent);
    border-radius: 8px 0 0 8px;
}
.card-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-elevated) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzoneInput"] {
    cursor: pointer !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
[data-testid="stTextInput"] label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Primary Button ── */
div.stButton > button {
    background: linear-gradient(135deg, #d97706, #f59e0b) !important;
    color: #0d1117 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.7rem 2rem !important;
    height: auto !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 20px var(--accent-glow) !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #f59e0b, #fbbf24) !important;
    box-shadow: 0 0 35px #f59e0b55 !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Status Alerts ── */
[data-testid="stSuccess"] {
    background: var(--success-glow) !important;
    border: 1px solid #22c55e44 !important;
    border-radius: 6px !important;
    color: var(--success) !important;
}
[data-testid="stWarning"] {
    background: #f59e0b11 !important;
    border: 1px solid #f59e0b44 !important;
    border-radius: 6px !important;
    color: var(--accent) !important;
}
[data-testid="stError"] {
    background: #ef444411 !important;
    border: 1px solid #ef444444 !important;
    border-radius: 6px !important;
}
[data-testid="stInfo"] {
    background: #3b82f611 !important;
    border: 1px solid #3b82f644 !important;
    border-radius: 6px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--accent) !important;
}

/* ── Image containers ── */
[data-testid="stImage"] img {
    border-radius: 6px;
    border: 1px solid var(--border);
}

/* ── Metric Cards ── */
.metric-row {
    display: flex;
    gap: 12px;
    margin: 1rem 0;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 140px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem;
    text-align: center;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Damage Tags ── */
.damage-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0.8rem 0;
}
.damage-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    background: var(--bg-elevated);
    border: 1px solid var(--accent-dim);
    color: var(--accent);
    padding: 4px 12px;
    border-radius: 3px;
    letter-spacing: 0.05em;
}
.damage-tag.critical {
    border-color: var(--danger);
    color: var(--danger);
    background: #ef444411;
}

/* ── Report Block ── */
.report-block {
    background: var(--bg-base);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.9;
    white-space: pre-wrap;
    overflow-x: auto;
}
.report-block .highlight {
    color: var(--accent);
    font-weight: 500;
}
.report-block .value {
    color: var(--text-primary);
}

/* ── Map container ── */
[data-testid="stDeckGlJsonChart"],
iframe {
    border-radius: 6px !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
}

/* ── Dividers ── */
hr {
    border: none;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0;
}

/* ── Text area override ── */
textarea {
    background: var(--bg-base) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-dim); }

/* ── Responsive columns gap ── */
[data-testid="stHorizontalBlock"] {
    gap: 1.2rem !important;
}

/* ── No damage banner ── */
.no-damage {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--success-glow);
    border: 1px solid #22c55e44;
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    color: var(--success);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    margin: 0.8rem 0;
}

/* ── Step indicators ── */
.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px; height: 22px;
    background: var(--accent-glow);
    border: 1px solid var(--border-glow);
    border-radius: 50%;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--accent);
    margin-right: 8px;
    flex-shrink: 0;
}

/* ── Map link button ── */
a.map-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    text-decoration: none;
    border: 1px solid var(--border-glow);
    background: var(--accent-glow);
    padding: 6px 14px;
    border-radius: 4px;
    margin-top: 0.6rem;
    transition: all 0.2s;
}
a.map-link:hover {
    background: #f59e0b33;
    border-color: var(--accent);
}
</style>
""", unsafe_allow_html=True)

# ─── CONFIG ─────────────────────────────────
# (unchanged — no logic changes)
MODEL_PATH = "Model/road_damage_detection_model.pt"
SENDER_EMAIL = "pragadeeshwarirajkumar215@gmail.com"
SENDER_PASSWORD = "cqumddvmxrsokzch"
RECEIVER_EMAIL = "mugilancse54@gmail.com"

# ─── LOAD MODEL ─────────────────────────────
# (unchanged)
@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)

model = load_model()

# ─── SESSION STATE ───────────────────────────
# (unchanged)
if "img" not in st.session_state:
    st.session_state.img = None
if "result" not in st.session_state:
    st.session_state.result = None
if "labels" not in st.session_state:
    st.session_state.labels = []

# ─── EMAIL FUNCTION ─────────────────────────
# (unchanged)
def send_email(report):
    msg = MIMEText(report)
    msg["Subject"] = "🚨 Road Damage Alert - Tamil Nadu Hackathon"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# ─── LOCATION SETUP ─────────────────────────
# (unchanged)
geolocator = Nominatim(user_agent="road_damage_app")

# ═══════════════════════════════════════════
#  UI — HERO HEADER
# UI CHANGE: Replaced plain st.title + st.markdown with branded hero block
# ═══════════════════════════════════════════
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">⬡ AI Vision System · v2.0</div>
    <div class="hero-title">Road <span>Damage</span> Detection</div>
    <div class="hero-sub">Tamil Nadu Hackathon · Intelligent Infrastructure Monitoring</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  UI — TWO-COLUMN LAYOUT: Upload + Location
# UI CHANGE: Wrapped sections in styled card divs with section labels
# ═══════════════════════════════════════════
col1, col2 = st.columns([1.1, 0.9], gap="medium")

with col1:
    # UI CHANGE: Card with mono label and accent left-border
    st.markdown("""
    <div class="section-card">
        <div class="card-label">01 · Input</div>
        <div class="card-title">Upload Road Image</div>
    </div>
    """, unsafe_allow_html=True)

    # (unchanged — original uploader logic)
    uploaded = st.file_uploader(
        "Drag & drop or click to browse — JPG, PNG, JPEG",
        type=["jpg", "png", "jpeg"],
        label_visibility="visible"
    )

    if uploaded:
        st.session_state.img = Image.open(uploaded)
        st.image(st.session_state.img, use_container_width=True, caption="")
        # UI CHANGE: Show a small status line after image loads
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                    color:#7d8590;margin-top:6px;letter-spacing:0.08em;">
            ✓ &nbsp;IMAGE LOADED &nbsp;·&nbsp; {uploaded.name}
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="section-card">
        <div class="card-label">02 · Location</div>
        <div class="card-title">Set Damage Location</div>
    </div>
    """, unsafe_allow_html=True)

    # (unchanged — original location logic)
    location_name = st.text_input(
        "Enter location name",
        placeholder="e.g. Madurai, Chennai, Coimbatore..."
    )

    lat, lon = None, None

    if location_name:
        try:
            location = geolocator.geocode(location_name)
            if location:
                lat, lon = location.latitude, location.longitude
                # UI CHANGE: Styled address display instead of plain st.success
                st.markdown(f"""
                <div style="background:#22c55e11;border:1px solid #22c55e44;border-radius:6px;
                            padding:10px 14px;margin-top:8px;display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.1rem;">📍</span>
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                    color:#22c55e;letter-spacing:0.1em;text-transform:uppercase;">
                            GEOCODED
                        </div>
                        <div style="color:#e6edf3;font-size:0.82rem;margin-top:2px;">
                            {location.address[:80]}{'...' if len(location.address) > 80 else ''}
                        </div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                                    color:#7d8590;margin-top:4px;">
                            {lat:.5f}° N, {lon:.5f}° E
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠ Location not found — try a more specific name")
        except:
            st.error("⚠ Error fetching location")

    # UI CHANGE: Helpful hint below location input
    if not location_name:
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                    color:#484f58;margin-top:10px;line-height:1.7;">
            ↳ Location is used to tag the damage report<br>
            ↳ GPS coordinates auto-resolved via geocoder
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  UI — DETECT BUTTON
# UI CHANGE: Wrapped in a centered, max-width container with spacing
# ═══════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)

btn_col = st.columns([1, 2, 1])[1]
with btn_col:
    detect_clicked = st.button("⬡  RUN DAMAGE DETECTION", use_container_width=True)

# ─── DETECT LOGIC ────────────────────────────
# (unchanged — original prediction logic)
if detect_clicked and st.session_state.img:
    with st.spinner("Analysing image with AI model..."):
        results = model.predict(st.session_state.img, conf=0.1)
        result_img = results[0].plot()[:, :, ::-1]
        st.session_state.result = result_img

        boxes = results[0].boxes
        labels = []
        if boxes is not None and len(boxes) > 0:
            for c, cf in zip(boxes.cls, boxes.conf):
                name = model.names[int(c)]
                labels.append(f"{name} ({cf*100:.2f}%)")
        st.session_state.labels = labels

elif detect_clicked and not st.session_state.img:
    st.warning("⚠ Please upload a road image before running detection.")

# ═══════════════════════════════════════════
#  UI — RESULTS SECTION
# UI CHANGE: Full redesign — metrics row, damage tags, styled report
# ═══════════════════════════════════════════
if st.session_state.result is not None:

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;letter-spacing:0.18em;
                color:#f59e0b;text-transform:uppercase;margin-bottom:1rem;display:flex;
                align-items:center;gap:10px;">
        03 · ANALYSIS RESULTS
        <span style="flex:1;height:1px;background:#21262d;display:inline-block;"></span>
    </div>
    """, unsafe_allow_html=True)

    res_col1, res_col2 = st.columns([1.2, 0.8], gap="medium")

    with res_col1:
        # UI CHANGE: Card wrapper around result image
        st.markdown('<div class="section-card" style="padding:1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">Detection Output</div>', unsafe_allow_html=True)
        st.image(st.session_state.result, use_container_width=True, caption="")
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        # UI CHANGE: Metrics row showing damage count + confidence
        num_detections = len(st.session_state.labels)
        
        # Parse confidence values for avg
        confs = []
        for lbl in st.session_state.labels:
            try:
                c = float(lbl.split("(")[1].replace("%)", ""))
                confs.append(c)
            except:
                pass
        avg_conf = f"{sum(confs)/len(confs):.1f}%" if confs else "—"

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">{num_detections}</div>
                <div class="metric-label">Defects Found</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_conf}</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{'HIGH' if num_detections >= 3 else 'MED' if num_detections >= 1 else 'LOW'}</div>
                <div class="metric-label">Severity</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # UI CHANGE: Damage tags instead of plain text
        if st.session_state.labels:
            st.markdown('<div class="card-label" style="margin-top:1rem;">Detected Damage Types</div>', unsafe_allow_html=True)
            tags_html = '<div class="damage-tags">'
            for lbl in st.session_state.labels:
                css_class = "damage-tag critical" if float(lbl.split("(")[1].replace("%)", "")) > 70 else "damage-tag"
                tags_html += f'<span class="{css_class}">{lbl}</span>'
            tags_html += '</div>'
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="no-damage">
                <span>✓</span> No structural damage detected in this image
            </div>
            """, unsafe_allow_html=True)

        # MAP section inside right column
        if lat and lon:
            st.markdown('<div class="card-label" style="margin-top:1.2rem;">Location Map</div>', unsafe_allow_html=True)
            st.map({"lat": [lat], "lon": [lon]})
            st.markdown(f"""
            <a class="map-link" href="https://www.google.com/maps?q={lat},{lon}" target="_blank">
                🌍 &nbsp;Open in Google Maps
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#f59e0b0d;border:1px solid #f59e0b33;border-radius:6px;
                        padding:10px 14px;font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                        color:#b45309;margin-top:1rem;">
                ⚠ &nbsp;Enter a valid location to plot on map
            </div>
            """, unsafe_allow_html=True)

    # ─── REPORT SECTION ────────────────────────
    # UI CHANGE: Styled report card instead of raw text_area
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;letter-spacing:0.18em;
                color:#f59e0b;text-transform:uppercase;margin-bottom:1rem;display:flex;
                align-items:center;gap:10px;">
        04 · INCIDENT REPORT
        <span style="flex:1;height:1px;background:#21262d;display:inline-block;"></span>
    </div>
    """, unsafe_allow_html=True)

    # (unchanged — original report string assembly)
    report = f"""
Road Damage Incident Report
Time         : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Damage       : {', '.join(st.session_state.labels) if st.session_state.labels else 'None detected'}
Location     : {location_name if location_name else 'Not Provided'}
Coordinates  : {f'{lat:.5f}, {lon:.5f}' if lat and lon else 'N/A'}
Map URL      : https://www.google.com/maps?q={lat},{lon}
Source       : AI Vision Model (Tamil Nadu Hackathon)
"""

    # UI CHANGE: Styled monospace report block instead of plain text_area
    st.markdown(f"""
    <div class="section-card">
        <div class="card-label">Generated Report</div>
        <div class="report-block">{report.strip()}</div>
    </div>
    """, unsafe_allow_html=True)

    # Keep hidden text_area for copy fallback (minimized)
    with st.expander("📋 Copy raw report text"):
        st.text_area("", report, height=160, label_visibility="collapsed")

    # ─── EMAIL BUTTON ──────────────────────────
    # (unchanged — original email logic)
    st.markdown("<br>", unsafe_allow_html=True)
    send_col = st.columns([1, 2, 1])[1]
    with send_col:
        if st.button("📩  DISPATCH REPORT TO OFFICER", use_container_width=True):
            if not location_name:
                st.error("⚠ Please enter a location before dispatching the report.")
            else:
                with st.spinner("Sending secure report..."):
                    if send_email(report):
                        st.markdown("""
                        <div style="background:#22c55e11;border:1px solid #22c55e44;border-radius:6px;
                                    padding:12px 16px;text-align:center;font-family:'JetBrains Mono',monospace;
                                    font-size:0.8rem;color:#22c55e;margin-top:8px;letter-spacing:0.08em;">
                            ✓ &nbsp;REPORT DISPATCHED SUCCESSFULLY
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Dispatch failed. Check email configuration.")

# ─── FOOTER ─────────────────────────────────
# UI CHANGE: Added a subtle footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:0.62rem;
            color:#484f58;letter-spacing:0.12em;border-top:1px solid #21262d;padding-top:1.2rem;">
    ROAD DAMAGE DETECTION SYSTEM &nbsp;·&nbsp; TAMIL NADU HACKATHON &nbsp;·&nbsp; AI VISION MODULE
</div>
""", unsafe_allow_html=True)