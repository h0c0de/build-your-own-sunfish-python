"""Uji Irisan 2 (Sunfish) — aturan penuh lewat suite perft.

Wasit: suite perft klasik enam posisi yang dipakai
komunitas pemrograman catur selama puluhan tahun —
posisi-posisinya dipilih justru karena memeras
rokade, en passant, promosi, pin en passant, dan
hak rokade yang gugur karena benteng ditangkap.
Angka yang salah satu saja berarti ada aturan yang
salah ditafsir.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mesin import dari_fen, perft

LULUS = 0


def ok(nama):
    global LULUS
    LULUS += 1
    print("  ok %2d. %s" % (LULUS, nama))


SUITE = [
    ("awal",
     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     {1: 20, 2: 400, 3: 8902}),
    ("kiwipete",
     "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/"
     "R3K2R w KQkq - 0 1",
     {1: 48, 2: 2039, 3: 97862}),
    ("posisi3-en-passant-pin",
     "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
     {1: 14, 2: 191, 3: 2812, 4: 43238}),
    ("posisi4-promosi-rokade",
     "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/"
     "R2Q1RK1 w kq - 0 1",
     {1: 6, 2: 264, 3: 9467}),
    ("posisi5",
     "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R "
     "w KQ - 1 8",
     {1: 44, 2: 1486, 3: 62379}),
    ("posisi6",
     "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/"
     "1PP1QPPP/R4RK1 w - - 0 10",
     {1: 46, 2: 2079, 3: 89890}),
]

for nama, fen, emas in SUITE:
    pos = dari_fen(fen)
    for kedalaman in sorted(emas):
        n = perft(pos, kedalaman)
        assert n == emas[kedalaman], (nama, kedalaman, n,
                                      emas[kedalaman])
    ok("%s: perft %s cocok" % (
        nama, "/".join(str(emas[d]) for d in sorted(emas))))

print("\nIRISAN 2 HIJAU: %d pemeriksaan" % LULUS)
