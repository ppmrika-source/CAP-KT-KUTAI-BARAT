# =========================================================
# 📊 Aplikasi CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu)
# Pemerintah Kabupaten Kutai Barat
# Ready for Streamlit Cloud
# =========================================================

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import pandas as pd
import base64
import requests

# -------------------------
# 🔧 Konfigurasi halaman
# -------------------------
st.set_page_config(
    page_title="📊 CAP-KT Kutai Barat",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# 🔐 LOGIN GOOGLE
# -------------------------
# NOTE: Please set these secrets in Streamlit Cloud (Manage app → Settings → Secrets)
# Example secrets.toml keys:
# [google_oauth]
# client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
# client_secret = "YOUR_CLIENT_SECRET"
# redirect_uri = "https://cap-kt-kutai-barat.streamlit.app"

# Check secrets exist
if "google_oauth" not in st.secrets:
    st.error("🔒 Secrets untuk Google OAuth belum diset. Tambahkan di Manage app → Settings → Secrets dengan kunci [google_oauth].")
    st.info('Format: \n[google_oauth]\nclient_id = "..." \nclient_secret = "..." \nredirect_uri = "https://cap-kt-kutai-barat.streamlit.app"')
    st.stop()

client_id = st.secrets["google_oauth"].get("client_id", "")
client_secret = st.secrets["google_oauth"].get("client_secret", "")
redirect_uri = st.secrets["google_oauth"].get("redirect_uri", "")

if not client_id or not client_secret or not redirect_uri:
    st.error("🔒 Nilai client_id / client_secret / redirect_uri belum lengkap di secrets. Periksa kembali.")
    st.stop()

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPE = "openid email profile"

# Simple helper: build OAuth session
def make_oauth_session(state=None):
    return OAuth2Session(client_id, client_secret, scope=SCOPE, redirect_uri=redirect_uri, state=state)

# Handle OAuth flow
query_params = st.experimental_get_query_params()

if "user" not in st.session_state:
    # Step 1: user not logged in yet
    if "code" in query_params:
        # Returned from Google with ?code=...
        try:
            code = query_params["code"][0]
            oauth = make_oauth_session()
            token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
            # Get user info
            resp = requests.get(USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {token['access_token']}"})
            resp.raise_for_status()
            userinfo = resp.json()
            st.session_state.user = {
                "name": userinfo.get("name"),
                "email": userinfo.get("email"),
                "picture": userinfo.get("picture"),
                "raw": userinfo
            }
            # Clear query params and rerun to show app
            st.experimental_set_query_params()
            st.experimental_rerun()
        except Exception as e:
            st.error("Gagal menerima token/userinfo dari Google. Periksa Client ID/Secret dan Redirect URI di Google Cloud Console.\n\nDetail: " + str(e))
            st.stop()
    else:
        # Not yet authorized: show login link
        oauth = make_oauth_session()
        authorization_url, state = oauth.create_authorization_url(AUTHORIZATION_ENDPOINT)
        st.title("🔐 Login Diperlukan")
        st.markdown("Silakan login menggunakan akun Google institusi atau pribadi Anda untuk melanjutkan.")
        st.markdown(f"[👉 Login dengan Google]({authorization_url})")
        st.info("Jika tidak diarahkan kembali otomatis, pastikan redirect URI yang terdaftar di Google Cloud Console sama dengan: " + redirect_uri)
        st.stop()

# If here, user is logged in
user = st.session_state.get("user", {})
st.sidebar.image(user.get("picture", ""), width=64) if user.get("picture") else None
st.sidebar.write(f"👤 {user.get('name','-')}")
st.sidebar.write(f"✉️ {user.get('email','-')}")
if st.sidebar.button("🚪 Logout"):
    # clear only our keys (avoid removing secrets)
    for k in list(st.session_state.keys()):
        if k not in ("data_bantuan","data_upload"):
            del st.session_state[k]
    st.experimental_rerun()

# =========================================================
# 🎨 Gaya Header & Sidebar
# =========================================================
def add_bg_for_header(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .header-bg {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 20px;
                position: relative;
            }}
            .header-bg::before {{
                content: "";
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background-color: rgba(0,0,0,0.25);
                border-radius: 10px;
                z-index: 0;
            }}
            </style>
            <div class="header-bg"></div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # ignore missing image (app should still run)
        st.warning(f"Background header '{image_file}' tidak ditemukan — letakkan file di folder project jika ingin menampilkan header background.")

add_bg_for_header("background2.png")

# Sidebar background (non-fatal if missing)
sidebar_bg = "sidebar_bg.jpg"
try:
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                        url("file:///{sidebar_bg}");
            background-size: cover;
            background-position: center;
            color: white;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except Exception:
    pass

# Header logos (optional)
col1, col2, col3 = st.columns([1,6,1])
try:
    with col1:
        st.image("logo_kutai_barat.png", width=100)
except FileNotFoundError:
    with col1:
        st.write("")

with col2:
    st.markdown("""
        <h2 style='text-align: center; color: white; margin:0'>
        📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu)
        </h2>
        <h4 style='text-align: center; color:#F0F0F0; margin:0'>
        Bappeda Litbang Kutai Barat
        </h4>
    """, unsafe_allow_html=True)

try:
    with col3:
        st.image("logo_cap_kt.png", width=100)
except FileNotFoundError:
    with col3:
        st.write("")

st.markdown("Cek Aktivitas & Program Kemiskinan Terpadu untuk monitoring bantuan secara **mudah & interaktif**.")

# =========================================================
# 🧭 MENU NAVIGASI
# =========================================================
menu = st.sidebar.radio(
    "📂 Pilih Halaman:",
    ["Beranda", "Input Data", "Lihat Data", "Statistik", "Berbagi Data", "Tentang Aplikasi"]
)

# =========================================================
# --- Inisialisasi data
if "data_bantuan" not in st.session_state:
    st.session_state.data_bantuan = pd.DataFrame(columns=[
        "Program","Kegiatan","Sub Kegiatan","Kecamatan","Kampung",
        "Nama Individu","NIK Individu","Nama Kelompok/UMKM","Nama Pengurus & Anggota",
        "Nomor Registrasi/No. Akta Notaris Kelompok","Jenis Bantuan","Rincian Bantuan",
        "Jumlah Bantuan","Total PAGU"
    ])

# =========================================================
# BERANDA
if menu == "Beranda":
    st.title("🏠 Beranda")
    st.info("Selamat datang di Aplikasi CAP-KT Kutai Barat.")
    st.write("Anda login sebagai:", user.get("email"))

# INPUT DATA
elif menu == "Input Data":
    st.header("✍️ Form Input Data Bantuan")
    col1, col2 = st.columns(2)
    with col1:
        program = st.text_input("Program")
        kegiatan = st.text_input("Kegiatan")
        sub_kegiatan = st.text_input("Sub Kegiatan")
        nama_individu = st.text_input("Nama (Individu)")
        nik_individu = st.text_input("NIK (Individu)")
        kecamatan = st.text_input("Kecamatan")
        kampung = st.text_input("Kampung")
    with col2:
        nama_kelompok = st.text_input("Nama Kelompok / UMKM")
        pengurus_anggota = st.text_area("Nama Pengurus & Anggota Kelompok")
        nik_kelompok = st.text_input("Nomor Registrasi/No. Akta Notaris Kelompok")
        jenis_bantuan = st.selectbox("Jenis Bantuan", ["Modal Usaha","Alat Produksi","Pelatihan","Beasiswa","Bantuan Tunai","Bantuan Rumah Layak Huni","Lainnya"])
        rincian_bantuan = st.text_area("Rincian Bantuan")
    jumlah_bantuan = st.number_input("Jumlah Bantuan (Rp)", min_value=0, step=1000)
    total_PAGU = st.number_input("Total Penyerapan PAGU (Rp)", min_value=0, step=1000)
    if st.button("💾 Simpan Data"):
        new_data = pd.DataFrame([{
            "Program": program, "Kegiatan": kegiatan, "Sub Kegiatan": sub_kegiatan,
            "Kecamatan": kecamatan, "Kampung": kampung,
            "Nama Individu": nama_individu, "NIK Individu": nik_individu,
            "Nama Kelompok/UMKM": nama_kelompok, "Nama Pengurus & Anggota": pengurus_anggota,
            "Nomor Registrasi/No. Akta Notaris Kelompok": nik_kelompok, "Jenis Bantuan": jenis_bantuan,
            "Rincian Bantuan": rincian_bantuan, "Jumlah Bantuan": jumlah_bantuan, "Total PAGU": total_PAGU
        }])
        st.session_state.data_bantuan = pd.concat([st.session_state.data_bantuan, new_data], ignore_index=True)
        st.success("✅ Data berhasil disimpan!")

# LIHAT DATA
elif menu == "Lihat Data":
    st.header("📑 Data Bantuan Tersimpan")
    if not st.session_state.data_bantuan.empty:
        st.dataframe(st.session_state.data_bantuan, use_container_width=True)
        csv = st.session_state.data_bantuan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Data (CSV)", csv, "data_bantuan.csv", "text/csv")
    else:
        st.info("Belum ada data yang tersimpan.")

# STATISTIK
elif menu == "Statistik":
    st.header("📊 Statistik Data Bantuan")
    if not st.session_state.data_bantuan.empty:
        total_data = len(st.session_state.data_bantuan)
        total_jumlah = st.session_state.data_bantuan["Jumlah Bantuan"].sum()
        total_PAGU = st.session_state.data_bantuan["Total PAGU"].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Data", total_data)
        col2.metric("Total Jumlah Bantuan", f"Rp {total_jumlah:,.0f}")
        col3.metric("Total PAGU", f"Rp {total_PAGU:,.0f}")
        st.subheader("📌 Grafik Jumlah Bantuan per Jenis Bantuan")
        chart_data = st.session_state.data_bantuan.groupby("Jenis Bantuan")["Jumlah Bantuan"].sum()
        st.bar_chart(chart_data)
    else:
        st.info("Belum ada data untuk ditampilkan.")

# BERBAGI DATA
elif menu == "Berbagi Data":
    st.header("📂 Form Berbagi Data")
    if "data_upload" not in st.session_state:
        st.session_state["data_upload"] = []
    with st.form("form_berbagi_data"):
        nama_data = st.text_input("Nama Data")
        sub_kegiatan_opd = st.text_input("Sub Kegiatan OPD")
        unit_pengelola = st.text_input("Unit Pengelola Data (Produsen Data)")
        sumber_data = st.text_input("Sumber Data")
        deskripsi = st.text_area("Deskripsi Data")
        tujuan = st.text_area("Tujuan Pengumpulan Data")
        wilayah = st.text_input("Ruang Lingkup / Wilayah")
        waktu = st.text_input("Waktu Pengumpulan / Update")
        metode = st.text_input("Metode Pengumpulan")
        kualitas = st.text_area("Kualitas dan Validasi Data")
        indikator = st.text_input("Indikator Terkait")
        pemanfaatan = st.text_area("Pemanfaatan Data")
        rencana_bagi = st.text_area("Rencana Bagi Pakai Data")
        format_data = st.selectbox("Format Data", ["CSV","Excel","PDF","Word","Lainnya"])
        pic = st.text_input("PIC Metadata")
        gambaran_umum = st.text_area("Gambaran Umum Data")
        uploaded_file = st.file_uploader("Unggah File", type=["csv","xlsx","pdf","docx"])
        submitted = st.form_submit_button("📤 Upload Data")
        if submitted:
            if uploaded_file is not None:
                st.session_state["data_upload"].append({
                    "Nama Data": nama_data,
                    "Format Data": format_data,
                    "Unit Pengelola": unit_pengelola,
                    "Gambaran Umum": gambaran_umum,
                    "Nama File Asli": uploaded_file.name
                })
                st.success(f"✅ File '{uploaded_file.name}' berhasil diupload oleh {unit_pengelola}.")
            else:
                st.error("⚠️ Harap unggah file sebelum submit.")
    st.subheader("📑 Daftar Data yang Diupload")
    if len(st.session_state["data_upload"]) > 0:
        df = pd.DataFrame(st.session_state["data_upload"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data yang diupload.")

# TENTANG APLIKASI
elif menu == "Tentang Aplikasi":
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi **CAP-KT Kutai Barat** dikembangkan oleh **Bappeda Litbang Kabupaten Kutai Barat**  
    untuk mendukung pengelolaan data kemiskinan dan bantuan sosial secara terpadu.  

    **Fitur utama:**  
    - Login aman menggunakan Google 🔐  
    - Input dan visualisasi data kemiskinan 📋  
    - Statistik bantuan interaktif 📊  
    - Upload & berbagi data antar perangkat daerah 📤  
    - Desain antarmuka modern dan responsif 💻  
    """)

# =========================================================
# End of file
# =========================================================
