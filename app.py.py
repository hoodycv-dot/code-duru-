"""
Code-Duru (كودورو / Kudurru) AI Financial Guardian Platform
Built for: Agentic AI Challenge Iraq (قادة الذكاء الاصطناعي) Hackathon
Theme: Executive Minimalist Purple & White (SubTrack-inspired)
"""

import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Code-Duru | كودورو",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_json(filename):
    path = BASE_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


breached_data = load_json("breached_data.json")
transactions_data = load_json("transactions.json")

BREACH_MAP = {item["email"].lower(): item for item in breached_data["breached_emails"]}

# ----------------------------------------------------------------------------
# THEME / CSS — Purple & White Executive Minimalist (SubTrack-inspired)
# ----------------------------------------------------------------------------
PRIMARY_PURPLE = "#7C3AED"
ZAIN_PURPLE = "#5A189A"
BG_LIGHT = "#F8F7FF"
WHITE = "#FFFFFF"
DANGER_RED = "#DC2626"
SAFE_GREEN = "#16A34A"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG_LIGHT};
        font-family: 'Segoe UI', 'Tahoma', sans-serif;
    }}
    .kudurru-card {{
        background-color: {WHITE};
        border-radius: 18px;
        padding: 24px 28px;
        box-shadow: 0 4px 18px rgba(124, 58, 237, 0.08);
        border: 1px solid #EDE9FE;
        margin-bottom: 18px;
    }}
    .kudurru-title {{
        color: {ZAIN_PURPLE};
        font-weight: 800;
        font-size: 1.4rem;
        margin-bottom: 4px;
    }}
    .kudurru-subtitle {{
        color: #6B7280;
        font-size: 0.95rem;
        margin-bottom: 12px;
    }}
    .badge-safe {{
        background-color: #DCFCE7;
        color: {SAFE_GREEN};
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 700;
    }}
    .badge-danger {{
        background-color: #FEE2E2;
        color: {DANGER_RED};
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 700;
        animation: pulse 1.4s infinite;
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(220,38,38,0.4); }}
        70% {{ box-shadow: 0 0 0 12px rgba(220,38,38,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(220,38,38,0); }}
    }}
    .arabic-rtl {{
        direction: rtl;
        text-align: right;
        font-size: 1.05rem;
    }}
    div.stButton > button {{
        background-color: {PRIMARY_PURPLE};
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 22px;
        font-weight: 700;
        width: 100%;
    }}
    div.stButton > button:hover {{
        background-color: {ZAIN_PURPLE};
        color: white;
    }}
    .sub-row {{
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #F0EEFB;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# VOICE / ACCESSIBILITY HELPER (browser TTS via JS, Iraqi Arabic voice hint)
# ----------------------------------------------------------------------------
def speak_arabic(text: str):
    """Injects JS to read Arabic text aloud using the browser's speech synthesis."""
    safe_text = text.replace("\n", " ").replace('"', "'")
    st.components.v1.html(
        f"""
        <script>
        try {{
            const msg = new SpeechSynthesisUtterance("{safe_text}");
            msg.lang = "ar-IQ";
            msg.rate = 0.95;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        }} catch (e) {{ console.log("TTS not available", e); }}
        </script>
        """,
        height=0,
    )


def play_buzzer():
    """Plays an urgent alarm tone in-browser using the Web Audio API."""
    st.components.v1.html(
        """
        <script>
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            const ctx = new AudioCtx();
            function beep(freq, start, dur) {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "square";
                osc.frequency.value = freq;
                gain.gain.value = 0.15;
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(ctx.currentTime + start);
                osc.stop(ctx.currentTime + start + dur);
            }
            beep(880, 0, 0.25);
            beep(660, 0.3, 0.25);
            beep(880, 0.6, 0.25);
            beep(660, 0.9, 0.25);
        } catch (e) { console.log("Audio not available", e); }
        </script>
        """,
        height=0,
    )


def trigger_vapi_webhook(transaction):
    """
    Simulated call to n8n webhook -> Vapi.ai outbound call.
    In production, replace N8N_WEBHOOK_URL with the real n8n webhook endpoint,
    and this becomes a real `requests.post(...)` call.
    """
    payload = {
        "customer_name": transaction["customer_name_ar"],
        "customer_phone": transaction["customer_phone"],
        "transaction_id": transaction["id"],
        "amount_iqd": transaction["amount_iqd"],
        "script": transaction["call_script_ar_iq"],
        "timestamp": datetime.now().isoformat(),
    }
    # Example real integration (commented out — set your n8n URL in Replit Secrets):
    # import requests
    # requests.post(os.environ["N8N_WEBHOOK_URL"], json=payload, timeout=10)
    return payload


# ----------------------------------------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------------------------------------
defaults = {
    "step": "landing",
    "accessibility_mode": False,
    "email": "",
    "email_checked": False,
    "email_status": None,
    "kyc_done": False,
    "bank_connected": False,
    "fraud_state": "pending",  # pending -> frozen -> resolved
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(step):
    st.session_state.step = step
    st.rerun()


# ----------------------------------------------------------------------------
# HEADER (always visible)
# ----------------------------------------------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        f"<h1 style='color:{ZAIN_PURPLE}; font-weight:900;'>💜 Code-Duru <span style='color:{PRIMARY_PURPLE}; font-size:1.2rem;'>| كودورو</span></h1>",
        unsafe_allow_html=True,
    )
with col2:
    acc_label = "🔊 Voice Mode: ON" if st.session_state.accessibility_mode else "🔈 Voice Mode: OFF"
    if st.button(acc_label, key="acc_toggle"):
        st.session_state.accessibility_mode = not st.session_state.accessibility_mode
        st.rerun()

if st.session_state.accessibility_mode:
    st.markdown(
        "<div class='kudurru-card arabic-rtl'>🦻 <b>نمط المكفوفين وضعاف البصر مفعّل</b> — وكيل كودورو راح يقرالج كل خطوة صوتياً باللهجة العراقية.</div>",
        unsafe_allow_html=True,
    )

st.divider()

# ----------------------------------------------------------------------------
# STEP: LANDING
# ----------------------------------------------------------------------------
if st.session_state.step == "landing":
    st.markdown(
        """
        <div class="kudurru-card">
            <div class="kudurru-title">مرحباً بيك بمنصة كودورو 💜</div>
            <div class="kudurru-subtitle arabic-rtl">
                منصتك المصرفية الذكية المستوحاة من مسلات الكودورو البابلية — حماية حقوقك وأموالك بالذكاء الاصطناعي.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.accessibility_mode:
        speak_arabic("مرحباً بيك بمنصة كودورو. هسة راح نبدأ بإنشاء حسابك، خلينا نفحص بريدك الإلكتروني أول شي.")

    st.markdown("### Get Started")
    if st.button("🚀 Create Account / إنشاء حساب"):
        go("email_check")

# ----------------------------------------------------------------------------
# STEP: EMAIL BREACH CHECK
# ----------------------------------------------------------------------------
elif st.session_state.step == "email_check":
    st.markdown(
        """
        <div class="kudurru-card">
            <div class="kudurru-title">Step 1 · Email Security Check</div>
            <div class="kudurru-subtitle arabic-rtl">نفحص بريدك الإلكتروني آلياً مقابل بنك التسريبات العالمي</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Demo emails — try one: `judiesami@yahoo.com` (breached) or `dfghjhd.cv234@gmail.com` (safe)")
    email_input = st.text_input("Email Address", value=st.session_state.email, placeholder="you@example.com")

    if st.button("🔍 Check Email"):
        st.session_state.email = email_input
        key = email_input.strip().lower()
        result = BREACH_MAP.get(key)
        st.session_state.email_status = result if result else {"status": "unknown", "message_ar_iq": "إيميلچ مو موجود بقاعدة بياناتنا التجريبية — جرب أحد الإيميلين أعلاه للتجربة."}
        st.session_state.email_checked = True
        st.rerun()

    if st.session_state.email_checked and st.session_state.email_status:
        res = st.session_state.email_status
        if res["status"] == "breached":
            st.markdown(
                f"<div class='badge-danger arabic-rtl'>🚨 تنبيه! هذا الإيميل مكشوف بتسريب سابق ({res.get('breach_source','')})</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<p class='arabic-rtl'>{res['message_ar_iq']}</p>", unsafe_allow_html=True)
            st.warning("Preventive account freeze applied pending identity re-verification.")
            if st.session_state.accessibility_mode:
                speak_arabic(res["message_ar_iq"])
            if st.button("🔁 Try a different email"):
                st.session_state.email_checked = False
                st.rerun()
        elif res["status"] == "safe":
            st.markdown(
                "<div class='badge-safe arabic-rtl'>✅ إيميلچ آمن 100%! ننتقل الآن لتأكيد الهوية</div>",
                unsafe_allow_html=True,
            )
            if st.session_state.accessibility_mode:
                speak_arabic(res["message_ar_iq"])
            if st.button("➡️ Continue to Identity Verification"):
                go("kyc")
        else:
            st.info(res["message_ar_iq"])

# ----------------------------------------------------------------------------
# STEP: KYC
# ----------------------------------------------------------------------------
elif st.session_state.step == "kyc":
    st.markdown(
        """
        <div class="kudurru-card">
            <div class="kudurru-title">Step 2 · Digital Identity Verification (KYC)</div>
            <div class="kudurru-subtitle arabic-rtl">إدخال الرقم الوطني لربط الحساب بسجل الحوكمة</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Demo national ID: `199283746512`")
    national_id = st.text_input("National ID / الرقم الوطني", placeholder="199283746512")

    if st.button("✅ Verify Identity"):
        if national_id.strip() == transactions_data["customer"]["national_id"]:
            st.session_state.kyc_done = True
            st.success("Identity verified successfully / تم تأكيد الهوية بنجاح")
            if st.session_state.accessibility_mode:
                speak_arabic("تم تأكيد هويتك بنجاح، هسة نربط حسابك المصرفي.")
            time.sleep(0.6)
            go("connect_bank")
        else:
            st.error("Invalid National ID — try the demo ID above / الرقم الوطني غير صحيح")

# ----------------------------------------------------------------------------
# STEP: CONNECT BANK
# ----------------------------------------------------------------------------
elif st.session_state.step == "connect_bank":
    st.markdown(
        """
        <div class="kudurru-card">
            <div class="kudurru-title">Step 3 · Connect Your Bank / Zain Cash</div>
            <div class="kudurru-subtitle arabic-rtl">نقرأ تغذيتك المالية فقط — بدون تخزين أرقام بطاقاتك</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🏦 Connect a Bank"):
        with st.spinner("Connecting securely to Zain Cash..."):
            time.sleep(1.2)
        st.session_state.bank_connected = True
        st.success(f"{transactions_data['customer']['bank_linked']} connected successfully ✅")
        if st.session_state.accessibility_mode:
            speak_arabic("تم ربط حسابك بنجاح مع زين كاش. هسة تكدرين تشوفين اشتراكاتچ الدورية.")
        time.sleep(0.6)
        go("dashboard")

# ----------------------------------------------------------------------------
# STEP: DASHBOARD (Subscriptions + Fraud Radar)
# ----------------------------------------------------------------------------
elif st.session_state.step == "dashboard":
    customer = transactions_data["customer"]
    st.markdown(
        f"""
        <div class="kudurru-card">
            <div class="kudurru-title">أهلاً {customer['name_ar']} 👋</div>
            <div class="kudurru-subtitle">Balance: {customer['account_balance_iqd']:,} IQD &nbsp;|&nbsp; Linked: {customer['bank_linked']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📊 SubTrack Radar", "🛡️ Fraud Radar"])

    # ---- SUBSCRIPTIONS TAB ----
    with tab1:
        subs = transactions_data["subscriptions"]
        monthly_total = sum(s["amount_iqd"] for s in subs)
        st.markdown(
            f"<div class='kudurru-card arabic-rtl'>وين دتروح فلوسك؟ 💸<br>"
            f"<b>مجموع الاشتراكات الشهرية: {monthly_total:,} د.ع</b> — "
            f"<b>سنوياً: {monthly_total*12:,} د.ع</b></div>",
            unsafe_allow_html=True,
        )
        for s in subs:
            c1, c2, c3 = st.columns([1, 3, 2])
            c1.markdown(f"<div style='font-size:1.6rem'>{s['logo']}</div>", unsafe_allow_html=True)
            c2.markdown(f"**{s['name']}**  \n<span style='color:#9CA3AF'>{s['category']}</span>", unsafe_allow_html=True)
            c3.markdown(f"**{s['amount_iqd']:,} IQD**/mo  \n<span style='color:#9CA3AF'>renews {s['next_renewal']}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:4px 0; border-color:#F0EEFB;'>", unsafe_allow_html=True)

        st.info("🔔 تنبيه استباقي: راح نذكرچ بـ 24 ساعة كل ما يقرب موعد تجديد اشتراك، وتكدرين تلغين فوراً من هنا.")

    # ---- FRAUD RADAR TAB ----
    with tab2:
        fraud = transactions_data["fraud_scenario"]

        st.markdown("#### Recent Transactions")
        for t in transactions_data["normal_transactions"]:
            st.markdown(
                f"<div class='sub-row'><span>{t['merchant']}</span>"
                f"<span>{t['amount_iqd']:,} IQD — {t['date']}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("#### ⚠️ Live Threat Monitor")

        if st.session_state.fraud_state == "pending":
            st.warning("Monitoring active transactions in real time...")
            if st.button("▶️ Simulate: Suspicious external withdrawal detected"):
                st.session_state.fraud_state = "frozen"
                st.rerun()

        elif st.session_state.fraud_state == "frozen":
            play_buzzer()
            st.markdown(
                f"""
                <div class="badge-danger arabic-rtl">
                🚨 محاولة سحب خارجي مشبوهة بمبلغ {fraud['amount_iqd']:,} د.ع رُصدت الآن!<br>
                المعاملة مجمدة وقائياً قبل خصم أي مبلغ من رصيدچ.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
            st.markdown(f"**Destination:** {fraud['merchant']}")
            st.markdown(f"**Risk flags:** {', '.join(fraud['risk_flags'])}")

            if st.session_state.accessibility_mode:
                speak_arabic("رصدنا محاولة سحب خارجي مشبوهة، جمدنا المعاملة، هسة رح نتصل بيچ للتأكيد.")

            if st.button("📞 Trigger Live Voice Call to Customer (Vapi.ai)"):
                with st.spinner("Dialing 07709044763 via Vapi.ai / n8n webhook..."):
                    trigger_vapi_webhook(fraud)
                    time.sleep(1.5)
                st.markdown(
                    f"<div class='kudurru-card arabic-rtl'>📞 <b>سجل المكالمة:</b><br>{fraud['call_script_ar_iq']}</div>",
                    unsafe_allow_html=True,
                )
                if st.session_state.accessibility_mode:
                    speak_arabic(fraud["call_script_ar_iq"])
                st.markdown(
                    f"<div class='kudurru-card arabic-rtl' style='color:{ZAIN_PURPLE};'>🗣️ <b>رد الزبونة:</b> \"{fraud['expected_customer_response_ar_iq']}\"</div>",
                    unsafe_allow_html=True,
                )
                st.session_state.fraud_state = "awaiting_confirm"
                time.sleep(1)
                st.rerun()

        elif st.session_state.fraud_state == "awaiting_confirm":
            st.markdown(
                f"<div class='kudurru-card arabic-rtl'>🗣️ <b>رد الزبونة:</b> \"{fraud['expected_customer_response_ar_iq']}\"</div>",
                unsafe_allow_html=True,
            )
            if st.button("✅ Apply Customer Decision (Cancel & Block)"):
                st.session_state.fraud_state = "resolved"
                st.rerun()

        elif st.session_state.fraud_state == "resolved":
            st.markdown(
                "<div class='badge-safe arabic-rtl'>✅ تم إلغاء المعاملة وحظر الحساب الخارجي بنجاح — القرار موثق بسجل الكودورو المحصن.</div>",
                unsafe_allow_html=True,
            )
            st.balloons()
            if st.session_state.accessibility_mode:
                speak_arabic("تم إلغاء المعاملة وحظر الحساب الخارجي، فلوسچ بأمان تام.")
            st.json(
                {
                    "transaction_id": fraud["id"],
                    "resolution_status": "cancelled_and_blocked",
                    "resolved_at": datetime.now().isoformat(),
                    "logged_to": "Kudurru Immutable Ledger",
                }
            )
            if st.button("🔄 Reset Demo"):
                st.session_state.fraud_state = "pending"
                st.rerun()

    st.divider()
    if st.button("⬅️ Restart Full Demo Flow"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
