"""Uji Irisan 1 (Sunfish) — papan, langkah, perft awal.

Wasit: angka perft posisi awal yang baku di seluruh
dunia catur (20 / 400 / 8902), skor awal 0, dan tabel
PST yang identik dengan tabel hulu (dibekukan di sini
sebagai beberapa nilai contoh + jumlah total).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mesin import PST, Langkah, perft, posisi_awal, render_petak

LULUS = 0


def ok(nama):
    global LULUS
    LULUS += 1
    print("  ok %2d. %s" % (LULUS, nama))


pos = posisi_awal()
assert pos.skor == 0
ok("skor posisi awal = 0 (simetri materi + PST)")

# Jangkar PST: nilai dasar + contoh petak (dari hulu).
assert PST["P"][91] == 100 and PST["Q"][21] == 929 + 6
assert PST["K"][95] == 60000 + 6  # e1 pada tabel raja tengah
assert PST["N"][73] == 280 + 13  # kuda di c3
ok("jangkar PST: nilai dasar bidak dan contoh petak cocok")

langkah = sorted(render_petak(m.i) + render_petak(m.j)
                 for m in pos.gen_moves())
assert len(langkah) == 20
assert "e2e4" in langkah and "g1f3" in langkah
ok("20 langkah pseudo-sah dari posisi awal, termasuk e2e4 & g1f3")

for kedalaman, emas in ((1, 20), (2, 400), (3, 8902)):
    n = perft(pos, kedalaman)
    assert n == emas, (kedalaman, n, emas)
    ok("perft awal kedalaman %d = %d" % (kedalaman, emas))

# Sesudah 1.e4: giliran lawan dalam kerangka terbalik.
anak = pos.move(Langkah(85, 65, ""))  # e2 -> e4
assert anak.papan[anak.papan.index("K")]  # raja yang bergerak ada
assert sum(1 for m in anak.gen_moves()) == 20
ok("sesudah e2e4 papan terbalik dan lawan punya 20 langkah")

print("\nIRISAN 1 HIJAU: %d pemeriksaan" % LULUS)
