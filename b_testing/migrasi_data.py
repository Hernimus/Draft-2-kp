# opac_web.py - Versi Final dengan SEMUA KOLOM
import sqlite3
import math
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-sangat-sulit-ditebak'
NAMA_DATABASE = "perpustakaan.db"

def get_db_connection():
    conn = sqlite3.connect(NAMA_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rute Otentikasi dan Publik (Tidak Berubah) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ... (logika login tidak berubah) ...
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM pengguna WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Username atau password salah.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def halaman_utama():
    return render_template('index.html')

@app.route('/cari')
def halaman_hasil_pencarian():
    query = request.args.get('q', '')
    conn = get_db_connection()
    hasil = conn.execute(
        'SELECT * FROM buku WHERE judul_buku LIKE ? OR pengarang LIKE ? OR isbn LIKE ?', 
        (f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('hasil.html', hasil_pencarian=hasil, query=query)

# --- Halaman Admin ---
@app.route('/admin')
@login_required
def admin_dashboard():
    page = request.args.get('page', 1, type=int)
    buku_per_halaman = 20 # Tampilkan lebih banyak per halaman
    conn = get_db_connection()
    total_buku = conn.execute('SELECT COUNT(*) FROM buku').fetchone()[0]
    total_halaman = math.ceil(total_buku / buku_per_halaman)
    offset = (page - 1) * buku_per_halaman
    katalog = conn.execute(
        'SELECT * FROM buku ORDER BY id DESC LIMIT ? OFFSET ?',
        (buku_per_halaman, offset)
    ).fetchall()
    conn.close()
    return render_template('admin.html', katalog=katalog, page=page, total_halaman=total_halaman)

# --- FUNGSI CRUD YANG DIPERBARUI ---
@app.route('/admin/tambah', methods=['GET', 'POST'])
@login_required
def tambah_buku():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO buku (judul_buku, pengarang, penerbit, tempat_terbit, tahun, isbn, 
            jilid, edisi, cetakan, jumlah_halaman, rak_buku, jumlah_buku, 
            tinggi_buku, nomor_panggil, inisial, perolehan, harga, keterangan, no_induk) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['judul_buku'], request.form['pengarang'], request.form['penerbit'],
            request.form['tempat_terbit'], request.form['tahun'], request.form['isbn'],
            request.form['jilid'], request.form['edisi'], request.form['cetakan'],
            request.form['jumlah_halaman'], request.form['rak_buku'], request.form['jumlah_buku'],
            request.form['tinggi_buku'], request.form['nomor_panggil'], request.form['inisial'],
            request.form['perolehan'], request.form['harga'], request.form['keterangan'], request.form['no_induk']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('tambah_buku.html')

@app.route('/admin/edit/<int:buku_id>', methods=['GET', 'POST'])
@login_required
def edit_buku(buku_id):
    conn = get_db_connection()
    buku = conn.execute('SELECT * FROM buku WHERE id = ?', (buku_id,)).fetchone()
    if request.method == 'POST':
        conn.execute('''
            UPDATE buku SET judul_buku = ?, pengarang = ?, penerbit = ?, tempat_terbit = ?, 
            tahun = ?, isbn = ?, jilid = ?, edisi = ?, cetakan = ?, jumlah_halaman = ?, 
            rak_buku = ?, jumlah_buku = ?, tinggi_buku = ?, nomor_panggil = ?, 
            inisial = ?, perolehan = ?, harga = ?, keterangan = ?, no_induk = ?
            WHERE id = ?
        ''', (
            request.form['judul_buku'], request.form['pengarang'], request.form['penerbit'],
            request.form['tempat_terbit'], request.form['tahun'], request.form['isbn'],
            request.form['jilid'], request.form['edisi'], request.form['cetakan'],
            request.form['jumlah_halaman'], request.form['rak_buku'], request.form['jumlah_buku'],
            request.form['tinggi_buku'], request.form['nomor_panggil'], request.form['inisial'],
            request.form['perolehan'], request.form['harga'], request.form['keterangan'], request.form['no_induk'],
            buku_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('edit_buku.html', buku=buku)

@app.route('/admin/hapus/<int:buku_id>', methods=['POST'])
@login_required
def hapus_buku(buku_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM buku WHERE id = ?', (buku_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)