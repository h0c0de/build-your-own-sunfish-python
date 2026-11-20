"""Uji Irisan 3 (Sunfish) — evaluasi & pencarian.

Wasit ganda:
1. Diferensial beku melawan modul hulu: 9 posisi dari
   permainan acak berbenih tetap (emas_irisan3.py) —
   skor posisi dan nilai value() SETIAP langkah harus
   sama persis, dan skor inkremental harus sama dengan
   hitung-ulang dari papan (skor_dari_nol).
2. Perilaku pencarian: MTD-bi menemukan mate-in-1,
   posisi skakmat dinilai mate, stalemate dinilai 0,
   dan akhir permainan KQK dimenangkan lewat
   main-sendiri (bidak terkuat seri ini: tabel raja
   akhir permainan bekerja).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cari import Pencari
from emas_irisan3 import EMAS
from mesin import (MATE_BAWAH, dari_fen, langkah_sah,
                   render_petak, skor_dari_nol)

LULUS = 0


def ok(nama):
    global LULUS
    LULUS += 1
    print("  ok %2d. %s" % (LULUS, nama))


def render(m):
    return render_petak(m.i) + render_petak(m.j) + m.prom.lower()


# --- Diferensial evaluasi ---
for fen, skor_emas, nilai_emas in EMAS:
    pos = dari_fen(fen)
    assert pos.skor == skor_emas, (fen, pos.skor, skor_emas)
    # Inkremental == jumlah naif dikurangi jangkar 38
    # (semua posisi emas bergiliran Putih).
    assert skor_dari_nol(pos) - 38 == pos.skor, fen
    nilai = sorted(((render(m), pos.value(m))
                    for m in pos.gen_moves()), reverse=True)
    assert nilai == [tuple(x) for x in nilai_emas], fen
ok("9 posisi emas: skor + nilai semua langkah identik hulu, "
   "inkremental == hitung-ulang")

# --- Mate-in-1: Benteng a1-a8 skakmat di baris belakang ---
pos = dari_fen("6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1")
hasil = Pencari().pilih(pos, 3)
assert hasil is not None
skor, langkah = hasil
assert render(langkah) == "a1a8", render(langkah)
assert skor >= MATE_BAWAH, skor
ok("mate-in-1 ditemukan: a1a8 dengan skor pita mate")

# --- Posisi sesudah mate itu: yang bergerak termate ---
pos_mate = dari_fen("R5k1/5ppp/8/8/8/8/8/6K1 b - - 0 1")
assert langkah_sah(pos_mate) == []
skor_mate = Pencari().bound(pos_mate, 0, 2)
assert skor_mate <= -MATE_BAWAH, skor_mate
ok("posisi skakmat: tak ada langkah sah, skor mate negatif")

# --- Stalemate dinilai 0 ---
pos_stale = dari_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
assert langkah_sah(pos_stale) == []
assert Pencari().bound(pos_stale, 0, 2) == 0
ok("stalemate: tak ada langkah sah, skor tepat 0")

# --- KQK main-sendiri: Ratu+ Raja vs Raja harus mate ---
# Kedalaman 4: pada kedalaman 3 ratu masih berputar
# menurut PST tanpa melihat mate (temuan uji pertama).
pos = dari_fen("8/8/8/4k3/8/8/3QK3/8 w - - 0 1")
pencari = Pencari()
riwayat = [pos]
mate = False
for _ply in range(100):
    hasil = pencari.pilih(pos, 4, riwayat)
    if hasil is None:
        # Tak bisa bergerak: mate bila kena skak
        mate = pos.rotate(langkah_nol=True).tangkap_raja() is not None
        break
    _skor, langkah = hasil
    pos = pos.move(langkah)
    riwayat.append(pos)
assert mate
ok("KQK main-sendiri berakhir skakmat dalam <= 100 ply")

print("\nIRISAN 3 HIJAU: %d pemeriksaan" % LULUS)
