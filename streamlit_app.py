import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Keuangan Real-Time", layout="wide")

# --- JUDUL APLIKASI ---
st.title("💰 Aplikasi Keuangan & Investasi (Google Sheets)")

# --- KONEKSI KE GOOGLE SHEETS ---
# Membuka koneksi menggunakan credential yang ada di Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNGSI LOAD & SAVE DATA ---
def load_data():
    try:
        # Membaca data dari Google Sheets (Sheet1)
        # ttl=0 agar data tidak di-cache (selalu fresh saat di-reload)
        df = conn.read(worksheet="Sheet1", ttl=0)
        
        # Jika sheet masih kosong, kembalikan dataframe dengan struktur kolom
        if df.empty:
             return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])
        
        # Pastikan kolom Tanggal dibaca sebagai datetime
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df
        
    except Exception as e:
        # Jika terjadi error (misal sheet baru dibuat), buat struktur awal
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])

def save_data(df):
    # Mengupdate data ke Google Sheets
    # Pastikan format tanggal diubah menjadi string agar kompatibel dengan JSON/Sheets
    df_save = df.copy()
    df_save['Tanggal'] = df_save['Tanggal'].astype(str) 
    conn.update(worksheet="Sheet1", data=df_save)

# Load data saat aplikasi dibuka
df = load_data()

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("📝 Input Transaksi Baru")

with st.sidebar.form("form_transaksi", clear_on_submit=True):
    # BAGIAN INI YANG TADI ERROR (SEKARANG SUDAH MENJOROK KE DALAM)
    tgl = st.date_input("Tanggal", datetime.now())
    
    # Kategori sesuai permintaan
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    
    kategori_opsi = []
    if jenis == "Pemasukan":
        kategori_opsi = ["Gaji", "Dividen", "Bonus", "Lainnya"]
    else:
        kategori_opsi = ["Operasional Bulanan", "Investasi", "Kebutuhan Pokok", "Hiburan", "Lainnya"]
        
    kategori = st.selectbox("Kategori Detail", kategori_opsi)
    jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
    ket = st.text_input("Keterangan Tambahan")
    
    submit = st.form_submit_button("Simpan Data")

    if submit:
        # Membuat data baru
        new_data = pd.DataFrame([{
            "Tanggal": pd.to_datetime(tgl),
            "Kategori": kategori,
            "Jenis": jenis,
            "Jumlah": jumlah,
            "Keterangan": ket,
            "Bulan": tgl.strftime("%B"),
            "Tahun": tgl.year
        }])
        
        # Menggabungkan data lama dengan data baru
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        # Simpan ke Google Sheets
        with st.spinner('Menyimpan ke Google Sheets...'):
            save_data(updated_df)
            
        st.success("Data berhasil disimpan ke Cloud!")
        st.rerun() # Refresh halaman untuk menarik data terbaru

# --- DASHBOARD UTAMA ---

# Jika data kosong, stop eksekusi di sini
if df.empty:
    st.info("Belum ada data di Google Sheets. Silakan input data di sidebar.")
    st.stop()

# 1. Filter Data (Tahun)
tahun_list = df['Tahun'].unique().tolist()
if tahun_list:
    pilih_tahun = st.selectbox("Pilih Tahun Laporan", sorted(tahun_list, reverse=True))
    df_filtered = df[df['Tahun'] == pilih_tahun]
else:
    df_filtered = df # Fallback jika tahun belum terdeteksi

# --- REKAP & METRIK ---
col1, col2, col3, col4 = st.columns(4)

total_masuk = df_filtered[df_filtered['Jenis'] == 'Pemasukan']['Jumlah'].sum()
total_keluar = df_filtered[df_filtered['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
total_invest = df_filtered[df_filtered['Kategori'] == 'Investasi']['Jumlah'].sum()
saldo = total_masuk - total_keluar

col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
col3.metric("Total Investasi", f"Rp {total_invest:,.0f}")
col4.metric("Sisa Saldo", f"Rp {saldo:,.0f}")

st.markdown("---")

# --- GRAFIK (VISUALISASI) ---
col_grafik1, col_grafik2 = st.columns(2)

# Order bulan
order_bulan = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Grouping data per bulan
df_bulan = df_filtered.groupby(['Bulan', 'Jenis'])['Jumlah'].sum().reset_index()

with col_grafik1:
    st.subheader("Grafik Arus Kas Bulanan")
    if not df_bulan.empty:
        fig_bar = px.bar(df_bulan, x='Bulan', y='Jumlah', color='Jenis', 
                         barmode='group', category_orders={"Bulan": order_bulan},
                         color_discrete_map={"Pemasukan": "green", "Pengeluaran": "red"})
        st.plotly_chart(fig_bar, use_container_width=True)

# Grafik 2: Komposisi Pengeluaran
df_expense = df_filtered[df_filtered['Jenis'] == 'Pengeluaran']
with col_grafik2:
    st.subheader("Proporsi Pengeluaran & Investasi")
    if not df_expense.empty:
        fig_pie = px.pie(df_expense, values='Jumlah', names='Kategori', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TABEL DETAIL ---
st.subheader("📄 Laporan Detail Transaksi")
# Format tanggal agar enak dilihat di tabel
df_display = df_filtered.copy()
df_display['Tanggal'] = df_display['Tanggal'].dt.strftime('%Y-%m-%d')
st.dataframe(df_display.sort_values(by="Tanggal", ascending=False), use_container_width=True)

# --- LAPORAN TAHUNAN (SUMMARY) ---
st.markdown("---")
st.subheader(f"Laporan Rekapitulasi Tahun {pilih_tahun}")
summary_table = df_filtered.groupby(['Bulan', 'Jenis'])['Jumlah'].sum().unstack().fillna(0)
summary_table = summary_table.reindex(order_bulan).dropna(how='all')
st.table(summary_table.style.format("Rp {:,.0f}"))
