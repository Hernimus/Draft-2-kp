import { useEffect, useState } from "react";
import "./Katalog.css";

function Katalog() {
  const [data, setData] = useState([]);
  const [query, setQuery] = useState("");
  const [rakFilter, setRakFilter] = useState("");
  const [rakList, setRakList] = useState([]);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(25);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedBook, setSelectedBook] = useState(null);
  const [sortBy, setSortBy] = useState("id");
  const [order, setOrder] = useState("asc");

  // 🔹 Ambil daftar rak dari backend
  useEffect(() => {
    fetch("http://localhost:5000/api/rak")
      .then((res) => res.json())
      .then((json) => setRakList(json))
      .catch((err) => console.error("Error rak:", err));
  }, []);

  // 🔹 Ambil data katalog
  useEffect(() => {
    let url = `http://localhost:5000/api/katalog?page=${page}&per_page=${limit}&sort_by=${sortBy}&order=${order}`;
    if (rakFilter) url += `&rak_filter=${encodeURIComponent(rakFilter)}`;
    fetch(url)
      .then((res) => res.json())
      .then((json) => {
        setData(json.data);
        // Calculate total pages from total and per_page
        setTotalPages(Math.ceil(json.total / limit));
      })
      .catch((err) => console.error("Error:", err));
  }, [rakFilter, page, limit, sortBy, order]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [page]);

  // ✅ Lock scroll saat modal terbuka
  useEffect(() => {
    if (selectedBook) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
  }, [selectedBook]);

  const renderPageNumbers = () => {
    const pages = [];
    let start = Math.max(1, page - 2);
    let end = Math.min(totalPages, page + 2);

    if (start > 1) {
      pages.push(
        <button key={1} onClick={() => setPage(1)} className="page-btn">
          1
        </button>
      );
      if (start > 2) pages.push(<span key="start-dots">...</span>);
    }

    for (let i = start; i <= end; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => setPage(i)}
          className={`page-btn ${i === page ? "active" : ""}`}
        >
          {i}
        </button>
      );
    }

    if (end < totalPages) {
      if (end < totalPages - 1) pages.push(<span key="end-dots">...</span>);
      pages.push(
        <button
          key={totalPages}
          onClick={() => setPage(totalPages)}
          className="page-btn"
        >
          {totalPages}
        </button>
      );
    }

    return pages;
  };

  return (
    <div className="katalog-container">
      <h2>📚 Daftar Katalog Buku</h2>

      <div className="filter-bar">
        <div className="limit-container">
          <label>
            Tampilkan:
            <select
              className="limit-select"
              value={limit}
              onChange={(e) => {
                setLimit(Number(e.target.value));
                setPage(1);
              }}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={75}>75</option>
              <option value={100}>100</option>
            </select>
            data
          </label>
        </div>

        {/* 🔹 Dropdown RAK */}
        <div className="rak-container">
          <label>
            Rak:
            <select
              className="rak-select"
              value={rakFilter}
              onChange={(e) => {
                setRakFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Semua Rak</option>
              {rakList.map((rak, idx) => (
                <option key={idx} value={rak.value}>
                  {rak.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {/* 🔹 Dropdown Sort */}
        <div className="sort-container">
          <label>
            Urutkan:
            <select
              className="sort-select"
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setPage(1);
              }}
            >
              <option value="id">Default</option>
              <option value="judul_buku">Judul Buku</option>
              <option value="pengarang">Pengarang</option>
              <option value="penerbit">Penerbit</option>
              <option value="tahun">Tahun</option>
              <option value="rak_buku">Rak</option>
            </select>
            <select
              className="order-select"
              value={order}
              onChange={(e) => {
                setOrder(e.target.value);
                setPage(1);
              }}
            >
              <option value="asc">Naik</option>
              <option value="desc">Turun</option>
            </select>
          </label>
        </div>

        {/* 🔹 Input pencarian */}
        <input
          type="text"
          placeholder="Cari judul, pengarang, atau ISBN..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setPage(1);
          }}
          className="search-input"
        />
      </div>



      <table className="katalog-table">
        <thead>
          <tr>
            <th>Judul Buku</th>
            <th>Pengarang</th>
            <th>Penerbit</th>
            <th>Tahun</th>
            <th>Rak</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((row) => (
              <tr key={row.id}>
                <td>{row.judul_buku}</td>
                <td>{row.pengarang}</td>
                <td>{row.penerbit}</td>
                <td>{row.tahun}</td>
                <td>{row.rak_buku}</td>
                <td>
                  <button
                    className="detail-btn"
                    onClick={() => setSelectedBook(row)}
                  >
                    Detail
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6" style={{ textAlign: "center" }}>
                Tidak ada data
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="katalog-list">  
        {data.length > 0 ? (
          data.map((row) => (
            <div key={row.id} className="katalog-card">
              <h4>{row.judul_buku}</h4>
              <p><b>Pengarang:</b> {row.pengarang || "Tidak diketahui"}</p>
              <p><b>Penerbit:</b> {row.penerbit || "-"}</p>
              <p><b>Tahun:</b> {row.tahun || "-"}</p>
              <p><b>Rak:</b> {row.rak_buku || "-"}</p>
              <button
                className="detail-btn"
                onClick={() => setSelectedBook(row)}
              >
                Lihat
              </button>
            </div>
          ))
        ) : (
          <p style={{ textAlign: "center" }}>Tidak ada data</p>
        )}
      </div>


      <div className="katalog-pagination">
        <button
          disabled={page <= 1}
          onClick={() => setPage(page - 1)}
          className="page-btn"
        >
          ⬅
        </button>

        {renderPageNumbers()}

        <button
          disabled={page >= totalPages}
          onClick={() => setPage(page + 1)}
          className="page-btn"
        >
          ➡
        </button>
      </div>

     {/* 🔹 Modal Detail Buku dengan Bootstrap */}
{selectedBook && (
  <div
    className="modal fade show d-block"
    tabIndex="-1"
    style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
  >
    <div className="modal-dialog modal-lg modal-dialog-scrollable">
      <div className="modal-content">
        <div className="modal-header">
          <h5 className="modal-title">{selectedBook.judul_buku}</h5>
          <button
            type="button"
            className="btn-close"
            onClick={() => setSelectedBook(null)}
          ></button>
        </div>
        <div className="modal-body">
          <p><b>Pengarang:</b> {selectedBook.pengarang}</p>
          <p><b>Penerbit:</b> {selectedBook.penerbit}</p>
          <p><b>Tempat Terbit:</b> {selectedBook.tempat_terbit}</p>
          <p><b>Tahun:</b> {selectedBook.tahun}</p>
          <p><b>ISBN:</b> {selectedBook.isbn}</p>
          <p><b>Jilid:</b> {selectedBook.jilid}</p>
          <p><b>Edisi:</b> {selectedBook.edisi}</p>
          <p><b>Cetakan:</b> {selectedBook.cetakan}</p>
          <p><b>Jumlah Halaman:</b> {selectedBook.jumlah_halaman}</p>
          <p><b>Rak Buku:</b> {selectedBook.rak_buku}</p>
          <p><b>Jumlah Buku:</b> {selectedBook.jumlah_buku}</p>
          <p><b>Tinggi Buku (cm):</b> {selectedBook.tinggi_buku}</p>
          <p><b>Nomor Panggil:</b> {selectedBook.nomor_panggil}</p>
          <p><b>Inisial:</b> {selectedBook.inisial}</p>
          <p><b>Perolehan:</b> {selectedBook.perolehan}</p>
          <p><b>Harga:</b> {selectedBook.harga}</p>
          <p><b>Keterangan:</b> {selectedBook.ket}</p>
          <p><b>No. Induk:</b> {selectedBook.no_induk}</p>
        </div>
        <div className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setSelectedBook(null)}
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  </div>
)}
    </div>
  );
}

export default Katalog;
