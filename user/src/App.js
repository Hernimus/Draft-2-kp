



import { BrowserRouter, Routes, Route } from "react-router-dom";
import Katalog from "./pages/katalog/Katalog";
import Admin from "./pages/admin/Admin";
import TambahBuku from "./pages/admin/TambahBuku";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Katalog />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/tambah" element={<TambahBuku />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
