# simpan sebagai tambah_admin.py
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

NAMA_DATABASE = "perpustakaan.db"

# Buat koneksi ke database
conn = sqlite3.connect(NAMA_DATABASE)
cursor = conn.cursor()

# 1. Buat tabel 'pengguna' jika belum ada
print("Membuat tabel 'pengguna'...")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pengguna (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# 2. Minta input untuk membuat admin pertama
print("\n--- Membuat Akun Admin Pertama ---")
username = input("Masukkan username untuk admin: ")
password = getpass("Masukkan password untuk admin: ") # getpass menyembunyikan ketikan password

# 3. Enkripsi password sebelum disimpan ke database
# Ini sangat penting untuk keamanan! Jangan pernah menyimpan password sebagai teks biasa.
hashed_password = generate_password_hash(password)

# 4. Masukkan data admin baru ke tabel
try:
    cursor.execute(
        'INSERT INTO pengguna (username, password) VALUES (?, ?)',
        (username, hashed_password)
    )
    conn.commit()
    print(f"\nBerhasil! Pengguna admin '{username}' telah dibuat.")
except sqlite3.IntegrityError:
    print(f"\nError: Username '{username}' sudah ada. Silakan jalankan lagi dengan username lain.")

# 5. Tutup koneksi
conn.close()