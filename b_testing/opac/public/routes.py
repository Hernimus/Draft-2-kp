# simpan sebagai opac/public/routes.py
import sqlite3
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash

# Membuat Blueprint untuk bagian publik
public_bp = Blueprint('public', __name__)

NAMA_DATABASE = "perpustakaan.db"

def get_db_connection():
    conn = sqlite3.connect(NAMA_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- ROUTE HALAMAN WEB ----------
@public_bp.route('/')
def halaman_utama():
    return render_template('public/index.html')

@public_bp.route('/cari')
def halaman_hasil_pencarian():
    query = request.args.get('q', '')
    conn = get_db_connection()
    hasil = conn.execute(
        'SELECT * FROM buku WHERE judul_buku LIKE ? OR pengarang LIKE ? OR isbn LIKE ?', 
        (f'%{query}%', f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('public/hasil.html', hasil_pencarian=hasil, query=query)

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": True, "redirect": "/admin"})
            return redirect(url_for('admin.admin_dashboard'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": "Username atau password salah."}), 401
            flash("Username atau password salah.", "danger")
    return render_template('public/login.html')

@public_bp.route('/logout')
def logout():
    session.clear()
    flash("Anda telah berhasil logout.", "success")
    return redirect(url_for('public.login')) # Arahkan ke blueprint public

# ---------- API UNTUK REACT ----------
@public_bp.route('/api/katalog', methods=['GET'])
def api_katalog():
    """Ambil data buku dengan pagination + filter rak"""
    query = request.args.get('q', '')
    rak = request.args.get('rak', '')  # ✅ filter rak
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    conn = get_db_connection()

    base_query = "FROM buku WHERE 1=1"
    params = []

    if query:
        base_query += " AND (judul_buku LIKE ? OR pengarang LIKE ? OR isbn LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])

    if rak:
        base_query += " AND rak_buku = ?"
        params.append(rak)

    # Hitung total
    total = conn.execute(f"SELECT COUNT(*) {base_query}", params).fetchone()[0]

    # Ambil data dengan limit & offset
    hasil = conn.execute(
        f"SELECT * {base_query} LIMIT ? OFFSET ?",
        (*params, limit, offset)
    ).fetchall()

    # Ambil daftar rak unik
    rak_list = conn.execute("SELECT DISTINCT rak_buku FROM buku ORDER BY rak_buku").fetchall()
    conn.close()

    data = [dict(row) for row in hasil]
    all_rak = [r["rak_buku"] for r in rak_list if r["rak_buku"]]

    return jsonify({
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "all_rak": all_rak  # ✅ dikirim ke frontend
    })

# 🔹 Mapping manual Rak → Tema
@public_bp.route('/api/rak', methods=['GET'])
def api_rak():
    conn = get_db_connection()
    rak_list = conn.execute(
        "SELECT DISTINCT rak_buku FROM buku WHERE rak_buku != '' ORDER BY rak_buku"
    ).fetchall()
    conn.close()
    
    RAK_TEMA = {
        "10A": "Ensiklopedia",
        "11B": "Hukum Perdagangan",
        "1A": "Ensiklopedia",
        "1B": "Politik ",
        "1C": "Kamus",
        "1D": "Cyber Crime",
        "1E": "Hukum Islam ",
        "1F": "Hukuman Internasional",
        "1G": "Hukum Lingkungan",
        "1H": "Kamus",
        "2A": "",
        "2B": "Pidana Khusus",
        "2C": "Acara Pidana",
        "2D": "",
        "2E": "",
        "2F": "Peradilan Militer",
        "2G": "",
        "2H": "",
        "5A": "",
        "5B": "Ilmu Hukum",
        "5C": "Konsumen/PT",
        "5D": "",
        "5E": "",
        "5F": "Perpajakan",
        "5G": "",
        # tambahkan sesuai kebutuhan
    }
    
    rak_data = []
    for row in rak_list:
        rak_code = row['rak_buku']
        tema = RAK_TEMA.get(rak_code, "")
        rak_label = f"{rak_code} ({tema})" if tema else rak_code
        rak_data.append({"value": rak_code, "label": rak_label})

    print(rak_data)  # 🔹 cek di terminal Flask
    return jsonify(rak_data)

