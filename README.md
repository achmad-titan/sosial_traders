# TraderCore - Advanced Social Trading Portfolio Platform

## 📌 Deskripsi Proyek
TraderCore adalah platform ekosistem trading modern yang menjembatani kebutuhan teknis monitoring portofolio dengan aspek interaksi sosial. Proyek ini dibangun untuk menjawab tantangan transparansi dalam dunia trading, di mana pengguna dapat menunjukkan performa mereka secara terverifikasi melalui sistem database terintegrasi.

Platform ini menggunakan arsitektur **Decoupled (Separation of Concerns)**, memisahkan antara Logic Backend (FastAPI) dan Interface Frontend (HTML/JS), yang memungkinkan skalabilitas dan performa tinggi bagi pengguna akhir.

---

## 🏗️ Arsitektur dan Teknologi

### 1. Backend: FastAPI & Python 3.14
Pemilihan **FastAPI** didasarkan pada efisiensi eksekusi asinkronus (ASGI) yang setara dengan bahasa pemrograman tingkat tinggi lainnya.
- **SQLAlchemy (ORM):** Digunakan untuk abstraksi database MySQL, memastikan manajemen data aman dari ancaman SQL Injection melalui query terparameterisasi.
- **Bcrypt (Hashing):** Implementasi keamanan kredensial. Password diproses melalui *one-way hashing* kompleks sebelum disimpan di database.
- **JWT (JSON Web Token):** Standar industri untuk **Stateless Authentication**, menjaga sesi pengguna tetap aman tanpa membebani memori server.

### 2. Frontend: Tailwind CSS & Fetch API
Antarmuka pengguna dikembangkan dengan **Tailwind CSS** menggunakan pendekatan *Utility-First* untuk menciptakan tema **Dark Mode** yang profesional, ergonomis, dan minimalis.
- **Fetch API:** Menghubungkan frontend dengan server secara asinkron (AJAX), memberikan pengalaman pengguna yang mulus tanpa perlu memuat ulang halaman sepenuhnya (Single Page Experience).

---

## 📊 Hasil Uji Aplikasi & Kualitas (User Acceptance Testing)

Pengujian dilakukan secara menyeluruh untuk memvalidasi setiap modul fungsionalitas berdasarkan standar kualitas yang ditetapkan:

| No | Modul Fitur | Detail Fungsionalitas & Aspek Kualitas | Status |
| :--- | :--- | :--- | :--- |
| 1 | **Autentikasi User** | Verifikasi Sign Up dan Login. Sistem mampu mengenali kredensial valid dan memberikan akses token JWT secara aman. | ✅ Pass |
| 2 | **Integrasi Akun Trading** | User dapat melakukan input data akun MetaTrader (Nomor akun, Server, Saldo) yang terhubung langsung secara relasional ke ID pengguna. | ✅ Pass |
| 3 | **Kendali Privasi** | Implementasi logika visibilitas profil. User dapat beralih antara Mode Publik atau Private untuk menyembunyikan data sensitif. | ✅ Pass |
| 4 | **Dashboard & Mode Tamu** | Hirarki akses data yang tepat. Tamu (Guest) dapat melihat statistik umum, sementara fitur manajerial dikunci di balik sistem Login. | ✅ Pass |
| 5 | **Sistem Sosial (Follow)** | Implementasi relasi *Many-to-Many*. Sistem menyertakan *Self-follow protection* untuk menjaga integritas data sosial. | ✅ Pass |
| 6 | **Moderasi & Reporting** | Fitur pelaporan akun bermasalah untuk menjaga kualitas komunitas, tersimpan secara terstruktur dalam database. | ✅ Pass |
| 7 | **Forum Komunitas** | Media diskusi terintegrasi yang menarik data profil penulis secara otomatis melalui relasi Foreign Key database. | ✅ Pass |
| 8 | **Global Leaderboard** | Algoritma pengurutan berdasarkan akumulasi ekuitas tertinggi untuk memberikan transparansi peringkat trader global. | ✅ Pass |
| 9 | **Pencarian & Kartu Profil** | Fitur pencarian username spesifik dan pembuatan kartu profil visual berbasis CSS modern untuk keperluan reputasi digital. | ✅ Pass |

---

## 🛠️ Panduan Instalasi & Penggunaan

### Prasyarat:
- Python 3.10+
- Database MySQL (Laragon/XAMPP)

### Langkah-langkah:
1. **Clone Repository:**
   ```bash
   git clone [https://github.com/achmad-titan/sosial_traders.git](https://github.com/achmad-titan/sosial_traders.git)

2. **Setup Virtual Environment:**
   ```bash
   python -m venv env
    ./env/Scripts/activate

3. **Instalasi Dependency:**
    ```Bash
    pip install fastapi uvicorn sqlalchemy mysql-connector-python passlib[bcrypt] pyjwt

4. **Konfigurasi Database:**
    Pastikan MySQL aktif. Sistem akan menginisialisasi tabel secara otomatis saat server dijalankan pertama kali.

5. **Running Server:**
    ```Bash
    uvicorn main:app --reload

Dikembangkan oleh Achmad Titan Dewa Ruci (202310370311394)
Implementasi nyata dari pemrograman jaringan, manajemen database relasional, dan arsitektur web modern.
