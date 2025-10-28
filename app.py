import streamlit as st
import pandas as pd
import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import gspread
from google.oauth2.service_account import Credentials
import os
# ----------------------------
# KONFIGURASI HALAMAN
# ----------------------------
st.set_page_config(
    page_title="📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat",
    page_icon="📂",
    layout="wide"
)

# ----------------------------
# AMBIL DATA RAHASIA DARI secrets.toml
# ----------------------------
try:
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
except KeyError:
    st.error("❌ Konfigurasi Google OAuth belum diatur di Secrets Streamlit Cloud.")
    st.stop()

# ----------------------------
# URL & KONSTANTA GOOGLE OAUTH
# ----------------------------
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPE = "openid email profile"

# ----------------------------
# FUNGSI PEMBANTU
# ----------------------------
def make_oauth_session(state=None):
    return OAuth2Session(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        state=state
    )

# ----------------------------
# PROSES LOGIN GOOGLE
# ----------------------------
if "email" not in st.session_state:
    params = st.query_params
    code = params.get("code")
    error = params.get("error")

    if error:
        st.error(f"Login error: {error}")
        st.stop()

    if code:
        try:
            oauth = make_oauth_session()
            token = oauth.fetch_token(
                url=TOKEN_URL,
                code=code,
                grant_type="authorization_code",
                redirect_uri=redirect_uri
            )

            headers = {"Authorization": f"Bearer {token['access_token']}"}
            resp = oauth.get(USERINFO_URL, headers=headers)
            userinfo = resp.json()

            st.session_state.email = userinfo.get("email")
            st.session_state.name = userinfo.get("name")

            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Gagal login: {e}")
            st.stop()

    else:
        oauth = make_oauth_session()
        authorization_url, state = oauth.create_authorization_url(AUTH_URL)
        st.title("🔐 Login Diperlukan")
        st.markdown(f"[➡️ Login dengan Google]({authorization_url})")
        st.stop()


    # --- Tahap 1: Jika belum login, tampilkan tombol login ---
else:
        oauth = make_oauth_session()
        authorization_url, state = oauth.create_authorization_url(AUTH_URL)       

# ----------------------------
# KONTEN APLIKASI SETELAH LOGIN
# ----------------------------
st.success(f"✅ Login berhasil sebagai {st.session_state.email}")

st.markdown("### 🎉 Selamat datang di Aplikasi CAP-KT")
st.write("Anda sudah berhasil login. Silakan lanjut ke fitur utama aplikasi.")
# Tombol Logout
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

st.set_page_config(page_title="📊 CAP-KT Kutai Barat", layout="wide")

# ======================
# 🔴 FIREBASE SETUP
# ======================
try:
    # Ambil dict dari secrets
    firebase_cred_dict = dict(st.secrets["firebase"])
    firebase_cred_dict["private_key"] = firebase_cred_dict["private_key"].replace("\\n", "\n")
    
    cred = credentials.Certificate(firebase_cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    st.sidebar.success("✅ Firebase terhubung")
except Exception as e:
    st.sidebar.warning(f"⚠️ Firebase gagal: {e}")
    db = None

# ======================
# 🔵 SQLITE LOCAL
# ======================
conn = sqlite3.connect("data_local.db", check_same_thread=False)
c = conn.cursor()
# Buat tabel jika belum ada
c.execute("""
CREATE TABLE IF NOT EXISTS bantuan(
    Program TEXT, Kegiatan TEXT, Sub_Kegiatan TEXT,
    Nama_Individu TEXT, NIK_Individu TEXT,
    Kecamatan TEXT, Kampung TEXT,
    Nama_Kelompok TEXT, Pengurus_Anggota TEXT,
    No_Akta TEXT,
    Jenis_Bantuan TEXT, Rincian_Bantuan TEXT,
    Jumlah_Bantuan REAL, Total_PAGU REAL,
    OPD TEXT
)
""")
conn.commit()

# ======================
# 🔵 GOOGLE SHEET SETUP
# ======================
sheet = None
try:
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    credentials_gs = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(credentials_gs)
    SHEET_URL = st.secrets.get("sheet_url")
    if SHEET_URL:
        sheet = client.open_by_url(SHEET_URL).sheet1
        st.sidebar.success(f"✅ Terhubung ke Google Sheet: {sheet.title}")
except Exception as e:
    st.sidebar.warning(f"⚠️ Google Sheet gagal: {e}")
    sheet = None

# ======================
# 📑 SESSION STATE
# ======================
if "data_bantuan" not in st.session_state:
    st.session_state.data_bantuan = pd.DataFrame(columns=[
        "Program", "Kegiatan", "Sub Kegiatan", "Nama Individu", "NIK Individu",
        "Kecamatan", "Kampung", "Nama Kelompok", "Pengurus_Anggota",
        "No_Akta", "Jenis Bantuan", "Rincian Bantuan",
        "Jumlah_Bantuan", "Total_PAGU", "OPD"
    ])

# ======================
# MENU NAVIGASI
# ======================
menu = st.sidebar.selectbox("Pilih Menu", ["Input Data", "Lihat Data", "Statistik", "Tentang"])
if menu == "Input Data":
    st.header("✍️ Input Data Bantuan")
    
    col1, col2 = st.columns(2)
    with col1:
        program = st.text_input("Program")
        kegiatan = st.text_input("Kegiatan")
        sub_kegiatan = st.text_input("Sub Kegiatan")
        nama_individu = st.text_input("Nama Individu")
        nik_individu = st.text_input("NIK")
        kecamatan = st.text_input("Kecamatan")
        kampung = st.text_input("Kampung")
    with col2:
        nama_kelompok = st.text_input("Nama Kelompok")
        pengurus_anggota = st.text_area("Pengurus & Anggota")
        no_akta = st.text_input("No. Akta")
        jenis_bantuan = st.selectbox("Jenis Bantuan", ["Modal Usaha", "Beasiswa", "Bantuan Tunai", "Lainnya"])
        rincian_bantuan = st.text_area("Rincian Bantuan")
        jumlah_bantuan = st.number_input("Jumlah Bantuan", min_value=0, step=1000)
        total_pagu = st.number_input("Total PAGU", min_value=0, step=1000)
        opd = st.text_input("OPD Penanggung Jawab")
    
    if st.button("💾 Simpan Data"):
        new_data = pd.DataFrame([{
            "Program": program, "Kegiatan": kegiatan, "Sub Kegiatan": sub_kegiatan,
            "Nama Individu": nama_individu, "NIK Individu": nik_individu,
            "Kecamatan": kecamatan, "Kampung": kampung,
            "Nama Kelompok": nama_kelompok, "Pengurus_Anggota": pengurus_anggota,
            "No_Akta": no_akta, "Jenis Bantuan": jenis_bantuan, "Rincian_Bantuan": rincian_bantuan,
            "Jumlah_Bantuan": jumlah_bantuan, "Total_PAGU": total_pagu, "OPD": opd
        }])
        
        # 🔹 Simpan ke Firebase
        try:
            if db:
                db.collection("data_capkt").add(new_data.to_dict(orient="records")[0])
                st.success("✅ Data tersimpan di Firebase")
        except Exception as e:
            st.warning(f"⚠️ Firebase gagal: {e}")
        
        # 🔹 Simpan ke SQLite fallback
        try:
            c.execute("""
            INSERT INTO bantuan VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(new_data.iloc[0]))
            conn.commit()
            st.success("✅ Data tersimpan di SQLite lokal")
        except Exception as e:
            st.error(f"❌ SQLite gagal: {e}")
        
        # 🔹 Simpan ke Google Sheet
        try:
            if sheet:
                sheet.append_row(new_data.iloc[0].tolist(), value_input_option="USER_ENTERED")
                st.success("✅ Data tersimpan di Google Sheet")
        except Exception as e:
            st.warning(f"⚠️ Google Sheet gagal: {e}")
        
        # 🔹 Simpan ke session state
        st.session_state.data_bantuan = pd.concat([st.session_state.data_bantuan, new_data], ignore_index=True)

elif menu == "Lihat Data":
    st.header("📑 Data Bantuan Tersimpan")
    df_display = st.session_state.data_bantuan.copy()
    if df_display.empty and db:
        # Ambil dari Firebase
        try:
            data_fb = [doc.to_dict() for doc in db.collection("data_capkt").stream()]
            df_display = pd.DataFrame(data_fb)
        except:
            pass
    st.dataframe(df_display, use_container_width=True)
    if not df_display.empty:
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "data_bantuan.csv", "text/csv")
    else:
        st.info("Belum ada data tersimpan.")

elif menu == "Statistik":
    st.header("📊 Statistik Data Bantuan")
    df_stat = st.session_state.data_bantuan
    if not df_stat.empty:
        st.metric("Total Data", len(df_stat))
        st.metric("Total Jumlah Bantuan", f"Rp {df_stat['Jumlah_Bantuan'].sum():,.0f}")
        st.metric("Total PAGU", f"Rp {df_stat['Total_PAGU'].sum():,.0f}")
        chart_data = df_stat.groupby("Jenis Bantuan")["Jumlah_Bantuan"].sum()
        st.bar_chart(chart_data)
    else:
        st.info("Belum ada data untuk ditampilkan.")

elif menu == "Tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi CAP-KT untuk monitoring penyaluran bantuan di Kutai Barat.
    - Input data bantuan lengkap
    - Statistik interaktif
    - Export data ke CSV
    """)

