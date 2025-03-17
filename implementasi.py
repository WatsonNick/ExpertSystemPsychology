import streamlit as st
import numpy as np
import pandas as pd
st.set_page_config(layout="wide")

#-------------------------------------------------------------------------------------------------------------------------
# Impor data dari file CSV
file_csv = pd.read_csv("Copy of fakta-diagnosis - Sheet1.csv")
file_csv.set_index('No', inplace=True)

# Dictionary untuk menyimpan data
data_kecerdasan_dict = {}
data_prodi_dict = {}

# Iterasi melalui baris DataFrame
for index, row in file_csv.iterrows():
    statement = row['Ciri-ciri']
    category_cerdas = row['Ciri-Ciri Kecerdasan']
    category_prodi = row['Prodi']
    score = row['MB'] - row['MD']

    if statement not in data_kecerdasan_dict:
        data_kecerdasan_dict[statement] = {}
    if statement not in data_prodi_dict:
        data_prodi_dict[statement] = {}

    data_kecerdasan_dict[statement][category_cerdas] = score
    data_prodi_dict[statement][category_prodi] = score

# Mengonversi ke format tuple
data_kecerdasan= [(statement, categories) for statement, categories in data_kecerdasan_dict.items()]
data_prodi= [(statement, categories) for statement, categories in data_prodi_dict.items()]

daftar_skor = {
    "Sangat Setuju": 1.0, "Setuju": 0.6, "Mungkin": 0.2, "Tidak Setuju": -0.4, "Sangat Tidak Setuju": -1.0
}

#-------------------------------------------------------------------------------------------------------------------------
# Menampilkan pertanyaan dan pilihan jawaban
st.title("Sistem Pakar Pemilihan Jurusan Kuliah")
st.write("Jawablah pertanyaan berikut sesuai dengan kecenderungan Anda.")

# Menyimpan jawaban user
user_answers = {}
cols = st.columns(2)
for i, (statement, _) in enumerate(data_kecerdasan):
    with cols[i % 2]:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; 
                    margin-bottom: 10px; background-color: #f9f9f9; height: 100px;
                    overflow: hidden; line-height: 1.5;">
                    <h5 style="margin: 0;">{f"{i + 1}. {statement}"}</h5>
                </div>""", 
                unsafe_allow_html=True
            )
            # Pilihan jawaban untuk user
            response = st.radio("", list(daftar_skor.keys()), key=f"{statement}_{i}", horizontal=True, index=len(daftar_skor) // 2)
            st.write("")
            user_answers[statement] = daftar_skor[response]

#-------------------------------------------------------------------------------------------------------------------------
# Hitung Certainty Factor untuk setiap kecerdasan
cf_kecerdasan = {}
log_kecerdasan = {}

for statement, answer in data_kecerdasan:
    cf_evidence = user_answers[statement]
    for tipe_cerdas, cf_pakar in answer.items():
        cf_value = cf_evidence * cf_pakar  # Hitung nilai CF baru
        if tipe_cerdas in cf_kecerdasan:
            old_value = cf_kecerdasan[tipe_cerdas]
            # Menentukan aturan yang digunakan berdasarkan tanda CF
            if old_value >= 0 and cf_value >= 0:  # Keduanya positif
                cf_kecerdasan[tipe_cerdas] = old_value + cf_value * (1 - old_value)
                log_kecerdasan[tipe_cerdas].append(
                    f"CF = {old_value:.2f} + ({cf_value:.2f} * (1 - {old_value:.2f})) = {cf_kecerdasan[tipe_cerdas]:.2f}"
                )
            elif old_value < 0 and cf_value < 0:  # Keduanya negatif
                cf_kecerdasan[tipe_cerdas] = old_value + cf_value * (1 + old_value)
                log_kecerdasan[tipe_cerdas].append(
                    f"CF = {old_value:.2f} + ({cf_value:.2f} * (1 + {old_value:.2f})) = {cf_kecerdasan[tipe_cerdas]:.2f}"
                )
            else:  # Satu positif, satu negatif
                cf_kecerdasan[tipe_cerdas] = (old_value + cf_value) / (1 - min(abs(old_value), abs(cf_value)))
                log_kecerdasan[tipe_cerdas].append(
                    f"CF = ({old_value:.2f} + {cf_value:.2f}) / (1 - min(|{old_value:.2f}|, |{cf_value:.2f}|)) = {cf_kecerdasan[tipe_cerdas]:.2f}"
                )
        else:
            cf_kecerdasan[tipe_cerdas] = cf_value
            log_kecerdasan[tipe_cerdas] = [f"CF Awal = {cf_evidence:.2f} * {cf_pakar:.2f} = {cf_value:.2f}"]

# Hitung Certainty Factor untuk setiap jurusan
cf_jurusan = {}
log_jurusan = {}

for statement, answer in data_prodi:
    cf_evidence = user_answers[statement]
    for jurusan, cf_pakar in answer.items():
        cf_value = cf_evidence * cf_pakar
        if jurusan in cf_jurusan:
            old_value = cf_jurusan[jurusan]
            if old_value >= 0 and cf_value >= 0:  # Keduanya positif
                cf_jurusan[jurusan] = old_value + cf_value * (1 - old_value)
                log_jurusan[jurusan].append(
                    f"CF = {old_value:.2f} + ({cf_value:.2f} * (1 - {old_value:.2f})) = {cf_jurusan[jurusan]:.2f}"
                )
            elif old_value < 0 and cf_value < 0:  # Keduanya negatif
                cf_jurusan[jurusan] = old_value + cf_value * (1 + old_value)
                log_jurusan[jurusan].append(
                    f"CF = {old_value:.2f} + ({cf_value:.2f} * (1 + {old_value:.2f})) = {cf_jurusan[jurusan]:.2f}"
                )
            else:  # Satu positif, satu negatif
                cf_jurusan[jurusan] = (old_value + cf_value) / (1 - min(abs(old_value), abs(cf_value)))
                log_jurusan[jurusan].append(
                    f"CF = ({old_value:.2f} + {cf_value:.2f}) / (1 - min(|{old_value:.2f}|, |{cf_value:.2f}|)) = {cf_jurusan[jurusan]:.2f}"
                )
        else:
            cf_jurusan[jurusan] = cf_value
            log_jurusan[jurusan] = [f"CF Awal = {cf_evidence:.2f} * {cf_pakar:.2f} = {cf_value:.2f}"]

#-------------------------------------------------------------------------------------------------------------------------
# Inisialisasi session state jika belum ada
if "show_kecerdasan" not in st.session_state:
    st.session_state.show_kecerdasan = False
if "show_jurusan" not in st.session_state:
    st.session_state.show_jurusan = False

st.write("\n")
# Membuat dua kolom untuk tombol
col1, col2 = st.columns(2)
# Menempatkan tombol di kolom masing-masing
with col1:
    if st.button("Lihat Hasil Kecerdasan"):
        st.session_state.show_kecerdasan = True
with col2:
    if st.button("Lihat Hasil Jurusan"):
        st.session_state.show_jurusan = True

# Membuat dua kolom untuk hasil (agar tampil sejajar)
col_left, col_right = st.columns(2)

# Menampilkan hasil kecerdasan di kolom kiri (3 terbaik)
with col_left:
    if st.session_state.show_kecerdasan:
        st.subheader("Hasil Kecerdasan")
        sorted_kecerdasan = sorted(cf_kecerdasan.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (tipe, nilai) in enumerate(sorted_kecerdasan):
            st.write(f"{i + 1}. {tipe}: {nilai:.2f}")

        # Menampilkan perhitungan Certainty Factor
        with st.expander("Lihat Detail Perhitungan CF Kecerdasan"):
            for tipe, logs in log_kecerdasan.items():
                st.write(f"**{tipe}**")
                for log in logs:
                    st.write(f"- {log}")

# Menampilkan hasil jurusan di kolom kanan (3 terbaik)
with col_right:
    if st.session_state.show_jurusan:
        st.subheader("Hasil Rekomendasi Jurusan")
        sorted_jurusan = sorted(cf_jurusan.items(), key=lambda x: x[1], reverse=True)[:3] 
        for i, (jurusan, nilai) in enumerate(sorted_jurusan):
            st.write(f"🎓 {i + 1}. {jurusan}: {nilai:.2f}")

        # Menampilkan perhitungan Certainty Factor
        with st.expander("Lihat Detail Perhitungan CF Jurusan"):
            for jurusan, logs in log_jurusan.items():
                st.write(f"**{jurusan}**")
                for log in logs:
                    st.write(f"- {log}")