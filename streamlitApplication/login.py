import streamlit as st #for the streamlit app
import sqlite3 #for database password operations
import hashlib #for password hashing when new users create accounts
import os #for generating a random salt
from pathlib import Path #for connecting to the database path


# locate the SQLite DB (sibling folder SQLiteApplication/Data/myTest.db)
DB_PATH = Path(__file__).resolve().parent.parent / "SQLiteApplication" / "Data" / "myTest.db"


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    # ensure users table exists
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
        """
    )
    conn.commit()
    return conn


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + "$" + dk.hex()


def _verify_password(stored: str, password: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
    except Exception:
        return False
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return dk.hex() == hash_hex


def create_user(username: str, password: str):
    if not username or not password:
        return False, "Username and password required"
    conn = _get_conn()
    cur = conn.cursor()
    try:
        pw_hash = _hash_password(password)
        cur.execute("INSERT INTO users(username, password_hash) VALUES(?,?)", (username, pw_hash))
        conn.commit()
        return True, "User registered"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)


def authenticate_user(username: str, password: str) -> bool:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        return False
    stored = row[0]
    return _verify_password(stored, password)


def app():
    st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

    st.markdown(
        """
        <h1 style="background: -webkit-linear-gradient(#00ffff, #333);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 48px;
                    font-weight: bold;
                    text-align: center;">
            Welcome
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # mode selector
    mode = st.radio("Mode", ("Login", "Register"), horizontal=True)

    if mode == "Register":
        st.subheader("Create a new account")
        new_user = st.text_input("Username", key="reg_user")
        new_pw = st.text_input("Password", type="password", key="reg_pw")
        new_pw2 = st.text_input("Confirm Password", type="password", key="reg_pw2")
        if st.button("Register"):
            if new_pw != new_pw2:
                st.error("Passwords do not match")
            else:
                ok, msg = create_user(new_user.strip(), new_pw)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    else:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Login"):
            if authenticate_user(username.strip(), password):
                st.success("Login successful")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username.strip()
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")


if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    app()
else:
    user = st.session_state.get('username', 'user')
    st.markdown(
        f"""
        <h2 style="background: -webkit-linear-gradient(#00ffff, #333);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 32px;
                    font-weight: bold;
                    text-align: center;">
            Welcome, {user}!
        </h2>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state.pop('username', None)
        st.experimental_rerun()

    if st.session_state['logged_in']:
        try:
            import webapps

            webapps.app()
        except Exception:
            st.info("Main app not available: webapps.app() could not be imported.")