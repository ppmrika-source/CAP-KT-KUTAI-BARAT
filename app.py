import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import pandas as pd
import base64
import os

# ------------------------------------
# KONFIGURASI HALAMAN
# ------------------------------------
st.set_page_config(
    page_title="📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat",
    page_icon="📂",
    layout="wide"
)

# ------------------------------------
# AUTENTIKASI GOOGLE
# ------------------------------------
try:
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
except KeyError:
    st.error("❌ Konfigurasi Google OAuth belum diatur di Secrets Streamlit Cloud.")
    st.stop()

auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"

if "email" not in st.session_state:
    # OAuth session
    oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope="openid email profile")
    auth_link = oauth.create_authorization_url(auth_url)[0]

    st.title("🔐 Login Diperlukan")
    st.markdown(f"[➡️ Login dengan Google]({auth_link})")
    st.stop()
else:
    st.success(f"✅ Login berhasil sebagai {st.session_state.email}")

# Tombol Logout
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# ------------------------------------
# FUNGSI TAMBAHAN: Background Header
# ------------------------------------
def add_bg_for_header(image_file):
    if not os.path.exists(image_file):
        st.warning(f"⚠️ File {image_file} tidak ditemukan.")
        return
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .header-bg {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            padding: 40px;
            margin-bottom: 20px;
            position: relative;
        }}
        .header-bg::before {{
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.18);
            border-radius: 10px;
            z-index: 0;
        }}
        .stApp, .stApp * {{ color: #2E86C1 !important; }}
        label[data-baseweb="label"] {{
            font-weight: bold !important;
            color: #2E86C1 !important;
            background-color: white !important;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        </style>
        <div class="header-bg"></div>
        """,
        unsafe_allow_html=True
    )

add_bg_for_header("background2.png")

# ------------------------------------
# HEADER
# ------------------------------------
col1, col2, col3 = st.columns([1,6,1])
with col1:
    st.image("logo_kutai_barat.png", width=100)
with col2:
    st.markdown("""
        <h2 style='text-align: center; color: #FFFFFF;'>
        📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat
        </h2>
        <h4 style='text-align: center; color:#F0F0F0;'>
        Bappeda Litbang Kutai Barat
        </h4>
    """, unsafe_allow_html=True)
with col3:
    st.image("logo_cap_kt.png", width=100)

# ------------------------------------
# MENU SIDEBAR
# ------------------------------------
st.sidebar.title("🔎 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Beranda", "Input Data", "Lihat Data", "Statistik", "Tentang"]
)

# ------------------------------------
# DATAFRAME SESSION
# ------------------------------------
if "data_bantuan" not in st.session_state:
    st.session_state.data_bantuan = pd.DataFrame(columns=[
        "Program", "Kegiatan", "Sub Kegiatan", "Kecamatan", "Kampung",
        "Nama Individu", "NIK Individu",
        "Nama Kelompok/UMKM", "Nama Pengurus & Anggota",
        "Nomor Registrasi/No. Akta Notaris Kelompok",
        "Jenis Bantuan", "Rincian Bantuan",
        "Jumlah Bantuan", "Total Realisasi PAGU"
    ])

# ------------------------------------
# HALAMAN BERANDA
# ------------------------------------
if menu == "Beranda":
    st.title("🏠 Beranda")
    st.markdown("""
    Selamat datang di **CAP-KT Kutai Barat** — Sistem Cek Aktivitas & Program Kemiskinan Terpadu.  
    Gunakan menu di kiri untuk:
    - Menginput Data 📥  
    - Melihat & Mengekspor Data 📄  
    - Menganalisis Bantuan 📊
    """)

# ------------------------------------
# HALAMAN INPUT DATA
# ------------------------------------
elif menu == "Input Data":
    st.title("📝 Input Data Bantuan")

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
        jenis_bantuan = st.selectbox("Jenis Bantuan", ["Modal Usaha", "Alat Produksi", "Pelatihan", "Beasiswa", "Tunai", "Rumah Layak Huni", "Lainnya"])
        rincian_bantuan = st.text_area("Rincian Bantuan")

    jumlah_bantuan = st.number_input("Jumlah Bantuan (Rp)", min_value=0, step=1000)
    total_PAGU = st.number_input("Total Realisasi PAGU (Rp)", min_value=0, step=1000)

    if st.button("💾 Simpan Data"):
        new_data = pd.DataFrame([{
            "Program": program,
            "Kegiatan": kegiatan,
            "Sub Kegiatan": sub_kegiatan,
            "Kecamatan": kecamatan,
            "Kampung": kampung,
            "Nama Individu": nama_individu,
            "NIK Individu": nik_individu,
            "Nama Kelompok/UMKM": nama_kelompok,
            "Nama Pengurus & Anggota": pengurus_anggota,
            "Nomor Registrasi/No. Akta Notaris Kelompok": nik_kelompok,
            "Jenis Bantuan": jenis_bantuan,
            "Rincian Bantuan": rincian_bantuan,
            "Jumlah Bantuan": jumlah_bantuan,
            "Total Realisasi PAGU": total_PAGU
        }])
        st.session_state.data_bantuan = pd.concat(
            [st.session_state.data_bantuan, new_data], ignore_index=True
        )
        st.success("✅ Data berhasil disimpan!")

# ------------------------------------
# HALAMAN LIHAT DATA
# ------------------------------------
elif menu == "Lihat Data":
    st.title("📂 Lihat Data Bantuan")
    if not st.session_state.data_bantuan.empty:
        st.dataframe(st.session_state.data_bantuan, use_container_width=True)
        csv = st.session_state.data_bantuan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "data_bantuan.csv", "text/csv")
    else:
        st.info("Belum ada data tersimpan.")

# ------------------------------------
# HALAMAN STATISTIK
# ------------------------------------
elif menu == "Statistik":
    st.title("📊 Statistik Data Bantuan")
    if not st.session_state.data_bantuan.empty:
        total = len(st.session_state.data_bantuan)
        total_jumlah = st.session_state.data_bantuan["Jumlah Bantuan"].sum()
        total_PAGU = st.session_state.data_bantuan["Total Realisasi PAGU"].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Jumlah Data", total)
        col2.metric("Total Bantuan", f"Rp {total_jumlah:,.0f}")
        col3.metric("Total PAGU", f"Rp {total_PAGU:,.0f}")
        st.bar_chart(st.session_state.data_bantuan.groupby("Jenis Bantuan")["Jumlah Bantuan"].sum())
    else:
        st.info("Belum ada data untuk ditampilkan.")

# ------------------------------------
# HALAMAN TENTANG
# ------------------------------------
elif menu == "Tentang":
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini dibuat untuk mendukung **pengelolaan dan integrasi data program penanggulangan kemiskinan** di Kutai Barat.  
    Dikembangkan oleh **Bappeda Litbang Kutai Barat** menggunakan **Streamlit**.
    """)

