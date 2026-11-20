# CATATAN — Mesin Catur Sunfish

Satu halaman per irisan: konsep inti + temuan.

## Irisan 1 — Papan 120 & model tangkap-raja

**Konsep inti.** Papan adalah string 10×12: bantalan
spasi/newline di sekeliling 8×8 membuat "keluar papan"
cukup dideteksi dari karakter, tanpa aritmetika batas.
A1=91, H1=98, A8=21, H8=28. Generator langkah mengikuti
sinar arah per bidak dan bersifat PSEUDO-sah: ia bahkan
menghasilkan langkah "menangkap raja lawan". Kesahan
adalah properti sesudah langkah dimainkan — bila lawan
punya langkah tangkap-raja, langkah kita tidak sah.
Satu mekanisme ini menggantikan seluruh kode deteksi
skak/pin/rokade-aman yang biasa memenuhi mesin catur.

**Temuan.**
- Rokade dibangkitkan dari sinar BENTENG: benteng di
  A1/H1 bergeser, dan saat petak di sampingnya berisi
  raja, langkah raja dua petak disisipkan. Jalur kosong
  antara benteng dan raja adalah syarat rokade — sinar
  yang putus oleh bidak apa pun otomatis membatalkannya.
- Skor awal tepat 0 dan perft 20/400/8902 cocok — papan,
  arah, dan rotasi benar sejak irisan pertama.

## Irisan 2 — Suite perft: aturan yang diperas

**Konsep inti.** Perft menghitung daun pohon langkah
sah; angka bakunya adalah kontrak paling kejam untuk
generator langkah — selisih satu saja berarti ada satu
aturan yang salah tafsir di satu sudut papan.

**Temuan.**
- Enam posisi klasik lolos semua, termasuk posisi 3
  (pin en passant horizontal: pion yang menangkap e.p.
  membuka garis benteng ke rajanya sendiri — tersaring
  murni oleh model tangkap-raja, tanpa kode khusus) dan
  Kiwipete (rokade kedua pihak + promosi di posisi 4).
- Hak rokade lawan (bc) disimpan dalam KERANGKA LAWAN:
  bc[0] terikat petak H8 mutlak, bc[1] ke A8 — karena
  sesudah rotate() kerangka lawan menjadi kerangka
  kita, dan di sana A1-nya adalah H8 mutlak. Konvensi
  ini yang membuat FEN->Posisi benar untuk rokade.

## Irisan 3 — Evaluasi berjangkar & MTD-bi

**Konsep inti.** bound(pos, gamma, kedalaman) tidak
mengembalikan skor eksak melainkan batas yang lebih
baik dari gamma; driver MTD-bi mempersempit kurung
dengan pencarian biner sampai lebar <= 15
(EVAL_ROUGHNESS — sekaligus harga 1 ply jarak mate,
agar mate tercepat selalu menang dari mate lambat).

**Temuan (yang paling berharga di build ini).**
- Skor Sunfish TIDAK sama dengan jumlah PST naif dari
  papan: F(posisi awal) = 38, padahal skor permainan
  didefinisikan 0 di sana. Tabel PST tidak simetris
  cermin (cermin 119-i adalah rotasi 180°, menukar
  lajur a<->h), sehingga skor hanya terdefinisi
  inkremental dari jangkar posisi awal; selisih F-skor
  konstan 38 dan membalik tanda tiap ply. Diferensial
  9 posisi emas membuktikannya angka-per-angka, dan
  dari_fen() mengoreksi jangkar ini.
- KQK pada kedalaman 3 TIDAK mate dalam 80 ply: ratu
  berputar mengikuti PST. Kedalaman 4 mate dalam 25
  ply — horizon mate harus masuk jangkauan pencarian;
  PST saja tidak memaksa mate. Tabel raja akhir
  (RAJA_AKHIR) bekerja: raja lawan terdorong ke sudut.
- Skor mate yang membawa kedalaman tersisa membuat
  posisi skakmat terbaca <= -MATE_BAWAH dan stalemate
  tepat 0 dari bound() yang sama.

## Irisan 4 — UCI & anggaran waktu

**Konsep inti.** Loop UCI bawaan sunfish.py: anggaran
langkah = jam/40 + increment − 200 ms jeda; batas
lembut (berhenti memulai iterasi) dan batas keras
(tenggat di dalam pencarian, dicek tiap 2048 node).

**Temuan.**
- Hanya langkah dari kedalaman yang SELESAI yang
  boleh dipercaya: probe yang terpotong tenggat di
  tengah kedalaman bisa memegang langkah sampah dari
  jendela gamma yang belum menetap. Driver menahan
  `terbaik` dari kedalaman sebelumnya dan hanya
  mempromosikan kandidat saat kedalaman baru mulai.
- Protokol terverifikasi sebagai proses terpisah:
  bestmove dari startpos dan sesudah 1.e4 e5 keduanya
  anggota himpunan langkah sah yang dihitung
  independen oleh mesin.py.
