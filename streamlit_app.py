import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN (MOBILE FRIENDLY) ---
st.set_page_config(page_title="APPV3 Mobile Banking", layout="centered") # Layout centered agar seperti HP

# --- 2. CSS CUSTOM (GAYA M-BANKING) ---
st.markdown("""
<style>
    /* Background App agar sedikit abu-abu lembut */
    .stApp {
        background-color: #f0f2f5;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* MENYEMBUNYIKAN HEADER BAWAAN STREAMLIT AGAR SEPERTI APP NATIVE */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* KARTU ATM (SALDO UTAMA) */
    .bank-card {
        background: linear-gradient(135deg, #0061ff 0%, #60efff 100%);
        border-radius: 20px;
        color: white;
        padding: 25px;
        box-shadow: 0 10px 20px rgba(0, 97, 255, 0.3);
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .bank-card h3 {
        color: rgba(255,255,255,0.8);
        font-size: 14px;
        font-weight: 400;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .bank-card h1 {
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin: 10px 0 20px 0;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chip {
        width: 40px;
        height: 30px;
        background: rgba(255,255,255,0.2);
        border-radius: 5px;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .card-brand {
        font-weight: bold;
        font-style: italic;
        font-size: 18px;
    }

    /* CONTAINER RINGKASAN (Income/Expense) */
    .summary-container {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    .summary-box {
        flex: 1;
        background: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .sum-label { font-size: 12px; color: #888; margin-bottom: 5px; }
    .sum-val-in { color: #28a745; font-weight: bold; font-size: 16px; }
    .sum-val-out { color: #dc3545; font-weight: bold; font-size: 16px; }

    /* SECTION HEADER */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #333;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* TOMBOL INPUT */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KONEKSI & LOAD DATA ---
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
    df_save = df.copy()
    df_save['Tanggal'] = df_save['Tanggal'].astype(str) 
    conn.update(worksheet="Sheet1", data=df_save)

df = load_data()

# --- 4. LOGIKA SALDO ---
saldo_awal = 4341114 
if not df.empty:
    total_masuk = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    total_keluar = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
else:
    total_masuk = 0
    total_keluar = 0
saldo_akhir = saldo_awal + total_masuk - total_keluar

# --- 5. UI: HEADER (SAPAAN) ---
col_head1, col_head2 = st.columns([3,1])
with col_head1:
    st.markdown("##### Selamat Datang,")
    st.markdown("## Bos Keuangan 👋")
with col_head2:
    # Placeholder foto profil (Icon)
    st.markdown("<div style='background:#ddd; width:50px; height:50px; border-radius:50%; text-align:center; line-height:50px;'>👤</div>", unsafe_allow_html=True)

# --- 6. UI: KARTU ATM (SALDO) ---
st.markdown(f"""
<div class="bank-card">
    <h3>TOTAL SALDO</h3>
    <h1>Rp {saldo_akhir:,.0f}</h1>
    <div class="card-footer">
        <div class="chip"></div>
        <div class="card-brand">APPV3 Platinum</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 7. UI: RINGKASAN MASUK/KELUAR ---
st.markdown(f"""
<div class="summary-container">
    <div class="summary-box">
        <div class="sum-label">Pemasukan (Total)</div>
        <div class="sum-val-in">▲ Rp {total_masuk:,.0f}</div>
    </div>
    <div class="summary-box">
        <div class="sum-label">Pengeluaran (Total)</div>
        <div class="sum-val-out">▼ Rp {total_keluar:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 8. UI: TOMBOL TRANSAKSI (COLLAPSIBLE) ---
# Menggunakan Expander agar menu tidak memenuhi layar (Khas Mobile App)
with st.expander("➕  TAMBAH TRANSAKSI BARU", expanded=False):
    with st.form("form_m_banking", clear_on_submit=True):
        st.caption("Input detail transaksi Anda di bawah ini")
        
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal", datetime.now())
            jenis = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
        with c2:
            jumlah = st.number_input("Nominal (Rp)", min_value=0, step=1000)
            
            # Kategori Dinamis
            if jenis == "Pemasukan":
                opsi = ["Gaji", "Tunjangan", "Bonus", "Investasi", "Lainnya"]
            else:
                opsi = ["Makan & Minum", "Transportasi", "Gaji Karyawan", "Belanja", "Tagihan", "Hiburan", "Lainnya"]
            kategori = st.selectbox("Kategori", opsi)
            
        ket = st.text_input("Catatan", placeholder="Cth: Beli Kopi, Bayar Listrik...")
        
        # Tombol Submit Full Width
        btn_submit = st.form_submit_button("KIRIM TRANSAKSI", type="primary", use_container_width=True)

        if btn_submit:
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
                with st.spinner('Memproses transaksi...'):
                    save_data(updated_df)
                st.toast("Transaksi Berhasil!", icon="✅")
                st.rerun()
            else:
                st.error("Nominal tidak boleh 0")

# --- 9. UI: RIWAYAT TRANSAKSI (LIST VIEW) ---
st.markdown('<div class="section-title">Riwayat Terakhir</div>', unsafe_allow_html=True)

if df.empty:
    st.info("Belum ada riwayat transaksi.")
else:
    # Persiapan Data Tampilan
    df_view = df.copy().sort_values(by="Tanggal", ascending=False)
    
    # Kita buat tampilan tabel yang sangat bersih
    # Menggunakan Column Config Streamlit untuk styling
    st.dataframe(
        df_view[['Tanggal', 'Kategori', 'Jumlah', 'Jenis']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tanggal": st.column_config.DateColumn("Tgl", format="DD/MM/YY"),
            "Kategori": st.column_config.TextColumn("Detail", width="medium"),
            "Jenis": st.column_config.TextColumn("Tipe", width="small"),
            "Jumlah": st.column_config.NumberColumn(
                "Nominal",
                format="Rp %d",
            )
        }
    )
