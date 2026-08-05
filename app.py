#Aapka streamlit ka code.
"""
💖 Glow Bank — an interactive Streamlit banking app
Rebuilt from a console-based Bank class into a slick, animated web UI.
"""

import json
import random
import string
import time
from pathlib import Path

import streamlit as st

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DB_PATH = Path(__file__).parent / "database.json"

st.set_page_config(
    page_title="Glow Bank",
    page_icon="💖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# STYLE
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #1f1147 0%, #4b1668 40%, #8f2d78 75%, #ff6b9d 100%);
        background-size: 300% 300%;
        animation: gradientShift 18s ease infinite;
    }

    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    section[data-testid="stSidebar"] {
        background: rgba(15, 8, 36, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .glow-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #ffd1ff, #fad0c4, #a18cd1, #ffd1ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 6s linear infinite;
        margin-bottom: 0;
        text-shadow: 0 0 30px rgba(255,255,255,0.15);
    }

    @keyframes shine {
        0% {background-position: 0% 50%;}
        100% {background-position: 300% 50%;}
    }

    .subtitle {
        text-align: center;
        color: #eadcff;
        opacity: 0.85;
        font-weight: 300;
        margin-top: -8px;
        margin-bottom: 1.6rem;
        letter-spacing: 1px;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 8px 32px rgba(31, 4, 61, 0.37);
        backdrop-filter: blur(8px);
        margin-bottom: 1.2rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 40px rgba(255, 107, 157, 0.35);
    }

    .avatar {
        width: 78px;
        height: 78px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(135deg, #ff6b9d, #a18cd1);
        margin: 0 auto 10px auto;
        box-shadow: 0 0 25px rgba(255, 107, 157, 0.55);
        animation: pulse 2.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 15px rgba(255, 107, 157, 0.4); }
        50% { box-shadow: 0 0 30px rgba(255, 107, 157, 0.8); }
        100% { box-shadow: 0 0 15px rgba(255, 107, 157, 0.4); }
    }

    div.stButton > button {
        background: linear-gradient(90deg, #ff6b9d, #a18cd1);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(255, 107, 157, 0.35);
    }
    div.stButton > button:hover {
        transform: scale(1.04);
        box-shadow: 0 8px 22px rgba(255, 107, 157, 0.55);
        color: white;
    }

    .metric-box {
        text-align: center;
        color: white;
    }

    .badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.15);
        font-size: 0.75rem;
        color: #fff;
        margin-left: 8px;
    }

    hr {
        border-color: rgba(255,255,255,0.15);
    }

    ::placeholder { color: rgba(255,255,255,0.5) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# DATA LAYER  (same logic as the original Bank class, made UI-safe)
# ------------------------------------------------------------------
def load_data():
    if DB_PATH.exists():
        try:
            with open(DB_PATH) as fs:
                return json.loads(fs.read())
        except Exception:
            return []
    return []


def save_data(data):
    with open(DB_PATH, "w") as fs:
        fs.write(json.dumps(data, indent=2))


def generate_account_no():
    letters = "".join(random.choices(string.ascii_uppercase, k=4))
    digits = "".join(random.choices(string.digits, k=8))
    return letters + digits


def find_user(data, acc_no, pin):
    matches = [u for u in data if u["accountno."] == acc_no and u["pin"] == pin]
    return matches[0] if matches else None


if "data" not in st.session_state:
    st.session_state.data = load_data()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = None  # holds the account dict once logged in


def refresh():
    st.session_state.data = load_data()


def initials(name):
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "🙂"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown('<div class="glow-title">💖 Glow Bank</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">banking, but make it sparkle ✨</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# SIDEBAR NAV
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌸 Menu")
    page = st.radio(
        "Navigate",
        [
            "🏠 Home",
            "✨ Create Account",
            "🔐 Login",
            "💸 Deposit",
            "🏧 Withdraw",
            "🪪 My Details",
            "✏️ Update Details",
            "🗑️ Close Account",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.session_state.logged_in:
        u = st.session_state.logged_in
        st.markdown(f'<div class="avatar">{initials(u["name"])}</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:white;'>Hi, <b>{u['name'].split()[0]}</b> 👋</p>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align:center;color:#eadcff;font-size:0.85rem;'>Acc: {u['accountno.']}</p>",
            unsafe_allow_html=True,
        )
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state.logged_in = None
            st.rerun()
    else:
        st.info("Not logged in yet — head to 🔐 Login")

# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------
if page == "🏠 Home":
    refresh()
    data = st.session_state.data
    total_accounts = len(data)
    total_balance = sum(u.get("Balance", 0) for u in data)

    c1, c2, c3 = st.columns(3)
    for col, label, value, emoji in [
        (c1, "Total Accounts", total_accounts, "🧑‍🤝‍🧑"),
        (c2, "Total Balance", f"₹{total_balance:,}", "💰"),
        (c3, "Avg Balance", f"₹{(total_balance // total_accounts) if total_accounts else 0:,}", "📊"),
    ]:
        with col:
            st.markdown(
                f"""<div class="glass-card metric-box">
                        <div style="font-size:2rem;">{emoji}</div>
                        <div style="font-size:1.7rem;font-weight:700;">{value}</div>
                        <div style="opacity:0.8;">{label}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="glass-card">
        <h4>Welcome to Glow Bank 🌟</h4>
        <p style="color:#eadcff;">
        A tiny, glowy corner of the internet where you can open an account,
        stash some virtual cash, and feel like a finance main character.
        Use the sidebar to get started — create an account, log in, and
        try depositing or withdrawing money. Everything is saved locally
        so your account will still be here next time. 💫
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------
# CREATE ACCOUNT
# ------------------------------------------------------------------
elif page == "✨ Create Account":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✨ Open a new account")

    with st.form("create_account_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1)
            mail = st.text_input("Email")
        with col2:
            number = st.text_input("10-digit phone number")
            pin = st.text_input("Choose a 4-digit PIN", type="password", max_chars=4)
            confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)

        submitted = st.form_submit_button("Create Account 💖", use_container_width=True)

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Please enter your name.")
        if age < 18:
            errors.append("You must be 18 or older to open an account.")
        if not mail.strip() or "@" not in mail:
            errors.append("Please enter a valid email.")
        if not (number.isdigit() and len(number) == 10):
            errors.append("Phone number must be exactly 10 digits.")
        if not (pin.isdigit() and len(pin) == 4):
            errors.append("PIN must be exactly 4 digits.")
        if pin != confirm_pin:
            errors.append("PIN and confirmation do not match.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            refresh()
            new_acc = generate_account_no()
            info = {
                "name": name.strip(),
                "age": int(age),
                "mail": mail.strip(),
                "Balance": 0,
                "accountno.": new_acc,
                "number": int(number),
                "pin": int(pin),
            }
            st.session_state.data.append(info)
            save_data(st.session_state.data)
            st.success(f"Account created! Your account number is **{new_acc}** — save it somewhere safe 💌")
            st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------
elif page == "🔐 Login":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔐 Log in to your account")

    with st.form("login_form"):
        acc_no = st.text_input("Account number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Login ✨", use_container_width=True)

    if submitted:
        refresh()
        try:
            user = find_user(st.session_state.data, acc_no.strip(), int(pin))
        except ValueError:
            user = None
        if user:
            st.session_state.logged_in = user
            with st.spinner("Unlocking your glowy dashboard..."):
                time.sleep(0.6)
            st.success(f"Welcome back, {user['name'].split()[0]}! 💖")
            st.rerun()
        else:
            st.error("Invalid account number or PIN.")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# DEPOSIT
# ------------------------------------------------------------------
elif page == "💸 Deposit":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💸 Deposit money")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 🔐 Login page.")
    else:
        refresh()
        user = find_user(st.session_state.data, st.session_state.logged_in["accountno."], st.session_state.logged_in["pin"])
        st.metric("Current Balance", f"₹{user['Balance']:,}")

        amount = st.number_input("Amount to deposit (₹)", min_value=1, max_value=100000, step=100)
        if st.button("Deposit 💰", use_container_width=True):
            user["Balance"] += int(amount)
            save_data(st.session_state.data)
            st.session_state.logged_in = user
            st.success(f"₹{amount:,} deposited successfully! New balance: ₹{user['Balance']:,} 🎉")
            st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# WITHDRAW
# ------------------------------------------------------------------
elif page == "🏧 Withdraw":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🏧 Withdraw money")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 🔐 Login page.")
    else:
        refresh()
        user = find_user(st.session_state.data, st.session_state.logged_in["accountno."], st.session_state.logged_in["pin"])
        st.metric("Current Balance", f"₹{user['Balance']:,}")

        amount = st.number_input("Amount to withdraw (₹)", min_value=1, step=100)
        if st.button("Withdraw 🏧", use_container_width=True):
            if amount > user["Balance"]:
                st.error("Insufficient balance 🥲")
            else:
                user["Balance"] -= int(amount)
                save_data(st.session_state.data)
                st.session_state.logged_in = user
                st.success(f"₹{amount:,} withdrawn. New balance: ₹{user['Balance']:,} ✅")
                st.snow()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# MY DETAILS
# ------------------------------------------------------------------
elif page == "🪪 My Details":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🪪 Account details")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 🔐 Login page.")
    else:
        refresh()
        user = find_user(st.session_state.data, st.session_state.logged_in["accountno."], st.session_state.logged_in["pin"])
        st.markdown(f'<div class="avatar">{initials(user["name"])}</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Age:** {user['age']}")
            st.write(f"**Email:** {user['mail']}")
        with c2:
            st.write(f"**Account No.:** {user['accountno.']}")
            st.write(f"**Phone:** {user['number']}")
            st.write(f"**Balance:** ₹{user['Balance']:,}")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# UPDATE DETAILS
# ------------------------------------------------------------------
elif page == "✏️ Update Details":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("✏️ Update your details")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 🔐 Login page.")
    else:
        refresh()
        user = find_user(st.session_state.data, st.session_state.logged_in["accountno."], st.session_state.logged_in["pin"])

        with st.form("update_form"):
            name = st.text_input("Name", value=user["name"])
            mail = st.text_input("Email", value=user["mail"])
            number = st.text_input("Phone number", value=str(user["number"]))
            new_pin = st.text_input("New 4-digit PIN (leave blank to keep current)", type="password", max_chars=4)
            submitted = st.form_submit_button("Save Changes 💾", use_container_width=True)

        if submitted:
            errors = []
            if not (number.isdigit() and len(number) == 10):
                errors.append("Phone number must be exactly 10 digits.")
            if new_pin and not (new_pin.isdigit() and len(new_pin) == 4):
                errors.append("New PIN must be exactly 4 digits.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                user["name"] = name.strip()
                user["mail"] = mail.strip()
                user["number"] = int(number)
                if new_pin:
                    user["pin"] = int(new_pin)
                save_data(st.session_state.data)
                st.session_state.logged_in = user
                st.success("Details updated successfully! ✅")

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# CLOSE ACCOUNT
# ------------------------------------------------------------------
elif page == "🗑️ Close Account":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🗑️ Close your account")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 🔐 Login page.")
    else:
        st.error("This action is permanent and cannot be undone.")
        confirm = st.checkbox("Yes, I understand and want to permanently close my account.")
        if st.button("Close Account 💔", use_container_width=True, disabled=not confirm):
            refresh()
            acc_no = st.session_state.logged_in["accountno."]
            st.session_state.data = [u for u in st.session_state.data if u["accountno."] != acc_no]
            save_data(st.session_state.data)
            st.session_state.logged_in = None
            st.success("Your account has been closed. Goodbye 👋")
            time.sleep(1.2)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)