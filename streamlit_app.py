import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="APPV3 Mobile Banking", layout="centered") 

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

# --- 3. LOAD DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df.empty: return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan"])
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df
    except: return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan"])

def save_data(df):
    df_s = df.copy()
    df_s['Tanggal'] = df_s['Tanggal'].astype(str)
    conn.update(worksheet="Sheet1", data=df_s)

df = load_data()

# --- 4. LOGIKA PEMISAHAN SALDO ---
# Setting Saldo Awal Sesuai Permintaan
start_cash = 451020.90
start_invest = 4341114

if not df.empty:
    # Hitung Arus Kas
    total_masuk = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    total_keluar = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
    
    # Hitung Penambahan Investasi (Dari kategori 'Investasi' di Pengeluaran)
    # Asumsinya: Jika kita input Pengeluaran -> Investasi, itu uang pindah dari Cash ke Invest
    penambahan_invest = df[df['Kategori'] == 'Investasi']['Jumlah'].sum()
else:
    total_masuk = 0; total_keluar = 0; penambahan_invest = 0

# Rumus Akhir
# 1. Saldo Cash Flow = Awal + Pemasukan - Semua Pengeluaran (termasuk yg dipakai beli investasi)
saldo_cash_akhir = start_cash + total_masuk - total_keluar

# 2. Saldo Investasi = Awal + Uang yang dialokasikan ke Investasi
saldo_invest_akhir = start_invest + penambahan_invest

# --- 5. TAMPILAN UI ---

# Header Profil
c1, c2 = st.columns([3,1])
with c1:
    st.markdown("##### Halo, Bos Keuangan")
    st.caption(f"Update: {datetime.now().strftime('%d %b %Y')}")
with c2:
    st.markdown("<div style='font-size:30px; text-align:right;'>👨‍💼</div>", unsafe_allow_html=True)

# DUA KARTU BERDAMPINGAN
col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown(f"""
    <div class="card-cash">
        <div class="card-label">💳 CASH FLOW</div>
        <div class="card-value">Rp {saldo_cash_akhir:,.0f}</div>
        <div class="card-footer">Liquid Funds</div>
    </div>
    """, unsafe_allow_html=True)

with col_card2:
    st.markdown(f"""
    <div class="card-invest">
        <div class="card-label">💎 ASET INVESTASI</div>
        <div class="card-value">Rp {saldo_invest_akhir:,.0f}</div>
        <div class="card-footer">Total Assets</div>
    </div>
    """, unsafe_allow_html=True)

# RINGKASAN ARUS KAS
st.markdown(f"""
<div class="summary-row">
    <div class="mini-box">
        <div class="mini-label">Pemasukan Bulan Ini</div>
        <div class="mini-val-in">+ Rp {total_masuk:,.0f}</div>
    </div>
    <div class="mini-box">
        <div class="mini-label">Pengeluaran Bulan Ini</div>
        <div class="mini-val-out">- Rp {total_keluar:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# FORM INPUT (EXPANDER)
with st.expander("➕ INPUT TRANSAKSI BARU", expanded=False):
    with st.form("main_form", clear_on_submit=True):
        st.info("💡 Tips: Pilih Kategori 'Investasi' untuk memindahkan uang dari Cash ke Aset.")
        
        c_in1, c_in2 = st.columns(2)
        with c_in1:
            tgl = st.date_input("Tanggal", datetime.now())
            jenis = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
        with c_in2:
            amt = st.number_input("Nominal (Rp)", min_value=0, step=5000)
            if jenis == "Pemasukan":
                kat = st.selectbox("Kategori", ["Gaji", "Bonus", "Dividen", "Lainnya"])
            else:
                kat = st.selectbox("Kategori", ["Makan", "Transport", "Tagihan", "Investasi", "Belanja", "Lainnya"])
        
        desc = st.text_input("Keterangan")
        btn = st.form_submit_button("SIMPAN TRANSAKSI", type="primary")
        
        if btn and amt > 0:
            new_df = pd.DataFrame([{
                "Tanggal": pd.to_datetime(tgl), "Kategori": kat, "Jenis": jenis,
                "Jumlah": amt, "Keterangan": desc, "Bulan": tgl.strftime("%B"), "Tahun": tgl.year
            }])
            save_data(pd.concat([df, new_df], ignore_index=True))
            st.toast("Data Tersimpan!", icon="✅")
            st.rerun()

# RIWAYAT
st.markdown('<div class="section-title">Riwayat Mutasi</div>', unsafe_allow_html=True)
if not df.empty:
    st.dataframe(
        df.sort_values("Tanggal", ascending=False)[['Tanggal','Kategori','Jumlah','Jenis']],
        use_container_width=True, hide_index=True,
        column_config={
            "Tanggal": st.column_config.DateColumn("Tgl", format="DD/MM"),
            "Jumlah": st.column_config.NumberColumn("Rp", format="%d"),
            "Jenis": st.column_config.TextColumn("Tipe", width="small")
        }
    )
else:
    st.info("Belum ada data transaksi.")
