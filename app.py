import pandas as pd
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import base64
import os

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

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

# Konfigurasi halaman
# -------------------------
st.set_page_config(
    page_title="📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat",
    page_icon="📂",
    layout="wide"
)

# -------------------------
# Fungsi untuk background + overlay
# -------------------------
def add_bg_for_header(image_file):
    import base64
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    
    st.markdown(
        f"""
        <style>
        /* Container khusus header dengan background */
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

        /* Overlay semi-transparent di header */
        .header-bg::before {{
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.18);
            border-radius: 10px;
            z-index: 0;
        }}

        /* Semua teks tetap biru */
        .stApp, .stApp * {{
            color: #2E86C1 !important;
        }}

        /* Label form tebal + latar putih */
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


# panggil background + overlay
add_bg_for_header ("background2.png")

# -------------------------
# Header dengan Logo
# -------------------------
col1, col2, col3 = st.columns([1,6,1])

with col1:
    st.image("logo_kutai_barat.png", width=100)

with col2:
    st.markdown(
        """
        <h2 style='text-align: center; color: #FFFFFF;'>
        📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat
        </h2>
        <h4 style='text-align: center; color:F0F0F0;'>
        Bappeda Litbang Kutai Barat
        </h4>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.image("logo_cap_kt.png", width=100)
# -------------------------
# Deskripsi aplikasi
# -------------------------
st.markdown("Cek Aktivitas & Program Kemiskinan Terpadu untuk monitoring Penyaluran Bantuan secara **mudah & interaktif**.")

# -------------------------
# Menu navigasi
# -------------------------
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    ["Input Data", "Lihat Data", "Analisis"]
)

if menu == "Input Data":
    st.title("📝 Halaman Input Data")
elif menu == "Lihat Data":
    st.title("📂 Halaman Lihat Data")
elif menu == "Analisis":
    st.title("📈 Halaman Analisis Data")



# Inisialisasi session state
if "data_bantuan" not in st.session_state:
    st.session_state.data_bantuan = pd.DataFrame(columns=[
        "Program", "Kegiatan", "Sub Kegiatan","Kecamatan","Kampung",
        "Nama Individu", "NIK Individu",  
        "Nama Kelompok/UMKM", "Nama Pengurus & Anggota","Nomor Registrasi/No. Akta Notaris Kelompok",
        "Jenis Bantuan", "Rincian Bantuan", "Jumlah Bantuan", "Total Realisasi PAGU"
    ])

# -----------------------------
# MENU: INPUT DATA
# -----------------------------
if menu == "Input Data":
    st.header("✍️ Form Input Data Bantuan")

    # Data kecamatan → kampung (contoh)
    DATA_WILAYAH = {
        "Barong Tongkok": [
            "Asa",
            "Balok Asa",
            "Barong Tongkok",
            "Belempung Ulaq",
            "Engkuni Pasek", 
            "Belempung Ulaq",
            "Geleo Asa",
            "Geleo Baru", 
            "Belempung Ulaq",
            "Geleo Asa",
            "Geleo Baru", 
            "Gemuruh Asa",
            "Juaq Asa",
            "Juhan Asa",
            "Mencimai",
            "Muara Asa",
            "Ngenyan Asa",
            "Ombau Asa",
            "Ongko Asa",
            "Pepas Asa",
            "Rejo Basuki",
            "Sendawar",
            "Simpang Raya",
            "Sumber Sari",
        ],
        "Bentian Besar": [
            "Anan Jaya",
            "Dilang Puti",
            "Jelum Sibak",
            "Penarung",
            "Randa Empas",
            "Sambung",
            "Suakong",
            "Tende",
            "Tukoq",
        ],
        "Bongan": [
            "Bukit Harapan",
            "Deraya",
            "Gerungung",
            "Jambuk",
            "Jambuk Makmur",
            "Lemper", 
            "Muara Gusik",
            "Muara Kedang",
            "Muara Siram", 
            "Penawai",
            "Pereng Taliq",
            "Resak", 
            "Siram Jaya",
            "Siram Makmur",
            "Tanjung Sari",
            "Tanjung Soke",
        ],
        "Damai": [
            "Benung",
            "Bermai",
            "Besiq",
            "Damai Kota",
            "Damai Seberang", 
            "Jengan Danum",
            "Keay",
            "Kelian", 
            "Lumpat Dahuq",
            "Mantar",
            "Mendika", 
            "Muara Bomboy",
            "Muara Niliq",
            "Muara Nyahing",
            "Muara Tokong",
            "Sempatn",
            "Tapulang",
        ],
        "Jempang": [
            "Tanjung Isuy",
            "Tanjung Jan",
            "Tanjung Jone",
            "Bekokong Makmur",
            "Lembonah",
            "Mancong",
            "Muara Nayan",
            "Muara Ohong", 
            "Muara Tae",
            "Pentat",
            "Perigiq", 
            "Pulau Lanting",
        ],
        "Muara Lawa": [
            "Benggeris",
            "Cempedes",
            "Dingin",
            "Lambing",
            "Lotaq", 
            "Muara Begai",
            "Muara Lawa",
            "Payang", 
        ],
        "Penyinggahan": [
            "Loa Deras",
            "Minta",
            "Tanjung Haur",
            "Penyinggahan Ilir",
            "Penyinggahan Ulu",
            "Bakung"
        ],
        "Muara Pahu": [
            "Dasaq",
            "Gunung Bayan",
            "Jerang Dayak",
            "Jerang Melayu",
            "Mendung", 
            "Muara Baroh",
            "Muara Beloan",
            "Sebelang", 
            "Tanjung Laong",
            "Tanjung Pagar",
            "Teluk Tempudau", 
            "Tepain Ulaq",
        ],
        "Melak": [
            "Empas",
            "Empakuq",
            "Muara Bunyut",
            "Melak Ilir",
            "Melak Ulu",
            "Muara Benangaq"
        ],
        "Mook Manaar Bulatn": [
            "Abit",
            "Gadur",
            "Gemuruh",
            "Gunung Rampah",
            "Jengan", 
            "Karangan",
            "Kelumpang", 
            "Linggang Marimun",
            "Linggang Muara Batuq",
            "Merayaq", 
            "Muara Jawaq",
            "Muara Kalaq",
            "Rembayan",
            "Sakaq Lotoq",
            "Sakaq Tada",
            "Tondoh",
        ],
        "Nyuatan": [
            "Awai",
            "Dempar",
            "Intu Lingau",
            "Jontai",
            "Lakan Bilem", 
            "Mu'ut",
            "Sembuan",
            "Sentalar", 
            "Temula",
            "Terajuk",
        ],
        "Linggang Bigung": [
            "Linggang Amer",
            "Linggang Bangunsari",
            "Linggang Bigung",
            "Linggang Bigung Baru",
            "Linggang Kebut", 
            "Linggang Mapan",
            "Linggang Melapeh",
            "Linggang Melapeh Baru", 
            "Linggang Mencelew",
            "Linggang Purwodadi",
            "Linggang Tutung",
        ],
        "Long Iram": [
            "Anah",
            "Kelian Luar",
            "Keliwai",
            "Linggang Muara Leban",
            "Long Daliq", 
            "Long Iram Bayan",
            "Long Iram Ilir",
            "Long Iram Kota", 
            "Long Iram Seberang",
            "Sukomulyo",
            "Ujoh Halang",        
        ],
        "Sekolaq Darat": [
            "Leleng",
            "Sekolaq Darat",
            "Sekolaq Joleq",
            "Sekolaq Muliaq",
            "Sekolaq Oday", 
            "Sumber Bangun",
            "Srimulyo",
            "Sumber Rejo", 
        ],
        "Tering": [
            "Kelian Dalam",
            "Linggang Banjarejo",
            "Linggang Jelemuq",
            "Linggang Kelubaq",
            "Linggang Muara Mujan", 
            "Linggang Muyub Ilir",
            "Linggang Purworejo",
            "Linggang Tering Seberang", 
            "Muyub Aket",
            "Muyub Ulu",
            "Tering Baru",
            "Tering Lama",
            "Tering Lama Ulu",
            "Tukul", 
        ],
        "Siluq Ngurai": [
            "Bentas",
            "Betung",
            "Kaliq",
            "Kendisiq",
            "Kenyanyan", 
            "Kiaq",
            "Lendian Liang Nayuq",
            "Muara Ponaq", 
            "Muhur",
            "Penawang",
            "Rikong",
            "Sang-Sang",
            "Tanah Mea",
            "Tebisaq", 
            "Tendiq",
        ]
    }

    col1, col2 = st.columns(2)

    with col1:
        program = st.text_input("Program")
        kegiatan = st.text_input("Kegiatan")
        sub_kegiatan = st.text_input("Sub Kegiatan")
        nama_individu = st.text_input("Nama (Individu)")
        nik_individu = st.text_input("NIK (Individu)")

        # dropdown kecamatan & kampung
        kecamatan = st.selectbox("Pilih Kecamatan", list(DATA_WILAYAH.keys()))
        kampung = st.selectbox("Pilih Kampung", DATA_WILAYAH[kecamatan])

    with col2:
        nama_kelompok = st.text_input("Nama Kelompok / UMKM")
        pengurus_anggota = st.text_area("Nama Pengurus & Anggota Kelompok")
        nik_kelompok = st.text_input("Nomor Registrasi/No. Akta Notaris Kelompok")
        jenis_bantuan = st.selectbox("Jenis Bantuan", ["Modal Usaha", "Alat Produksi", "Pelatihan", "Beasiswa", "Bantuan Tunai", "Bantuan Rumah Layak Huni", "Lainnya"])
        rincian_bantuan = st.text_area("Rincian Bantuan")

    jumlah_bantuan = st.number_input("Jumlah Bantuan (Rp)", min_value=0, step=1000)
    total_PAGU = st.number_input("Total Penyerapan PAGU (Rp)", min_value=0, step=1000)

    if st.button("💾 Simpan Data"):
        new_data = pd.DataFrame([{
            "Program": program,
            "Kegiatan": kegiatan,
            "Sub Kegiatan": sub_kegiatan,
            "Nama Individu": nama_individu,
            "NIK Individu": nik_individu,
            "Kecamatan": kecamatan,
            "Kampung": kampung,
            "Nama Kelompok/UMKM": nama_kelompok,
            "Nama Pengurus & Anggota": pengurus_anggota,
            "Nomor Registrasi/No. Akta Notaris Kelompok": nik_kelompok,
            "Jenis Bantuan": jenis_bantuan,
            "Rincian Bantuan": rincian_bantuan,
            "Jumlah Bantuan": jumlah_bantuan,
            "Total PAGU": total_PAGU
        }])
        st.session_state.data_bantuan = pd.concat(
            [st.session_state.data_bantuan, new_data], ignore_index=True
        )
        st.success("✅ Data berhasil disimpan!")


# -----------------------------
# MENU: LIHAT DATA
# -----------------------------
elif menu == "Lihat Data":
    st.header("📑 Data Bantuan Tersimpan")
    st.dataframe(st.session_state.data_bantuan, use_container_width=True)

    # Tombol download
    if not st.session_state.data_bantuan.empty:
        csv = st.session_state.data_bantuan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Data (CSV)", csv, "data_bantuan.csv", "text/csv")
    else:
        st.info("Belum ada data yang tersimpan.")

# -----------------------------
# MENU: STATISTIK
# -----------------------------
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

        # Grafik berdasarkan Jenis Bantuan
        st.subheader("📌 Grafik Jumlah Bantuan per Jenis Bantuan")
        chart_data = st.session_state.data_bantuan.groupby("Jenis Bantuan")["Jumlah Bantuan"].sum()
        st.bar_chart(chart_data)

    else:
        st.info("Belum ada data untuk ditampilkan.")

# -----------------------------
# MENU: TENTANG
# -----------------------------
elif menu == "Tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini dibuat menggunakan **Streamlit** untuk mendukung pengelolaan data bantuan.  
    **Fitur utama**:
    - Input data bantuan lengkap 📋  
    - Tabel data dinamis 📑  
    - Statistik & grafik interaktif 📊  
    - Export data ke CSV ⬇️  
    """)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="📂 Aplikasi Berbagi Data", layout="wide")
st.title("📂 Form Berbagi Data")
# Inisialisasi session state untuk menyimpan data upload
if "data_upload" not in st.session_state:
    st.session_state["data_upload"] = []
# ----------------------------
# FORM UPLOAD DATA
# ----------------------------
with st.form("form_metadata"):
    nama_data = st.text_input("Nama Data *")
    sub_kegiatan_opd = st.text_input("Sub Kegiatan OPD *")
    unit_pengelola = st.text_input("Unit Pengelola Data (Produsen Data) *")
    sumber_data = st.text_input("Sumber Data *")
    deskripsi = st.text_area("Deskripsi Data *")
    tujuan = st.text_area("Tujuan Pengumpulan Data *")
    wilayah = st.text_input("Ruang Lingkup / Wilayah *")
    waktu = st.text_input("Waktu Pengumpulan / Update *")
    metode = st.text_input("Metode Pengumpulan *")
    kualitas = st.text_area("Kualitas dan Validasi Data *")
    indikator = st.text_input("Indikator Terkait *")
    pemanfaatan = st.text_area("Pemanfaatan Data *")
    rencana_bagi = st.text_area("Rencana Bagi Pakai Data *")
    format_data = st.selectbox("Format Data *", ["", "CSV", "Excel", "PDF", "Word", "Lainnya"])
    pic = st.text_input("PIC Metadata *")

    submit = st.form_submit_button("💾 Simpan Metadata")

if submit:
    # Kumpulkan semua input ke list
    data_fields = [
        nama_data, sub_kegiatan_opd, unit_pengelola, sumber_data, deskripsi, tujuan,
        wilayah, waktu, metode, kualitas, indikator, pemanfaatan, rencana_bagi,
        format_data, pic
    ]

    # Cek apakah ada kolom yang kosong
    if any(str(field).strip() == "" for field in data_fields):
        st.error("⚠️ Mohon lengkapi semua kolom bertanda * sebelum menyimpan data.")
else:
    # Tambahkan data ke DataFrame
    UNIT_KERJA = [
        "Badan Perencanaan Pembangunan Penelitian & Pengembangan Daerah",
        "Badan Pendapatan Daerah",
        "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia",
        "Badan Keuangan dan Aset Daerah",
        "Badan Kesatuan Bangsa dan Politik",
        "Badan Penanggulangan Bencana Daerah",
        "Inspektorat Daerah",
        "Dinas Pendidikan dan Kebudayaan",
        "Dinas Kesehatan",
        "Dinas Pekerjaan Umum dan Penataan Ruang",
        "Dinas Perumahan, Kawasan Pemukiman dan Pertanahan",
        "Satuan Polisi Pamong Praja",
        "Dinas Sosial",
        "Dinas Pengendalian Penduduk, Keluarga Berencana, Pemberdayaan Perempuan dan Perlindungan Anak",
        "Dinas Tenaga Kerja dan Transmigrasi",
        "Dinas Kependudukan dan Pencatatan Sipil",
        "Dinas Pemberdayaan Masyarakat dan Kampung",
        "Dinas Perhubungan",
        "Dinas Komunikasi dan Informatika",
        "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
        "Dinas Pemuda dan Olahraga",
        "Dinas Arsip dan Perpustakaan",
        "Dinas Ketahanan Pangan",
        "Dinas Lingkungan Hidup",
        "Dinas Perdagangan, Koperasi, Usaha Kecil dan Menengah",
        "Dinas Pariwisata",
        "Dinas Pertanian",
        "Dinas Perikanan",
        "UPT Revitalisasi Perkebunan",
        "UPT Agrobisnis Pertanian",
        "UPTD Balai Benih Ikan Mentiwan",
        "Bongan",
        "Jempang",
        "Penyinggahan",
        "Muara Pahu",
        "Damai",
        "Melak",
        "Barong Tongkok",
        "Sekolaq Darat",
        "Mook Manaar Bulatn",
        "Tering",
        "Nyuatan",
        "Bentian Besar",
        "Linggang Bigung",
        "Siluq Ngurai",
        "Long Iram",
        "Muara Lawa"
    ]

    unit_kerja = st.selectbox("Unit Kerja Pengupload", UNIT_KERJA)


with st.form("upload_form"):
    gambaran_umum = st.text_area("Gambaran Umum Data")

    uploaded_file = st.file_uploader("Pilih File untuk Diupload", type=["csv", "xlsx", "pdf", "docx"])

    submitted = with st.form("nama_form") st.form_submit_button("📤 Upload Data")

    if submitted:
        if uploaded_file is not None:
            # Simpan ke session state
            st.session_state["data_upload"].append({
                "Nama Data": nama_data,
                "Format Data": format_data,
                "Unit Kerja Pengupload": unit_kerja,
                "Gambaran Umum": gambaran_umum,
                "Nama File Asli": uploaded_file.name
            })
            st.success(f"✅ File '{nama_file}' berhasil diupload oleh {unit_kerja}.")
        else:
            st.error("⚠️ Harap unggah file sebelum submit.")

# ----------------------------
# TABEL DATA UPLOAD
# ----------------------------
st.subheader("📑 Daftar Data yang Sudah Diupload")

if len(st.session_state["data_upload"]) > 0:
    df = pd.DataFrame(st.session_state["data_upload"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Belum ada data yang diupload.")

import streamlit as st

st.set_page_config(
    page_title="📊 CAP-KT (Cek Aktivitas & Program Kemiskinan Terpadu) Kutai Barat",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nama file background (letakkan di folder project)
sidebar_bg = "sidebar_bg.jpg"  

# CSS background + overlay
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(
            rgba(0, 0, 0, 0.6),   /* overlay hitam transparan */
            rgba(0, 0, 0, 0.6)
        ), url("file:///{sidebar_bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }}

    [data-testid="stSidebar"] * {{
        color: white !important;  /* teks putih agar kontras */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar Menu Navigasi
# -----------------------------
st.sidebar.title("🔎 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:", 
    ["Beranda", "Input Data", "Statistik", "Tentang Aplikasi"]
)

# -----------------------------
# Konten sesuai pilihan
# -----------------------------
if menu == "Beranda":
    st.title("🏠 Beranda")
    st.info("Ini adalah halaman utama aplikasi.")

elif menu == "Input Data":
    st.title("✍️ Input Data")
    st.write("Form untuk menambahkan data.")

elif menu == "Statistik":
    st.title("📊 Statistik")
    st.write("Grafik & analisis data akan muncul di sini.")

elif menu == "Tentang Aplikasi":
    st.title("ℹ️ Tentang")
    st.write("Aplikasi Bank Data Kemiskinan Kutai Barat - Bappeda Litbang.")






























