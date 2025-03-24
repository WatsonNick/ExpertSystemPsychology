import streamlit as st
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

selected = option_menu(
    menu_title=None,
    options=["Halaman Utama", "Deskripsi Kecerdasan"],
    orientation="horizontal",
)
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
data_kecerdasan = [(statement, categories) for statement, categories in data_kecerdasan_dict.items()]
data_prodi = [(statement, categories) for statement, categories in data_prodi_dict.items()]

daftar_skor = {
    "Sangat Setuju": 1.0, "Setuju": 0.6, "Mungkin": 0.2, "Tidak Setuju": -0.4, "Sangat Tidak Setuju": -1.0
}

# Deskripsi kecerdasan
deskripsi_kecerdasan = {
    "Kecerdasan Logika-Matematik": "Kemampuan berpikir secara logis, sistematis, dan analitis, serta keahlian dalam memecahkan masalah matematika atau pola berpikir abstrak.",
    "Kecerdasan Linguistik-Verbal": "Kemampuan dalam menggunakan bahasa dengan efektif, baik dalam bentuk lisan maupun tulisan.",
    "Kecerdasan Kinestetik": "Kecerdasan ini berkaitan dengan kemampuan menggunakan tubuh dan koordinasi fisik untuk mengekspresikan diri, berkreasi, atau memecahkan masalah.",
    "Kecerdasan Interpersonal": "Kemampuan dalam berinteraksi, memahami, dan berkomunikasi dengan orang lain secara efektif.",
    "Kecerdasan Eksistensial": "Kemampuan dalam memahami pertanyaan-pertanyaan mendalam tentang makna hidup, keberadaan, dan filosofi.",
    "Kecerdasan Naturalis": "Kecerdasan ini berkaitan dengan kemampuan seseorang dalam mengamati, memahami, dan berinteraksi dengan alam serta dunia di sekitarnya."
}

#=========================================================================================================================
# Page Halaman Utama (Halaman Utama)
# Menampilkan pertanyaan dan pilihan jawaban
if selected == "Halaman Utama":
    st.title("Sistem Pakar Pemilihan Jurusan Kuliah")
    st.write("Jawablah pertanyaan berikut sesuai dengan karakteristik Anda!")

    # Menyimpan jawaban user
    user_answers = {}
    daftar_keys = list(daftar_skor.keys())
    default_index = len(daftar_keys) // 2

    # Tentukan jumlah pertanyaan per expander
    questions_per_expander = 10
    total_questions = len(data_kecerdasan)
    total_expanders = (total_questions + questions_per_expander - 1) // questions_per_expander

    for group_index in range(total_expanders):
        with st.expander(f"Pertanyaan {group_index * questions_per_expander + 1} - {min((group_index + 1) * questions_per_expander, total_questions)}"):
            cols = st.columns(2)
            for i in range(group_index * questions_per_expander, min((group_index + 1) * questions_per_expander, total_questions)):
                statement, _ = data_kecerdasan[i]
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            border: 2.5px solid #fb4d46;
                            border-radius: 10px;
                            padding: 15px;
                            background-color: #f9f9f9;
                            overflow: hidden;
                            line-height: 1;">
                            <a style="margin: 0;">{i + 1}. {statement}</a>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
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

    # Konversi hasil ke persen
    cf_kecerdasan = {k: round(v * 100, 2) for k, v in cf_kecerdasan.items()}
    cf_jurusan = {k: round(v * 100, 2) for k, v in cf_jurusan.items()}

    #-------------------------------------------------------------------------------------------------------------------------
    # Inisialisasi session state
    if "show_kecerdasan" not in st.session_state:
        st.session_state.show_kecerdasan = False
    if "show_jurusan" not in st.session_state:
        st.session_state.show_jurusan = False
    st.write("\n")

    col1, col2 = st.columns(2)
    # Menempatkan tombol
    with col1:
        if st.button("Lihat Hasil Kecerdasan"):
            st.session_state.show_kecerdasan = True
    with col2:
        if st.button("Lihat Hasil Jurusan"):
            st.session_state.show_jurusan = True

    # Menampilkan hasil kecerdasan dan jurusan
    col_left, col_right = st.columns(2)
    # Menampilkan hasil kecerdasan di kolom kiri (3 terbaik)
    with col_left:
        if st.session_state.show_kecerdasan:
            st.subheader("Hasil Kecerdasan")
            sorted_kecerdasan = sorted(cf_kecerdasan.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (tipe, nilai) in enumerate(sorted_kecerdasan):
                st.write(f"🎓{i + 1}. {tipe}: {nilai:.2f}%")

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
                st.write(f"🎓 {i + 1}. {jurusan}: {nilai:.2f}%")

            # Menampilkan perhitungan Certainty Factor
            with st.expander("Lihat Detail Perhitungan CF Jurusan"):
                for jurusan, logs in log_jurusan.items():
                    st.write(f"**{jurusan}**")
                    for log in logs:
                        st.write(f"- {log}")

#=========================================================================================================================
# Page Deskripsi Kecerdasan
ciri_contoh_kecerdasan = {
    "Kecerdasan Naturalis": (
        "Ciri-ciri: menyukai tanaman, hewan, dan lingkungan; mudah mengenali pola di alam; "
        "dan tertarik dengan sains alam.\n\n"
        "Contoh profesi: Ahli biologi, Petani, Dokter hewan, Aktivis lingkungan."
    ),
    "Kecerdasan Kinestetik": (
        "Ciri-ciri: terampil dalam olahraga, seni gerak; mudah belajar lewat aktivitas fisik; "
        "dan memiliki koordinasi tubuh yang baik.\n\n"
        "Contoh profesi: Atlet, Penari, Dokter bedah, Mekanik."
    ),
    "Kecerdasan Logika-Matematik": (
        "Ciri-ciri: menyukai teka-teki, cepat memahami hubungan angka dan pola, "
        "dan suka berpikir deduktif.\n\n"
        "Contoh profesi: Ilmuwan, Programmer, Insinyur, Akuntan."
    ),
    "Kecerdasan Interpersonal": (
        "Ciri-ciri: mudah memahami emosi orang lain, pandai bernegosiasi, memimpin, "
        "dan menyukai kerja tim.\n\n"
        "Contoh profesi: Psikolog, Guru, Pemimpin, Sales."
    ),
    "Kecerdasan Linguistik-Verbal": (
        "Ciri-ciri: menyukai menulis, membaca, bercerita, atau berdebat; pandai bermain kata-kata; "
        "dan memiliki ingatan kuat terhadap informasi berbasis kata.\n\n"
        "Contoh profesi: Penulis, Pengacara, Penyiar radio, Penerjemah."
    ),
    "Kecerdasan Eksistensial": (
        "Ciri-ciri: sering merenung tentang makna kehidupan, tertarik pada konsep spiritual dan filsafat, "
        "dan memiliki rasa ingin tahu tinggi tentang eksistensi.\n\n"
        "Contoh profesi: Filsuf, Rohaniawan, Konselor spiritual, Peneliti spiritual."
    )
}

if selected == "Deskripsi Kecerdasan":
    for tipe in deskripsi_kecerdasan.keys():
        with st.expander(f"{tipe}"):
            st.write(f"Deskripsi: {deskripsi_kecerdasan[tipe]}")
            st.write(ciri_contoh_kecerdasan[tipe])
