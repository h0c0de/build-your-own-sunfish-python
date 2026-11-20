# RENCANA — Build 21: Mesin Catur Sunfish

Seri build-your-own-x, build ke-21. Sumber di luar fork:
**Sunfish** karya Thomas Dybdahl Ahle — mesin catur
Python minimalis (GPL v3), dibaca utuh dari berkas
`sunfish.py` master (commit e396948a) pada 20 Nov 2026.
Berbeda dari kebanyakan build seri ini, sumbernya
bukan tutorial bertahap melainkan satu berkas padat;
struktur irisan di sini DITURUNKAN dari arsitekturnya.

Bukti emas SEBELUM kode proyek ditulis (skrip sekali
pakai melawan modul hulu asli): perft posisi awal
kedalaman 1/2/3 = 20/400/8902 COCOK dengan filter
kesahan tangkap-raja, dan skor posisi awal = 0.

## Ruang lingkup (dinyatakan di muka)

MASUK — arsitektur inti Sunfish secara setia:
- Papan string 120 karakter berlapis bantalan; posisi
  selalu dari sudut pandang pihak yang bergerak
  (rotate() membalik papan + swapcase tiap langkah).
- Generator langkah pseudo-sah ala Micro-Max: kesahan
  TIDAK dicek saat membangkitkan — langkah sah adalah
  yang sesudah dimainkan raja sendiri tidak bisa
  ditangkap lawan (model tangkap-raja), termasuk
  rokade lewat petak terserang dan en passant.
- Evaluasi tabel petak-bidak (PST) dengan skor
  inkremental di dalam Position.value(); tabel raja
  tengah/akhir permainan (K_MID/K_END).
- Pencarian MTD-bi (C*) dengan tabel transposisi
  (batas bawah/atas), pencarian tenang (QS), langkah
  nol (null move), urutan langkah menurut nilai +
  langkah killer dari tabel, deteksi repetisi, dan
  skor mate berjarak (EVAL_ROUGHNESS per ply).
- Loop UCI bawaan sunfish.py (startpos + go wtime).

DILUAR — dicatat jujur, bukan disembunyikan:
- Penyempurnaan master 2026 yang paling halus: LMR,
  langit-langit futility, dan probe bahan bakar
  langkah-nol dalam (fuel probe). Pencarian di sini
  bentuk klasiknya: MTD-bi + QS + null move.
- Modul UI penuh hulu (sunfish_ui: FEN via UCI,
  pondering, opsi Hash) — loop UCI di sini yang
  ringkas bawaan sunfish.py.
- Varian NNUE, aturan seri 50 langkah (hulu sendiri
  juga tidak mendukungnya), dan pembuktian formal
  Lean yang menyertai master 2026.
- Parser FEN adalah tambahan berlabel untuk keperluan
  uji (hulu menerimanya lewat modul UI).

## Irisan

- [x] Irisan 1 — Papan & langkah: PST terbantalan,
  Position (gen_moves/rotate/move/value), model
  tangkap-raja. Wasit: perft posisi awal 20/400/8902
  dan skor awal 0.
- [x] Irisan 2 — Aturan penuh: FEN, rokade, en
  passant, promosi, hak rokade yang gugur. Wasit:
  suite perft klasik enam posisi (Kiwipete d3 =
  97862, posisi 3–6) — angka komunitas baku.
- [x] Irisan 3 — Evaluasi & pencarian: skor
  inkremental == hitung-ulang pada posisi acak
  (diferensial modul hulu, nilai dibekukan sebagai
  emas), MTD-bi menemukan mate-in-1, posisi skakmat
  dinilai mate, stalemate 0, dan KQK dimenangkan
  lewat main-sendiri.
- [x] Irisan 4 — UCI & finale: loop UCI menjawab
  uci/isready dan memberi bestmove sah dari
  startpos; suite perft penuh hijau; regresi
  irisan 1–3.

## Pagar selesai

- [x] `uji_irisan1.py` … `uji_irisan4.py` semua hijau.
- [x] Perft enam posisi cocok pada semua kedalaman
  yang diuji.
- [x] `CATATAN.md` satu halaman per irisan: konsep inti + temuan.
- [ ] Repo GitHub publik `build-your-own-sunfish-python`
  terbit dan terverifikasi (SHA blob lokal == remote,
  halaman publik terbaca).
