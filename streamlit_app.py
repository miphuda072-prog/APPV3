import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="APPV3 Premium Dashboard", 
    page_icon="📈", 
    layout="centered"
) 

# --- 2. STYLE CSS (GLASSMORPHISM & UI) ---
def set_professional_style():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom right, #e0eafc, #cfdef3); }
    header, footer {visibility: hidden;}
    [data-testid="stAppViewContainer"] > .main {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 10px 0;
        padding: 15px;
    }
    .card-cash {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px; color: white; padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
    }
    .card-invest {
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        border-radius: 15px; color: white; padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(106, 17, 203, 0.2);
    }
    .card-value { font-size: 22px; font-weight: 800; }
    .section-title { font-size: 18px; font-weight: 800; color: #1e3c72; margin-top: 25px; }
    .budget-text { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

set_professional_style()

# --- 3. KONEKSI DATA ---
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

# --- 4. LOGIKA PERHITUNGAN ---
start_cash = 451020.90
start_invest = 4341114.0
target_budget = 1505000.0  # <--- TARGET LIMIT ANDA SUDAH DISESUAIKAN

if not df.empty:
    total_masuk = float(df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum())
    total_keluar = float(df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum())
    penambahan_invest = float(df[df['Kategori'] == 'Investasi']['Jumlah'].sum())
    
    bln_ini = datetime.now().strftime("%B")
    thn_ini = datetime.now().year
    pengeluaran_bln_ini = float(df[(df['Jenis'] == 'Pengeluaran') & (df['Bulan'] == bln_ini) & (df['Tahun'] == thn_ini)]['Jumlah'].sum())
else:
    total_masuk = 0.0; total_keluar = 0.0; penambahan_invest = 0.0; pengeluaran_bln_ini = 0.0

saldo_cash_akhir = start_cash + total_masuk - total_keluar
saldo_invest_akhir = start_invest + penambahan_invest

# --- 5. UI: HEADER & SALDO ---
st.markdown("<h3 style='text-align: center; color: #1e3c72;'>📈 APPV3 DASHBOARD PREMIERE</h3>", unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)
with col_c1:
    st.markdown(f'<div class="card-cash"><div style="font-size:10px;">CASH BALANCE</div><div class="card-value">Rp {saldo_cash_akhir:,.0f}</div></div>', unsafe_allow_html=True)
with col_c2:
    st.markdown(f'<div class="card-invest"><div style="font-size:10px;">INVESTMENT ASSETS</div><div class="card-value">Rp {saldo_invest_akhir:,.0f}</div></div>', unsafe_allow_html=True)

# --- 6. FITUR BUDGETING (TARGET PENGELUARAN) ---
st.markdown("<div class='section-title'>Monthly Budget Tracker</div>", unsafe_allow_html=True)
persentase_budget = min(pengeluaran_bln_ini / target_budget, 1.0) if target_budget > 0 else 0

st.markdown(f"<div class='budget-text'>Pengeluaran {datetime.now().strftime('%B')}: Rp {pengeluaran_bln_ini:,.0f} / Rp {target_budget:,.0f}</div>", unsafe_allow_html=True)
st.progress(persentase_budget)

if persentase_budget >= 1.0:
    st.error(f"⚠️ Limit Rp {target_budget:,.0f} terlampaui!")
elif persentase_budget >= 0.8:
    st.warning("⚡ Mendekati limit budget Anda.")

# --- 7. GRAFIK PERKEMBANGAN ASET ---
st.markdown("<div class='section-title'>Asset Growth Analytics</div>", unsafe_allow_html=True)
if not df.empty:
    df_growth = df.groupby(['Tahun', 'Bulan']).Jumlah.sum().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_growth['Bulan'], y=df_growth['Jumlah'], mode='lines+markers', name='Arus Kas', line=dict(color='#1e3c72', width=3)))
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Data belum cukup untuk grafik.")

# --- 8. QUICK TRANSACTION ---
with st.expander("➕ TRANSAKSI BARU", expanded=False):
    with st.form("form_v5"):
        f1, f2 = st.columns(2)
        with f1:
            tgl = st.date_input("Tanggal", datetime.now())
            jenis = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
        with f2:
            amt = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            kat = st.selectbox("Kategori", ["Makan", "Transport", "Investasi", "Tagihan", "Lainnya"]) if jenis == "Pengeluaran" else st.selectbox("Kategori", ["Gaji", "Dividen", "Bonus", "Lainnya"])
        desc = st.text_input("Catatan")
        if st.form_submit_button("SIMPAN"):
            if amt > 0:
                new_row = pd.DataFrame([{"Tanggal": pd.to_datetime(tgl), "Kategori": kat, "Jenis": jenis, "Jumlah": amt, "Keterangan": desc, "Bulan": tgl.strftime("%B"), "Tahun": tgl.year}])
                save_data(pd.concat([df, new_row], ignore_index=True))
                st.rerun()

# --- 9. RECENT ACTIVITY ---
st.markdown("<div class='section-title'>Recent Activity</div>", unsafe_allow_html=True)
if not df.empty:
    st.dataframe(df.sort_values("Tanggal", ascending=False)[['Tanggal','Kategori','Jumlah','Jenis']], use_container_width=True, hide_index=True)
