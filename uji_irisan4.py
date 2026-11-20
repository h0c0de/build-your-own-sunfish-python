"""Uji Irisan 4 (Sunfish) — loop UCI & finale.

Loop UCI digerakkan sebagai proses terpisah lewat
pipa: harus menjawab uciok/readyok dan mengembalikan
bestmove yang SAH pada posisi awal dan sesudah
1.e4 e5. Finale: regresi irisan 1-3 (termasuk suite
perft penuh di irisan 2).
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mesin import (Langkah, langkah_sah, parse_petak,
                   posisi_awal, render_petak)

LULUS = 0
DASAR = os.path.dirname(os.path.abspath(__file__))


def ok(nama):
    global LULUS
    LULUS += 1
    print("  ok %2d. %s" % (LULUS, nama))


def render(m):
    return render_petak(m.i) + render_petak(m.j) + m.prom.lower()


def bicara_uci(perintah):
    r = subprocess.run([sys.executable,
                        os.path.join(DASAR, "sunfish.py")],
                       input=perintah, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout


def bestmove_dari(keluaran):
    for baris in keluaran.splitlines():
        if baris.startswith("bestmove"):
            return baris.split()[1]
    raise AssertionError("tidak ada bestmove:\n" + keluaran)


# --- Protokol dasar + bestmove sah dari startpos ---
pos = posisi_awal()
sah_awal = {render(m) for m in langkah_sah(pos)}
keluaran = bicara_uci("uci\nisready\nposition startpos\n"
                      "go wtime 20000 btime 20000\nquit\n")
assert "uciok" in keluaran and "readyok" in keluaran
bm = bestmove_dari(keluaran)
assert bm in sah_awal, bm
ok("UCI: uciok + readyok, bestmove awal sah (%s)" % bm)

# --- Sesudah 1.e4 e5: bestmove Putih tetap sah ---
pos2 = pos.move(Langkah(parse_petak("e2"), parse_petak("e4"), ""))
pos2 = pos2.move(Langkah(parse_petak("e2"), parse_petak("e4"), ""))
sah2 = {render(m) for m in langkah_sah(pos2)}
keluaran = bicara_uci("position startpos moves e2e4 e7e5\n"
                      "go wtime 20000 btime 20000\nquit\n")
bm2 = bestmove_dari(keluaran)
assert bm2 in sah2, bm2
ok("UCI: sesudah e2e4 e7e5, bestmove sah (%s)" % bm2)

print("\nIRISAN 4 HIJAU: %d pemeriksaan" % LULUS)

print("== regresi irisan 1-3 ==")
for n in (1, 2, 3):
    r = subprocess.run([sys.executable, "uji_irisan%d.py" % n],
                       cwd=DASAR, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    ok("uji_irisan%d hijau penuh" % n)

print("\nTOTAL IRISAN 4 + REGRESI: %d pemeriksaan" % LULUS)
