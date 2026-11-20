"""Pencarian MTD-bi (C*) ala Sunfish.

bound(pos, gamma, kedalaman) tidak mengembalikan skor
eksak, melainkan batas yang lebih baik: bila gamma di
atas skor sejati s*, hasilnya batas atas baru; bila
gamma <= s*, hasilnya batas bawah baru. Driver
mempersempit kurung [bawah, atas] dengan pencarian
biner sampai lebarnya <= EVAL_ROUGHNESS — itulah
MTD-bi. Konsekuensinya bound harus fungsi murni dari
(pos, kedalaman): semua keputusan di dalamnya tidak
boleh bergantung pada gamma.

Kesahan dibaca dari skor: langkah yang membiarkan
raja tertangkap menghasilkan anak bernilai tepat
-MATE_ATAS, jadi "skor > -MATE_ATAS" adalah uji sah.

Penyempurnaan master 2026 (LMR, langit-langit
futility, probe langkah-nol dalam) SENGAJA di luar
lingkup build ini — lihat RENCANA.md.
"""

import time
from collections import namedtuple

import mesin
from mesin import MATE_ATAS, MATE_BAWAH

QS = 36            # ambang nilai untuk pencarian tenang
KERAS_MATE = 15    # EVAL_ROUGHNESS hulu: lebar berhenti
                   # kurung MTD-bi = harga 1 ply jarak mate
BATAS_TABEL = 10 ** 6

Entri = namedtuple("Entri", "bawah atas")


class Berhenti(Exception):
    """Dibangkitkan di dalam pencarian saat tenggat lewat."""


class Pencari:
    def __init__(self):
        self.tp_skor, self.tp_langkah, self.riwayat = {}, {}, set()
        self.nodes = 0
        self.tenggat = self.lembut = 1 << 62
        self.akar = None

    def bound(self, pos, gamma, kedalaman, akar=False):
        self.nodes += 1
        if self.nodes % 2048 == 0 and time.time() > self.tenggat:
            raise Berhenti
        # Kedalaman <= 0 adalah pencarian tenang; dari
        # titik itu perilaku tak lagi bergantung pada
        # kedalaman, jadi tabel menyatukannya di 0.
        kedalaman = max(kedalaman, 0)

        # Raja kita sudah tertangkap di langkah sebelumnya
        if pos.skor <= -MATE_BAWAH:
            return -MATE_ATAS

        if not akar:
            entri = self.tp_skor.get((pos, kedalaman),
                                     Entri(-MATE_ATAS, MATE_ATAS))
            if entri.bawah >= gamma:
                return entri.bawah
            if entri.atas < gamma:
                return entri.atas
            # Jangan ulangi posisi (kecuali di kedalaman 0)
            if kedalaman > 0 and pos in self.riwayat:
                return 0

        killer = self.tp_langkah.get(pos)
        # Posisi "tenang" untuk langkah nol: skor tak
        # ekstrem dan masih ada bidak besar (jaga zugzwang
        # akhir permainan raja+pion).
        tenang = abs(pos.skor) < 750 and \
            any(c in pos.papan for c in "RBNQ")
        penjaga = not akar and tenang

        def aliran():
            # Langkah nol: tidak bergerak sama sekali.
            # Hanya 2 < kedalaman < 6 dan posisi tenang.
            if 2 < kedalaman < 6 and penjaga:
                yield None, None
            # Berhenti di tempat: untuk pencarian tenang.
            if kedalaman == 0:
                yield None, None
            # Langkah killer dari pencarian sebelumnya.
            if killer and (pos.value(killer) >= QS or kedalaman):
                yield pos.value(killer), killer
            # Langkah sungguhan, nilai terbesar dulu.
            yield from sorted(
                ((v, m) for m in pos.gen_moves()
                 if (v := pos.value(m)) >= QS or kedalaman),
                reverse=True)

        terbaik, hidup = -MATE_ATAS, False
        for nilai, langkah in aliran():
            if langkah is None and kedalaman == 0:
                skor = pos.skor
            elif langkah is None:
                # Langkah nol dibatasi skor statis + satu
                # ember KERAS_MATE agar nilainya monoton.
                cap = pos.skor + KERAS_MATE
                if cap >= gamma:
                    skor = min(cap, -self.bound(
                        pos.rotate(langkah_nol=True),
                        1 - gamma, kedalaman - 4))
                    if skor >= gamma and pos.tangkap_raja():
                        langkah = pos.tangkap_raja()
                        skor, hidup = MATE_ATAS, True
                else:
                    skor = cap
            elif nilai >= MATE_BAWAH:
                # Nilai sebesar ini hanya dari menangkap raja
                skor, hidup = MATE_ATAS, True
            else:
                skor = -self.bound(pos.move(langkah),
                                   1 - gamma, kedalaman - 1)
                hidup |= skor > -MATE_ATAS
            terbaik = max(terbaik, skor)
            if terbaik >= gamma:
                if langkah is not None and kedalaman:
                    self.tp_langkah[pos] = langkah
                    if len(self.tp_langkah) > BATAS_TABEL:
                        del self.tp_langkah[next(
                            k for k in self.tp_langkah
                            if k != self.akar)]
                break

        # Tak ada langkah sah sama sekali: skakmat atau
        # stalemate. Skor mate membawa jarak (kedalaman
        # yang tersisa), agar mate tercepat yang menang.
        if kedalaman and not hidup and all(
                pos.move(m).tangkap_raja() is not None
                for m in pos.gen_moves()):
            mate = max(1 - MATE_ATAS,
                       -MATE_BAWAH - kedalaman * KERAS_MATE)
            terbaik = mate if pos.rotate(
                langkah_nol=True).tangkap_raja() else 0

        if not akar:
            self.tp_skor[pos, kedalaman] = (
                Entri(terbaik, entri.atas) if terbaik >= gamma
                else Entri(entri.bawah, terbaik))
            if len(self.tp_skor) > BATAS_TABEL:
                del self.tp_skor[next(iter(self.tp_skor))]
        return terbaik

    def cari(self, riwayat):
        """Iterative deepening MTD-bi; menghasilkan
        (kedalaman, gamma, skor, langkah) tiap probe."""
        self.nodes, self.riwayat = 0, set(riwayat)
        self.tp_skor = {}
        pos = self.akar = riwayat[-1]
        # Ratu hilang dari papan -> raja boleh ke tengah.
        mesin.PST["K"] = mesin.RAJA_TENGAH if (
            "Q" in pos.papan and "q" in pos.papan) \
            else mesin.RAJA_AKHIR
        gamma = 0
        for kedalaman in range(1, 1000):
            bawah, atas = 1 - MATE_ATAS, MATE_ATAS
            while bawah < atas - KERAS_MATE:
                skor = self.bound(pos, gamma, kedalaman, akar=True)
                if skor >= gamma:
                    bawah = skor
                if skor < gamma:
                    atas = skor
                yield kedalaman, gamma, skor, self.tp_langkah.get(pos)
                gamma = (bawah + atas + 1) // 2
            if time.time() > self.lembut:
                return

    def pilih(self, pos, kedalaman, riwayat=None):
        """Langkah terbaik pada kedalaman tetap —
        pembungkus cari() untuk uji dan permainan."""
        self.lembut = time.time() + 3600
        self.tenggat = time.time() + 3600
        hist = list(riwayat) if riwayat else [pos]
        hasil = None
        for d, _g, skor, langkah in self.cari(hist):
            if d == kedalaman and langkah is not None:
                hasil = (skor, langkah)
            if d > kedalaman:
                break
        return hasil
