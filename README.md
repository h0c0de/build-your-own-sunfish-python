# Build Your Own — Mesin Catur (Sunfish)

Mesin catur lengkap dalam Python murni yang ditulis
ulang sebagai latihan belajar mengikuti arsitektur
**Sunfish** karya Thomas Dybdahl Ahle — mesin yang
terkenal karena intinya hanya ~111 baris tetapi cukup
kuat untuk mengalahkan kebanyakan manusia.

Sumber: github.com/thomasahle/sunfish (GPL v3;
build ini juga GPL v3 — lihat bagian Lisensi).
Sumbernya bukan tutorial bertahap melainkan satu
berkas padat; struktur irisan diturunkan dari
arsitekturnya dan dicatat di `RENCANA.md`.

## Isi

| Berkas | Isi |
|---|---|
| `mesin.py` | Papan string 120 karakter, tabel petak-bidak, generator langkah pseudo-sah, model tangkap-raja, parser FEN |
| `cari.py` | Pencarian MTD-bi (C*): tabel transposisi, pencarian tenang, langkah nol, skor mate berjarak |
| `sunfish.py` | Loop UCI ringkas (startpos + go) |
| `uji_irisan1.py` … `uji_irisan4.py` | Uji per irisan (total 20 pemeriksaan) |
| `emas_irisan3.py` | Data diferensial beku dari modul hulu |
| `CATATAN.md` | Catatan belajar per irisan |

## Menjalankan

```bash
python3 sunfish.py
# lalu bicara UCI:
# uci
# position startpos moves e2e4 e7e5
# go wtime 60000 btime 60000
```

## Menguji

```bash
python3 uji_irisan1.py   # papan & perft awal (7)
python3 uji_irisan2.py   # suite perft 6 posisi (6)
python3 uji_irisan3.py   # evaluasi & pencarian (5)
python3 uji_irisan4.py   # UCI + regresi penuh (2)
```

Wasit yang dipakai: angka perft baku komunitas
(Kiwipete kedalaman 3 = 97862, dst.), diferensial
skor/nilai melawan modul hulu pada 9 posisi beku,
mate-in-1, dan kemenangan KQK lewat main-sendiri.

## Tiga ide yang membuatnya bekerja

1. **Papan selalu dari sudut pandang yang bergerak.**
   Tiap langkah diakhiri `rotate()` — papan dibalik
   dan huruf ditukar besar/kecil — sehingga generator
   langkah dan evaluasi hanya ditulis sekali, untuk
   "kita", selamanya.
2. **Kesahan = raja tidak tertangkap.** Langkah
   dibangkitkan pseudo-sah; langkah yang membiarkan
   raja sendiri bisa ditangkap lawan dinyatakan tidak
   sah. Rokade lewat petak terserang, pin en passant,
   dan skak semuanya tersaring oleh satu mekanisme ini.
3. **Skor hidup di dalam posisi.** `value()` adalah
   satu-satunya tempat evaluasi: perubahan skor sebuah
   langkah, ditambahkan saat langkah dimainkan. Tak
   ada evaluasi ulang dari nol di dalam pencarian.

## Di luar lingkup (jujur)

Penyempurnaan master 2026 yang paling halus — LMR,
langit-langit futility, probe langkah-nol dalam —
tidak diimplementasikan; pencarian di sini bentuk
klasiknya. Modul UI penuh hulu (FEN via UCI,
pondering) dan varian NNUE juga di luar lingkup.
Rinciannya di `RENCANA.md`.

## Temuan paling menarik

Skor Sunfish **berjangkar di posisi awal**: jumlah
tabel petak-bidak secara naif pada posisi awal adalah
38, tetapi skor permainan didefinisikan 0 di sana, dan
selisih itu konstan (membalik tanda tiap ply) di
sepanjang permainan — akibat tabel yang tidak simetris
cermin. Posisi dari FEN harus dikoreksi jangkar ini
agar konsisten dengan posisi hasil permainan.
Ceritanya di `CATATAN.md` irisan 3.

## Lisensi

GPL v3, mengikuti Sunfish hulu
(Copyright © Thomas Dybdahl Ahle dan kontributor).
Kode di sini adalah penulisan ulang untuk belajar;
tabel petak-bidak adalah data tuning milik hulu.
