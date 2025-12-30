import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="APPV3 Executive", 
    page_icon="💎", 
    layout="centered"
) 

# --- 2. PREMIUM UI/CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    header, footer {visibility: hidden;}
    
    /* Glassmorphism Container */
    [data-testid="stAppViewContainer"] > .main {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        margin: 10px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    }

    /* Professional Cards */
    .card {
        padding: 20px;
        border-radius: 18px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .bg-cash { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    .bg-invest { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); }
    
    .card-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.8; }
    .card-value { font-size: 26px; font-weight: 800; margin-top: 5px; }
    
    .section-title { font-size: 18px; font-weight: 800; color: #1e3c72; margin-top: 25px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if df is None or df.empty:
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

# --- 4. FINANCIAL LOGIC ---
# Saldo Awal Anda
START_CASH = 451020.90
START_INVEST = 4341114.0
TARGET_BUDGET = 1505000.0

if not df.empty:
    total_masuk = float(df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum())
    total_keluar = float(df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum())
    penambahan_invest = float(df[df['Kategori'] == 'Investasi']['Jumlah'].sum())
    
    # Budget Tracking Bulan Berjalan
    now = datetime.now()
    exp_this_month = float(df[(df['Jenis'] == 'Pengeluaran') & (df['Bulan'] == now.strftime("%B")) & (df['Tahun'] == now.year)]['Jumlah'].sum())
else:
    total_masuk = 0.0; total_keluar = 0.0; penambahan_invest = 0.0; exp_this_month = 0.0

saldo_cash = START_CASH + total_masuk - total_keluar
saldo_invest = START_INVEST + penambahan_invest

# --- 5. UI DISPLAY ---
st.markdown("<h2 style='text-align: center; color: #1e3c72;'>💎 APPV3 EXECUTIVE</h2>", unsafe_allow_html=True)

# Main Wallets
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<div class="card bg-cash"><div class="card-label">Cash Flow</div><div class="card-value">Rp {saldo_cash:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="card bg-invest"><div class="card-label">Investment</div><div class="card-value">Rp {saldo_invest:,.0f}</div></div>', unsafe_allow_html=True)

# Budgeting Tracker
st.markdown("<div class='section-title'>Monthly Budget Limit</div>", unsafe_allow_html=True)
progress = min(exp_this_month / TARGET_BUDGET, 1.0) if TARGET_BUDGET > 0 else 0
st.markdown(f"**Pengeluaran:** Rp {exp_this_month:,.0f} / Rp {TARGET_BUDGET:,.0f}")
st.progress(progress)

if progress >= 1.0: st.error("🚨 Limit Rp 1.505.000 Terlampaui!")
elif progress >= 0.8: st.warning("⚠️ Waspada! Budget hampir habis.")

# Asset Growth Chart
st.markdown("<div class='section-title'>Asset Performance</div>", unsafe_allow_html=True)
if not df.empty:
    chart_data = df.groupby(df['Tanggal'].dt.date)['Jumlah'].sum().reset_index()
    fig = go.Figure(data=go.Scatter(x=chart_data['Tanggal'], y=chart_data['Jumlah'], fill='tozeroy', line_color='#1e3c72'))
    fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# Quick Actions
with st.expander("📝 CATAT TRANSAKSI", expanded=False):
    with st.form("exec_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_tgl = st.date_input("Tanggal", datetime.now())
            t_tipe = st.selectbox("Tipe", ["Pengeluaran", "Pemasukan"])
        with c2:
            t_amt = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            t_kat = st.selectbox("Kategori", ["Gaji", "Dividen", "Bonus", "Lainnya"]) if t_tipe == "Pemasukan" else st.selectbox("Kategori", ["Makan", "Transport", "Tagihan", "Investasi", "Belanja", "Lainnya"])
        
        t_ket = st.text_input("Catatan")
        if st.form_submit_button("KONFIRMASI", use_container_width=True):
            if t_amt > 0:
                new_row = pd.DataFrame([{"Tanggal": pd.to_datetime(t_tgl), "Kategori": t_kat, "Jenis": t_tipe, "Jumlah": t_amt, "Keterangan": t_ket, "Bulan": t_tgl.strftime("%B"), "Tahun": t_tgl.year}])
                save_data(pd.concat([df, new_row], ignore_index=True))
                st.rerun()

# History Table
st.markdown("<div class='section-title'>Transaction History</div>", unsafe_allow_html=True)
st.dataframe(df.sort_values("Tanggal", ascending=False)[['Tanggal','Kategori','Jumlah','Jenis']], use_container_width=True, hide_index=True)
