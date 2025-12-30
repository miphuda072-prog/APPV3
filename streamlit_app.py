import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
# Menggunakan 'page_icon' agar saat dijadikan launcher muncul ikon Bank
st.set_page_config(
    page_title="APPV3 Keuangan", 
    page_icon="🏦", 
    layout="centered"
) 

# --- 2. CSS CUSTOM (GAYA M-BANKING MODERN) ---
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f5;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    header, footer {visibility: hidden;}

    /* KARTU CASH FLOW (BIRU) */
    .card-cash {
        background: linear-gradient(135deg, #0061ff 0%, #60efff 100%);
        border-radius: 15px;
        color: white;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 97, 255, 0.3);
        margin-bottom: 15px;
        position: relative;
    }

    /* KARTU INVESTASI (UNGU/EMAS) */
    .card-invest {
        background: linear-gradient(135deg, #6610f2 0%, #d63384 100%);
        border-radius: 15px;
        color: white;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(102, 16, 242, 0.3);
        margin-bottom: 15px;
        position: relative;
    }

    .card-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
        margin-bottom: 5px;
    }
    .card-value {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .card-footer {
        font-size: 10px;
        opacity: 0.8;
        display: flex;
        justify-content: space-between;
    }

    /* RINGKASAN MINI */
    .summary-row {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    .mini-box {
        flex: 1;
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .mini-label { font-size: 10px; color: #888; }
    .mini-val-in { color: #28a745; font-weight: bold; font-size: 13px; }
    .mini-val-out { color: #dc3545; font-weight: bold; font-size: 13px; }

    /* JUDUL SECTION */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #333;
        margin-top: 20px;
        margin-bottom: 10px;
        border-left: 4px solid #0061ff;
        padding-left: 10px;
    }
    
    .stButton button { width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD DATA DARI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty: 
            return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df
    except: 
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])

def save_data(df):
    df_s = df.copy()
    df_s['Tanggal'] = df_s['Tanggal'].astype(str)
    conn.update(worksheet="Sheet1", data=df_s)

df = load_data()

# --- 4. LOGIKA PEMISAHAN SALDO & FORMAT RUPIAH ---
# Setting Saldo Awal sesuai permintaan user
start_cash = 451020.90
start_invest = 4341114.0

if not df.empty:
    # Hitung total masuk & keluar dari database
    total_masuk = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    total_keluar = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
    
    # Hitung dana yang dipindah ke Investasi (Kategori 'Investasi' di Pengeluaran)
    penambahan_invest = df[df['Kategori'] == 'Investasi']['Jumlah'].sum()
else:
    total_masuk = 0; total_keluar = 0; penambahan_invest = 0

# Rumus perhitungan saldo real-time
saldo_cash_akhir = start_cash + total_masuk - total_keluar
saldo_invest_akhir
