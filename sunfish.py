#!/usr/bin/env python3
"""Loop UCI ringkas ala sunfish.py hulu.

Menjawab uci / isready / quit, menerima
"position startpos moves ..." dan "go wtime ...
btime ...". Modul UI penuh hulu (FEN, pondering,
opsi Hash) di luar lingkup build ini — lihat
RENCANA.md.

Jalankan: python3 sunfish.py  (lalu bicara UCI)
"""

import sys
import time

from cari import Berhenti, Pencari
from mesin import Langkah, parse_petak, posisi_awal, render_petak

VERSI = "sunfish-belajar 21"
JEDA = 200  # ms: jeda jaringan + pencatatan arbiter,
            # dikurangkan dari setiap batas waktu


def main():
    pencari = Pencari()
    riwayat = [posisi_awal()]
    while True:
        try:
            args = input().split()
        except EOFError:
            break
        if not args:
            continue
        if args[0] == "uci":
            print("id name", VERSI)
            print("uciok", flush=True)
        elif args[0] == "isready":
            print("readyok", flush=True)
        elif args[0] == "quit":
            break
        elif args[:2] == ["position", "startpos"]:
            del riwayat[1:]
            for ply, teks in enumerate(args[3:]):
                i = parse_petak(teks[:2])
                j = parse_petak(teks[2:4])
                prom = teks[4:].upper()
                if ply % 2 == 1:
                    i, j = 119 - i, 119 - j
                riwayat.append(riwayat[-1].move(Langkah(i, j, prom)))
        elif args[0] == "go":
            waktu = dict(zip(args[1::2], map(int, args[2::2])))
            sisi = "wb"[len(riwayat) % 2 == 0]
            wtime = waktu.get(sisi + "time", 60000)
            winc = waktu.get(sisi + "inc", 0)
            # Anggaran langkah ini: 1/40 jam + increment,
            # dibatasi lembut 1/4 jam dan keras 1/2 jam.
            anggaran = wtime / 40 + winc - JEDA
            lembut = max(min(anggaran, wtime / 4 - JEDA), 100) / 1000
            pikir = max(min(5 * anggaran, wtime / 2 - JEDA), 200) / 1000
            mulai = time.time()
            pencari.tenggat = mulai + pikir
            pencari.lembut = mulai + lembut
            terbaik, calon, d0 = None, None, 1
            try:
                for kedalaman, gamma, skor, langkah in \
                        pencari.cari(riwayat):
                    if kedalaman > d0:
                        terbaik, d0 = calon or terbaik, kedalaman
                    if skor >= gamma:
                        if langkah is None:
                            print("info depth", kedalaman,
                                  "score cp", skor, flush=True)
                            break
                        i, j = langkah.i, langkah.j
                        if len(riwayat) % 2 == 0:
                            i, j = 119 - i, 119 - j
                        calon = render_petak(i) + render_petak(j) \
                            + langkah.prom.lower()
                        print("info depth", kedalaman,
                              "score cp", skor, "pv", calon,
                              flush=True)
            except Berhenti:
                calon = terbaik or calon
            print("bestmove", calon or terbaik or "(none)",
                  flush=True)


if __name__ == "__main__":
    main()
