import streamlit as st
from pathlib import Path
import json
import random
import string

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------

DATABASE = "database.json"

# Canonical schema keys — every account record is guaranteed to have these
# after passing through _normalize(). This is what prevents KeyErrors when
# older/malformed records exist in database.json.
REQUIRED_KEYS = {
    "name": "",
    "age": 0,
    "mail": "",
    "balance": 0,
    "accountno.": "",
    "pin": 0,
    "number": 0,
}


def _normalize(record: dict) -> dict:
    """Fill in any missing keys on a record so downstream code never KeyErrors."""
    fixed = dict(REQUIRED_KEYS)
    fixed.update(record)
    return fixed


def load_data():
    if Path(DATABASE).exists():
        try:
            with open(DATABASE) as fs:
                raw = json.loads(fs.read())
        except Exception as err:
            st.error(f"Could not read database.json: {err}")
            return []
        # Normalize every record on load so old/malformed entries can't crash the app
        return [_normalize(r) for r in raw]
    return []


def save_data(data):
    with open(DATABASE, "w") as fs:
        fs.write(json.dumps(data, indent=2))


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "logged_in_acc" not in st.session_state:
    st.session_state.logged_in_acc = None  # holds the account number once logged in


# ----------------------------------------------------------------------------
# Bank logic
# ----------------------------------------------------------------------------

def generate_acc_no():
    chars = random.choices(string.ascii_uppercase, k=4)
    digits = random.choices(string.digits, k=8)
    return "".join(chars + digits)


def find_user(data, acc_no, pin):
    """Safe lookup — uses .get() so a record missing a key is just skipped,
    never raises a KeyError."""
    matches = [
        u for u in data
        if u.get("accountno.") == acc_no and u.get("pin") == pin
    ]
    return matches[0] if matches else None


def get_current_user():
    if not st.session_state.logged_in_acc:
        return None
    matches = [
        u for u in st.session_state.data
        if u.get("accountno.") == st.session_state.logged_in_acc
    ]
    return matches[0] if matches else None


def create_account(name, age, mail, pin, number):
    if len(str(pin)) != 4:
        return False, "Your PIN must be exactly 4 digits."
    if len(str(number)) != 10:
        return False, "Your phone number must be exactly 10 digits."
    if age < 18:
        return False, "You must be 18 or older to open an account."

    info = _normalize({
        "name": name,
        "age": age,
        "mail": mail,
        "balance": 0,
        "accountno.": generate_acc_no(),
        "pin": pin,
        "number": number,
    })
    st.session_state.data.append(info)
    save_data(st.session_state.data)
    return True, info


def deposit_money(acc_no, pin, amount):
    user = find_user(st.session_state.data, acc_no, pin)
    if not user:
        return False, "Invalid account number or PIN."
    if amount > 100000 or amount <= 0:
        return False, "You cannot deposit more than ₹100,000 or an amount ≤ 0."
    user["balance"] += amount
    save_data(st.session_state.data)
    return True, user["balance"]


def withdraw_money(acc_no, pin, amount):
    user = find_user(st.session_state.data, acc_no, pin)
    if not user:
        return False, "Invalid account number or PIN."
    if amount <= 0:
        return False, "Enter an amount greater than 0."
    if amount >= user["balance"]:
        return False, "You don't have sufficient balance."
    user["balance"] -= amount
    save_data(st.session_state.data)
    return True, user["balance"]


def update_details(acc_no, pin, new_name, new_mail, new_number, new_pin):
    user = find_user(st.session_state.data, acc_no, pin)
    if not user:
        return False, "Invalid account number or PIN."

    if new_name.strip():
        user["name"] = new_name.strip()
    if new_mail.strip():
        user["mail"] = new_mail.strip()
    if new_number.strip():
        if len(new_number.strip()) != 10 or not new_number.strip().isdigit():
            return False, "Phone number must be exactly 10 digits."
        user["number"] = int(new_number.strip())
    if new_pin.strip():
        if len(new_pin.strip()) != 4 or not new_pin.strip().isdigit():
            return False, "PIN must be exactly 4 digits."
        user["pin"] = int(new_pin.strip())

    save_data(st.session_state.data)
    return True, user


def close_account(acc_no, pin):
    user = find_user(st.session_state.data, acc_no, pin)
    if not user:
        return False, "Invalid account number or PIN."
    st.session_state.data.remove(user)
    save_data(st.session_state.data)
    st.session_state.logged_in_acc = None
    return True, "Account closed successfully."


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Bank Management", page_icon="🏦", layout="centered")

with st.sidebar:
    st.markdown("## 🏦 Menu")
    if st.session_state.logged_in_acc:
        pages = ["Home", "Deposit", "Withdraw", "My Details", "Update Details", "Close Account"]
        st.success(f"Logged in: {st.session_state.logged_in_acc}")
        if st.button("Logout"):
            st.session_state.logged_in_acc = None
            st.rerun()
    else:
        pages = ["Home", "Create Account", "Login"]
        st.info("Not logged in yet — head to 🔒 Login")

    page = st.radio("Navigate", pages, label_visibility="collapsed")

# ---------------- Home ----------------
if page == "Home":
    st.title("🏦 Welcome to Bank Management")
    st.write("Use the menu on the left to create an account, log in, and manage your money.")
    st.metric("Total accounts", len(st.session_state.data))

# ---------------- Create Account ----------------
elif page == "Create Account":
    st.title("✨ Create Account")
    with st.form("create_account_form"):
        name = st.text_input("Full name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        mail = st.text_input("Email")
        pin = st.text_input("Choose a 4-digit PIN", type="password", max_chars=4)
        number = st.text_input("10-digit phone number", max_chars=10)
        submitted = st.form_submit_button("Create Account")

    if submitted:
        errors = []
        if not name.strip():
            errors.append("Name is required.")
        if not mail.strip():
            errors.append("Email is required.")
        if not pin.isdigit():
            errors.append("PIN must contain only digits.")
        if not number.isdigit():
            errors.append("Phone number must contain only digits.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            ok, result = create_account(name.strip(), int(age), mail.strip(), int(pin), int(number))
            if ok:
                st.success("🎉 Account created successfully! Save your account number below.")
                st.balloons()
                st.code(result["accountno."], language=None)
            else:
                st.error(result)

# ---------------- Login ----------------
elif page == "Login":
    st.title("🔒 Log in to your account")
    with st.form("login_form"):
        acc_no = st.text_input("Account number")
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Login ✨")

    if submitted:
        if not pin.isdigit():
            st.error("PIN must contain only digits.")
        else:
            user = find_user(st.session_state.data, acc_no.strip(), int(pin))
            if user:
                st.session_state.logged_in_acc = user["accountno."]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid account number or PIN.")

# ---------------- Pages below require login ----------------
elif page == "Deposit":
    st.title("💰 Deposit Money")
    user = get_current_user()
    if not user:
        st.error("Please log in first.")
    else:
        with st.form("deposit_form"):
            amount = st.number_input("Amount to deposit (₹)", min_value=0, step=100)
            submitted = st.form_submit_button("Deposit")
        if submitted:
            ok, result = deposit_money(user["accountno."], user["pin"], int(amount))
            if ok:
                st.success("✅ Deposit successful!")
                st.metric("New balance", f"₹{result}")
            else:
                st.error(result)

elif page == "Withdraw":
    st.title("💸 Withdraw Money")
    user = get_current_user()
    if not user:
        st.error("Please log in first.")
    else:
        with st.form("withdraw_form"):
            amount = st.number_input("Amount to withdraw (₹)", min_value=0, step=100)
            submitted = st.form_submit_button("Withdraw")
        if submitted:
            ok, result = withdraw_money(user["accountno."], user["pin"], int(amount))
            if ok:
                st.success("✅ Withdrawal successful!")
                st.metric("New balance", f"₹{result}")
            else:
                st.error(result)

elif page == "My Details":
    st.title("📇 My Details")
    user = get_current_user()
    if not user:
        st.error("Please log in first.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Balance", f"₹{user['balance']}")
        col2.metric("Age", user["age"])
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['mail']}")
        st.write(f"**Phone:** {user['number']}")
        st.write(f"**Account No.:** {user['accountno.']}")

elif page == "Update Details":
    st.title("✏️ Update Details")
    st.caption("Leave a field blank to keep it unchanged.")
    user = get_current_user()
    if not user:
        st.error("Please log in first.")
    else:
        with st.form("update_form"):
            new_name = st.text_input("New name (optional)")
            new_mail = st.text_input("New email (optional)")
            new_number = st.text_input("New 10-digit phone number (optional)", max_chars=10)
            new_pin = st.text_input("New 4-digit PIN (optional)", type="password", max_chars=4)
            submitted = st.form_submit_button("Update Details")
        if submitted:
            ok, result = update_details(
                user["accountno."], user["pin"], new_name, new_mail, new_number, new_pin
            )
            if ok:
                st.success("✅ Details updated successfully!")
            else:
                st.error(result)

elif page == "Close Account":
    st.title("🗑️ Close Account")
    st.warning("This action is permanent and cannot be undone.")
    user = get_current_user()
    if not user:
        st.error("Please log in first.")
    else:
        confirm = st.checkbox("I understand this will permanently delete my account")
        if st.button("Close Account"):
            if not confirm:
                st.error("Please check the confirmation box to proceed.")
            else:
                ok, result = close_account(user["accountno."], user["pin"])
                if ok:
                    st.success(result)
                    st.rerun()
                else:
                    st.error(result)