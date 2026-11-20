"""Inti mesin catur ala Sunfish: papan, langkah, nilai.

Ditulis ulang sebagai latihan belajar mengikuti
arsitektur Sunfish karya Thomas Dybdahl Ahle
(GPL v3, github.com/thomasahle/sunfish):

- Papan adalah string 120 karakter (10x12) — bantalan
  di sekeliling 8x8 membuat deteksi keluar-papan cukup
  dengan memeriksa karakter.
- Posisi SELALU dari sudut pandang pihak yang akan
  bergerak: bidak kita huruf besar di bawah, dan tiap
  langkah diakhiri rotate() yang membalik papan.
- Generator langkah bersifat pseudo-sah. Kesahan
  muncul dari model tangkap-raja: sebuah langkah sah
  bila sesudah dimainkan, lawan tidak dapat menangkap
  raja kita. Rokade dan en passant yang "ilegal"
  tersaring oleh mekanisme yang sama.
- Skor posisi diperbarui inkremental oleh value():
  tidak ada evaluasi ulang dari nol di dalam pencarian.
"""

from collections import namedtuple
from itertools import count

# ---------- Tabel petak-bidak (piece-square tables) ----------
# Nilai dasar tiap bidak + bonus per petak. Tabel milik
# Sunfish (hasil tuning penulisnya); baris pertama tiap
# tabel adalah baris 8 dari sudut pandang Putih.

NILAI = {"P": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 60000}
PST_MENTAH = {
    'P': (   0,   0,   0,   0,   0,   0,   0,   0,
            78,  83,  86,  73, 102,  82,  85,  90,
             7,  29,  21,  44,  40,  31,  44,   7,
           -17,  16,  -2,  15,  14,   0,  15, -13,
           -26,   3,  10,   9,   6,   1,   0, -23,
           -22,   9,   5, -11, -10,  -2,   3, -19,
           -31,   8,  -7, -37, -36, -14,   3, -31,
             0,   0,   0,   0,   0,   0,   0,   0),
    'N': ( -66, -53, -75, -75, -10, -55, -58, -70,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
            10,  67,   1,  74,  73,  27,  62,  -2,
            24,  24,  45,  37,  33,  41,  25,  17,
            -1,   5,  31,  21,  22,  35,   2,   0,
           -18,  10,  13,  22,  18,  15,  11, -14,
           -23, -15,   2,   0,   2,   0, -23, -20,
           -74, -23, -26, -24, -19, -35, -22, -69),
    'B': ( -59, -78, -82, -76, -23,-107, -37, -50,
           -11,  20,  35, -42, -39,  31,   2, -22,
            -9,  39, -32,  41,  52, -10,  28, -14,
            25,  17,  20,  34,  26,  25,  15,  10,
            13,  10,  17,  23,  17,  16,   0,   7,
            14,  25,  24,  15,   8,  25,  20,  15,
            19,  20,  11,   6,   7,   6,  20,  16,
            -7,   2, -15, -12, -14, -15, -10, -10),
    'R': (  35,  29,  33,   4,  37,  33,  56,  50,
            55,  29,  56,  67,  55,  62,  34,  60,
            19,  35,  28,  33,  45,  27,  25,  15,
             0,   5,  16,  13,  18,  -4,  -9,  -6,
           -28, -35, -16, -21, -13, -29, -46, -30,
           -42, -28, -42, -25, -25, -35, -26, -46,
           -53, -38, -31, -26, -29, -43, -44, -53,
           -30, -24, -18,   5,  -2, -18, -31, -32),
    'Q': (   6,   1,  -8,-104,  69,  24,  88,  26,
            14,  32,  60, -10,  20,  76,  57,  24,
            -2,  43,  32,  60,  72,  63,  43,   2,
             1, -16,  22,  17,  25,  20, -13,  -6,
           -14, -15,  -2,  -5,  -1, -10, -20, -22,
           -30,  -6, -13, -11, -16, -11, -16, -27,
           -36, -18,   0, -19, -15, -15, -21, -38,
           -39, -30, -31, -13, -31, -36, -34, -42),
    'K': (   4,  54,  47, -99, -99,  60,  83, -62,
           -32,  10,  55,  56,  56,  55,  10,   3,
           -62,  12, -57,  44, -67,  28,  37, -31,
           -55,  50,  11,  -4, -19,  13,   0, -49,
           -55, -43, -52, -28, -51, -47,  -8, -50,
           -47, -42, -43, -79, -64, -32, -29, -32,
            -4,   3, -14, -50, -57, -18,  13,   4,
            17,  30,  -3, -14,   6,  -1,  40,  18),
}


def _bantalan(tabel, bidak):
    """64 nilai -> 120 nilai sejajar indeks papan:
    tiap baris dibungkus 0 di kiri-kanan, nilai dasar
    bidak ditambahkan, dan 20 nol di kedua ujung."""
    baris = [(0,) + tuple(x + NILAI[bidak]
                          for x in tabel[i * 8:i * 8 + 8]) + (0,)
             for i in range(8)]
    return (0,) * 20 + tuple(v for b in baris for v in b) + (0,) * 20


PST = {k: _bantalan(t, k) for k, t in PST_MENTAH.items()}

# Tabel raja akhir permainan: mendorong raja ke tengah.
# Cukup untuk memenangkan akhir permainan KRK dan KQK.
RAJA_TENGAH = PST["K"]
RAJA_AKHIR = tuple(NILAI["K"] + 70 - 10 * (abs(2 * (i // 10) - 11)
                                           + abs(2 * (i % 10) - 9))
                   for i in range(120))

# ---------- Konstanta papan ----------

A1, H1, A8, H8 = 91, 98, 21, 28
PAPAN_AWAL = (
    "         \n"  #   0 -  9
    "         \n"  #  10 - 19
    " rnbqkbnr\n"  #  20 - 29
    " pppppppp\n"  #  30 - 39
    " ........\n"  #  40 - 49
    " ........\n"  #  50 - 59
    " ........\n"  #  60 - 69
    " ........\n"  #  70 - 79
    " PPPPPPPP\n"  #  80 - 89
    " RNBQKBNR\n"  #  90 - 99
    "         \n"  # 100 -109
    "         \n"  # 110 -119
)

# Arah gerak: Utara, Timur, Selatan, Barat dalam indeks.
U, T, S, B = -10, 1, 10, -1
ARAH = {
    "P": (U, U + U, U + B, U + T),
    "N": (U + U + T, T + U + T, T + S + T, S + S + T,
          S + S + B, B + S + B, B + U + B, U + U + B),
    "B": (U + T, S + T, S + B, U + B),
    "R": (U, T, S, B),
    "Q": (U, T, S, B, U + T, S + T, S + B, U + B),
    "K": (U, T, S, B, U + T, S + T, S + B, U + B),
}

# Nilai mate: raja bernilai jauh di atas semua kombinasi
# materi, sehingga menangkap raja selalu "menang".
MATE_BAWAH = NILAI["K"] - 13 * NILAI["Q"]
MATE_ATAS = NILAI["K"] + 10 * NILAI["Q"]

# Jangkar skor: jumlah PST naif posisi awal = 38, tetapi
# skor permainan didefinisikan 0 di sana. Selisihnya
# konstan (membalik tanda tiap ply) di sepanjang
# permainan; lihat dari_fen() dan CATATAN irisan 3.
JANGKAR_SKOR = 38

Langkah = namedtuple("Langkah", "i j prom")


class Posisi(namedtuple("Posisi", "papan skor wc bc ep kp")):
    """Keadaan permainan dari sudut pandang yang bergerak.

    papan -- string 120 karakter
    skor  -- evaluasi untuk pihak yang akan bergerak
    wc    -- hak rokade kita [sayap-raja-wanita, sayap-raja]
             dalam kerangka kita: [A1, H1]
    bc    -- hak rokade lawan dalam KERANGKA LAWAN
             sesudah dibalik: [H8 mutlak, A8 mutlak]
    ep    -- petak en passant (petak yang dilompati pion)
    kp    -- petak "king passant": petak singgah raja
             saat rokade, untuk deteksi rokade-kena-skak
    """

    def gen_moves(self):
        # Untuk tiap bidak kita, ikuti tiap sinar arah.
        # Sinar putus oleh bidak kawan / bantalan, dan
        # oleh tangkapan (kecuali bidak luncur).
        for i, p in enumerate(self.papan):
            if p not in "PNBRQK":
                continue
            for d in ARAH[p]:
                for j in count(i + d, d):
                    q = self.papan[j]
                    # Bantalan, di luar papan, bidak kawan
                    if q in " \nPNBRQK":
                        break
                    # Aturan pion
                    if p == "P":
                        if d in (U, U + U) and q != ".":
                            break
                        if d == U + U and (i < A1 + U
                                           or self.papan[i + U] != "."):
                            break
                        if d in (U + B, U + T) and q == "." \
                                and j != self.ep \
                                and abs(j - self.kp) > 1:
                            break
                        # Baris terakhir: promosi
                        if A8 <= j <= H8:
                            yield from (Langkah(i, j, prom)
                                        for prom in "NBRQ")
                            break
                    yield Langkah(i, j, "")
                    # Bidak non-luncur berhenti; luncur
                    # berhenti sesudah menangkap
                    if p in "PNK" or q in "pnbrqk":
                        break
                    # Rokade, dibangkitkan dari sinar benteng:
                    # benteng bergeser sampai di samping raja
                    if i == A1 and self.papan[j + T] == "K" and self.wc[0]:
                        yield Langkah(j + T, j + B, "")
                    if i == H1 and self.papan[j + B] == "K" and self.wc[1]:
                        yield Langkah(j + B, j + T, "")

    def rotate(self, langkah_nol=False):
        """Balik papan untuk pemain berikutnya.
        En passant gugur pada langkah nol."""
        return Posisi(self.papan[::-1].swapcase(), -self.skor,
                      self.bc, self.wc,
                      119 - self.ep if self.ep and not langkah_nol else 0,
                      119 - self.kp if self.kp and not langkah_nol else 0)

    def move(self, langkah):
        i, j, prom = langkah

        def taruh(papan, idx, p):
            return papan[:idx] + p + papan[idx + 1:]

        p, q = self.papan[i], self.papan[j]
        papan, wc, bc = self.papan, self.wc, self.bc
        skor = self.skor + self.value(langkah)
        ep = kp = 0
        # Langkah pokok
        papan = taruh(papan, j, papan[i])
        papan = taruh(papan, i, ".")
        # Hak rokade gugur bila benteng bergerak/ditangkap
        wc = (wc[0] and i != A1, wc[1] and i != H1)
        bc = (bc[0] and j != H8, bc[1] and j != A8)
        # Rokade: raja melompat dua petak, benteng menyusul
        if p == "K":
            wc = (False, False)
            if abs(j - i) == 2:
                kp = (i + j) // 2
                papan = taruh(papan, A1 if j < i else H1, ".")
                papan = taruh(papan, kp, "R")
        # Pion: promosi, langkah ganda, en passant
        if p == "P":
            if A8 <= j <= H8:
                papan = taruh(papan, j, prom)
            if j - i == 2 * U:
                ep = i + U
            if j == self.ep:
                papan = taruh(papan, j + S, ".")
        # Hasilnya dibalik, siap untuk pemain berikutnya
        return Posisi(papan, skor, wc, bc, ep, kp).rotate()

    def value(self, langkah):
        """Perubahan skor bila langkah dimainkan —
        satu-satunya tempat evaluasi terjadi."""
        i, j, prom = langkah
        p, q = self.papan[i], self.papan[j]
        skor = PST[p][j] - PST[p][i]
        # Tangkapan: bidak lawan dinilai di kerangka balik
        if q in "pnbrqk":
            skor += PST[q.upper()][119 - j]
        # Deteksi skak pada rokade: langkah yang mendarat
        # di dekat petak singgah raja bernilai tangkap-raja
        if abs(j - self.kp) < 2:
            skor += PST["K"][119 - j]
        # Rokade: benteng ikut berpindah
        if p == "K" and abs(i - j) == 2:
            skor += PST["R"][(i + j) // 2]
            skor -= PST["R"][A1 if j < i else H1]
        # Pion khusus
        if p == "P":
            if A8 <= j <= H8:
                skor += PST[prom][j] - PST["P"][j]
            if j == self.ep:
                skor += PST["P"][119 - (j + S)]
        return skor

    def tangkap_raja(self):
        """Langkah yang menangkap raja lawan, bila ada —
        bukti posisi ini dicapai lewat langkah tak sah.
        Dari posisi hasil rotate(langkah_nol), adanya
        langkah ini berarti pihak yang bergerak kena skak."""
        return next((m for m in self.gen_moves()
                     if self.papan[m.j] == "k"
                     or abs(m.j - self.kp) < 2), None)


def posisi_awal():
    return Posisi(PAPAN_AWAL, 0, (True, True), (True, True), 0, 0)


def parse_petak(teks):
    """'e2' -> indeks papan."""
    return A1 + ord(teks[0]) - ord("a") - 10 * (int(teks[1]) - 1)


def render_petak(i):
    """Indeks papan -> 'e2'."""
    return chr((i - A1) % 10 + ord("a")) + str(1 - (i - A1) // 10)


def dari_fen(fen):
    """FEN -> Posisi (tambahan untuk uji; hulu menerima
    FEN lewat modul UI-nya). Skor dihitung dari nol
    dengan PST yang sama, lalu DIJANGKARKAN: skor
    Sunfish adalah skor inkremental yang berawal dari
    0 di posisi awal, sedangkan jumlah PST naif
    F(posisi awal) = 38 (tabel tidak simetris cermin).
    Agar posisi FEN konsisten dengan posisi yang
    dicapai lewat permainan, kurangi 38 (dari sudut
    Putih) sebelum dibalik bila Hitam yang bergerak."""
    bagian = fen.split()
    baris = bagian[0].split("/")
    sisi = bagian[1] if len(bagian) > 1 else "w"
    rokade = bagian[2] if len(bagian) > 2 else "-"
    ep_teks = bagian[3] if len(bagian) > 3 else "-"
    papan = [" "] * 120
    for idx in range(120):
        r, c = divmod(idx, 10)
        papan[idx] = "\n" if c == 9 else " "
    skor = 0
    for rb, baris_teks in enumerate(baris):
        kolom = 0
        for ch in baris_teks:
            if ch.isdigit():
                for _ in range(int(ch)):
                    papan[21 + rb * 10 + kolom] = "."
                    kolom += 1
            else:
                idx = 21 + rb * 10 + kolom
                papan[idx] = ch
                if ch.isupper():
                    skor += PST[ch][idx]
                else:
                    skor -= PST[ch.upper()][119 - idx]
                kolom += 1
    papan = "".join(papan)
    skor -= JANGKAR_SKOR
    # Hak rokade: wc dalam kerangka yang bergerak;
    # bc lawan disimpan dalam kerangka lawan (dibalik):
    # bc[0] <-> benteng H8 (sayap raja Hitam),
    # bc[1] <-> benteng A8 (sayap wanita Hitam).
    wc = ("Q" in rokade, "K" in rokade)
    bc = ("k" in rokade, "q" in rokade)
    ep = parse_petak(ep_teks) if ep_teks != "-" else 0
    pos = Posisi(papan, skor, wc, bc, ep, 0)
    return pos if sisi == "w" else pos.rotate()


def skor_dari_nol(pos):
    """Jumlah PST naif F(pos) dari papan tersimpan —
    wasit konsistensi skor inkremental. Hubungannya:
    skor = F(pos) - JANGKAR_SKOR untuk posisi yang
    dicapai dari posisi awal dengan Putih bergerak
    (tanda jangkar membalik mengikuti kerangka)."""
    papan = pos.papan
    total = 0
    for idx, ch in enumerate(papan):
        if ch in "PNBRQK":
            total += PST[ch][idx]
        elif ch in "pnbrqk":
            total -= PST[ch.upper()][119 - idx]
    return total


def langkah_sah(pos):
    """Saring gen_moves menjadi langkah yang sah:
    sesudah dimainkan, raja sendiri tak tertangkap."""
    return [m for m in pos.gen_moves()
            if pos.move(m).tangkap_raja() is None]


def perft(pos, kedalaman):
    """Hitung daun pohon langkah sah — wasit baku
    kebenaran generator langkah."""
    if kedalaman == 0:
        return 1
    total = 0
    for m in pos.gen_moves():
        anak = pos.move(m)
        if anak.tangkap_raja() is not None:
            continue
        total += perft(anak, kedalaman - 1)
    return total
