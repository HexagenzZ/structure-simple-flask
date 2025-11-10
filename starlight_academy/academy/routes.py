from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from academy.db import get_conn
from psycopg2.extras import RealDictCursor

main = Blueprint('main', __name__)

@main.route('/')
def index():
    msg = request.args.get('msg', '')
    return render_template('add_student.html', msg=msg)

@main.route('/students')
def list_student():
    msg = request.args.get('msg', '')
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa ORDER BY nim")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('list_student.html', data=data, msg=msg)

@main.route('/add', methods=['POST'])
def add_student():
    form = {k: request.form.get(k, '').strip() for k in
            ['nim', 'nama', 'tahun_masuk', 'alamat', 'tanggal_lahir']}

    if not all(form.values()):
        return redirect(url_for('main.index', msg="⚠️ Lengkapi semua kolom terlebih dahulu!"))

    try:
        datetime.strptime(form['tanggal_lahir'], "%Y-%m-%d")
    except ValueError:
        return redirect(url_for('main.index', msg="⚠️ Format tanggal salah!"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nim FROM mahasiswa WHERE nim=%s", (form['nim'],))
    if cur.fetchone():
        cur.close()
        conn.close()
        return redirect(url_for('main.index', msg=f"❌ NIM {form['nim']} sudah terdaftar!"))

    cur.execute("""
        INSERT INTO mahasiswa (nim, nama, tahun_masuk, alamat, tanggal_lahir)
        VALUES (%s, %s, %s, %s, %s)
    """, (form['nim'], form['nama'], form['tahun_masuk'], form['alamat'], form['tanggal_lahir']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('main.list_student', msg="✅ Data berhasil ditambahkan!"))

@main.route('/detail/<nim>')
def detail_student(nim):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa WHERE nim=%s", (nim,))
    student = cur.fetchone()
    cur.close()
    conn.close()

    if not student:
        return redirect(url_for('main.list_student', msg="⚠️ Data tidak ditemukan!"))
    return render_template('detail_student.html', s=student)

@main.route('/delete/<nim>')
def delete_student(nim):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM mahasiswa WHERE nim=%s", (nim,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    msg = "🗑️ Data berhasil dihapus!" if deleted else "⚠️ Data tidak ditemukan!"
    return redirect(url_for('main.list_student', msg=msg))

@main.route('/api/students')
def get_students_json():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM mahasiswa ORDER BY nim")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

