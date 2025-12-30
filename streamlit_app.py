import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="APPV3 Keuangan", layout="wide")

# --- CSS KUSTOM UNTUK MENIRU TAMPILAN REFERENSI ---
st.markdown("""
<style>
    /* Mengatur font dan background dasar agar lebih bersih */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Styling untuk Judul Utama */
    .main-title {
        text-align: center;
        font-weight: 700;
        color: #333;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* Styling Custom Metric Box */
    .metric-container {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
    }
    .metric-box {
        flex: 1;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        overflow: hidden;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-header {
        padding: 10px;
        font-weight: 600;
        color: white;
    }
    .metric-value {
        padding: 20px;
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    /* Warna Header Metric */
    .bg-success { background-color: #28a745; } /* Hijau Pemasukan */
    .bg-danger { background-color: #dc3545; }  /* Merah Pengeluaran */
    .bg-primary { background-color: #0d6efd; } /* Biru Saldo */

    /* Styling Header Form Biru */
    .form-header {
        background-color: #0d6efd;
        color: white;
        padding: 15px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    /* Styling Container Form agar menyatu dengan header */
    [data-testid="stForm"] {
        border-radius: 0 0 8px 8px;
        border: 1px solid #e0e0e0;
        border-top: none;
        padding: 20px;
        background-color: white;
    }
    
    /* Styling Header Tabel Riwayat */
    .table-header {
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 20px;
        font-weight: 600;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# --- JUDUL APLIKASI (DI TENGAN) ---
st.markdown("<h1 class='main-title'>APPV3</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Mengelola keuangan Anda lebih baik.</p>", unsafe_allow_html=True)


# --- KONEKSI KE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI LOAD & SAVE DATA ---
def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty:
             return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])

def save_data(df):
    df_save = df.copy()
    df_save['Tanggal'] = df_save['Tanggal'].astype(str) 
    conn.update(worksheet="Sheet1", data=df_save)

# Load data saat aplikasi dibuka
df = load_data()

# --- PERHITUNGAN METRIK ---
saldo_awal = 4341114 
if not df.empty:
    total_masuk = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    total_keluar = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
else:
    total_masuk = 0
    total_keluar = 0

saldo_akhir = saldo_awal + total_masuk - total_keluar

# --- TAMPILAN METRIK (CUSTOM HTML) ---
st.markdown(f"""
<div class="metric-container">
    <div class="metric-box">
        <div class="metric-header bg-success">Total Pemasukan</div>
        <div class="metric-value" style="color: #28a745;">Rp {total_masuk:,.0f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-header bg-danger">Total Pengeluaran</div>
        <div class="metric-value" style="color: #dc3545;">Rp {total_keluar:,.0f}</div>
    </div>
    <div class="metric-box">
        <div class="metric-header bg-primary">Saldo Akhir</div>
        <div class="metric-value" style="color: #0d6efd;">Rp {saldo_akhir:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- FORM INPUT TRANSAKSI (HORIZONTAL DI HALAMAN UTAMA) ---
# Header Biru
st.markdown('<div class="form-header">Input Transaksi Baru</div>', unsafe_allow_html=True)

# Form Container
with st.form("form_transaksi", clear_on_submit=True):
    # Baris 1: Tanggal, Tipe, Kategori (Horizontal)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        tgl = st.date_input("Tanggal", datetime.now())
    with col_f2:
        jenis = st.selectbox("Tipe", ["Pengeluaran", "Pemasukan"])
    with col_f3:
        # LOGIKA KATEGORI (SUDAH DITAMBAHKAN GAJI)
        if jenis == "Pemasukan":
            # Gaji ada di sini sebagai pemasukan
            kategori_opsi = ["Gaji", "Tunjangan", "Dividen", "Bonus", "Lainnya"]
        else:
            # Gaji Karyawan juga ditambahkan di pengeluaran jika perlu membayar orang
            kategori_opsi = [
                "Kebutuhan Pokok", 
                "Transportasi", 
                "Makan & Minum",
                "Gaji Karyawan/ART", 
                "Kendaraan", 
                "Tagihan", 
                "Hiburan", 
                "Investasi", 
                "Lainnya"
            ]
        kategori = st.selectbox("Kategori", kategori_opsi)
    
    # Baris 2: Nominal dan Catatan (Horizontal)
    col_f4, col_f5 = st.columns([1, 2]) # Kolom catatan lebih lebar
    with col_f4:
        jumlah = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
    with col_f5:
        ket = st.text_input("Catatan (Opsional)", placeholder="Contoh: Bensin, Service motor...")
    
    # Tombol Submit Lebar Penuh
    submit = st.form_submit_button("Simpan Transaksi", use_container_width=True, type="primary")

    if submit:
        if jumlah > 0:
            new_data = pd.DataFrame([{
                "Tanggal": pd.to_datetime(tgl),
                "Kategori": kategori,
                "Jenis": jenis,
                "Jumlah": jumlah,
                "Keterangan": ket,
                "Bulan": tgl.strftime("%B"),
                "Tahun": tgl.year
            }])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            with st.spinner('Menyimpan ke Google Sheets...'):
                save_data(updated_df)
            st.success("Data berhasil disimpan!")
            st.rerun()
        else:
            st.error("Nominal harus lebih dari 0.")

# --- RIWAYAT TRANSAKSI (TABEL STYLED) ---
st.markdown('<div class="table-header">🕒 Riwayat Transaksi</div>', unsafe_allow_html=True)

if df.empty:
    st.info("Belum ada data transaksi.")
else:
    # 1. Filter Sederhana
    col_filter1, col_filter2 = st.columns([1,3])
    with col_filter1:
        st.selectbox("Filter Waktu", ["Semua Waktu", "Bulan Ini"], disabled=True)
        
    # 2. Persiapan Data untuk Tabel
    df_display = df.copy()
    df_display = df_display.sort_values(by="Tanggal", ascending=False)
    
    # Format Tanggal
    df_display['Tanggal'] = df_display['Tanggal'].dt.strftime('%d-%m-%Y')
    
    # Format Jumlah jadi Rupiah
    df_display['Nominal'] = df_display['Jumlah'].apply(lambda x: f"Rp {x:,.0f}")

    # Pilih Kolom
    df_final = df_display[['Tanggal', 'Jenis', 'Kategori', 'Nominal', 'Keterangan']]
    df_final = df_final.rename(columns={'Jenis': 'Tipe', 'Keterangan': 'Catatan'})

    # 3. Styling Tabel
    def style_tipe(val):
        color = 'white'
        bg_color = '#dc3545' # Merah default
        if val == 'Pemasukan':
            bg_color = '#28a745' # Hijau
        
        return f'background-color: {bg_color}; color: {color}; border-radius: 12px; padding: 4px 10px; font-weight: bold; text-align: center; display: inline-block;'

    # Terapkan styling
    styled_df = df_final.style.map(style_tipe, subset=['Tipe'])

    # Tampilkan tabel
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tipe": st.column_config.TextColumn(width="small"),
            "Nominal": st.column_config.TextColumn(width="medium"),
             "Catatan": st.column_config.TextColumn(width="large"),
        }
    )
