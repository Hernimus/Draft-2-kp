# simpan sebagai opac/admin/routes.py
import sqlite3
import math
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from functools import wraps

# Membuat Blueprint untuk bagian admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

NAMA_DATABASE = "perpustakaan.db"

# ... (fungsi get_db_connection dan generate_pagination bisa disalin ke sini) ...
def get_db_connection():
    conn = sqlite3.connect(NAMA_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_pagination(current_page, total_pages):
    if total_pages <= 7: return list(range(1, total_pages + 1))
    pages = {1, total_pages, current_page, current_page - 1, current_page - 2, current_page + 1, current_page + 2}
    sorted_pages = sorted([p for p in pages if 1 <= p <= total_pages])
    paginated_list = []
    last_page = 0
    for page in sorted_pages:
        if last_page + 1 < page: paginated_list.append(None)
        paginated_list.append(page)
        last_page = page
    return paginated_list

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Anda harus login untuk mengakses halaman ini.", "warning")
            return redirect(url_for('public.login')) # Arahkan ke blueprint public
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
def admin_dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    conn = get_db_connection()
    total_buku = conn.execute('SELECT COUNT(*) FROM buku').fetchone()[0]
    total_halaman = math.ceil(total_buku / per_page)
    offset = (page - 1) * per_page
    katalog = conn.execute('SELECT * FROM buku ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
    conn.close()
    pagination_numbers = generate_pagination(page, total_halaman)
    return render_template('admin/dashboard.html', katalog=katalog, page=page, total_halaman=total_halaman, pagination=pagination_numbers, per_page=per_page)

# ... (semua fungsi admin lainnya disalin ke sini, dengan @admin_bp.route) ...
# Contoh:
@admin_bp.route('/tambah', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/tambah_buku.html')

@admin_bp.route('/cari')
@login_required
def admin_cari():
    query = request.args.get('q', '')
    conn = get_db_connection()
    hasil = conn.execute(
        'SELECT * FROM buku WHERE judul_buku LIKE ? OR pengarang LIKE ? OR isbn LIKE ?',
        (f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('admin/admin_cari.html', hasil_pencarian=hasil, query=query)

@admin_bp.route('/edit/<int:buku_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_dashboard'))
    conn.close()
    return render_template('admin/edit_buku.html', buku=buku)

@admin_bp.route('/hapus/<int:buku_id>', methods=['POST'])
@login_required
def hapus_buku(buku_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM buku WHERE id = ?', (buku_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin_dashboard'))
