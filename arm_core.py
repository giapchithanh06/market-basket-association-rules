"""
arm_core.py — Cài đặt ba thuật toán khai phá luật kết hợp.

Dùng cho tiểu luận "Kỹ thuật luật kết hợp và các thuật toán khai phá luật kết hợp".
Chỉ phụ thuộc thư viện chuẩn của Python, không cần mlxtend.

Nội dung:
    - apriori(...)    : thuật toán Apriori (Agrawal & Srikant, VLDB 1994)
    - fp_growth(...)  : thuật toán FP-Growth (Han, Pei & Yin, SIGMOD 2000)
    - eclat(...)      : thuật toán ECLAT (Zaki, IEEE TKDE 2000)
    - sinh_luat(...)  : sinh luật kết hợp kèm support, confidence, lift, leverage
    - goi_y_mua_kem(...) : gợi ý mặt hàng mua kèm từ tập luật
"""

from collections import defaultdict
from itertools import combinations
import time


# ---------------------------------------------------------------- tiện ích
def dem_ho_tro(itemset, D):
    """Số giao dịch trong D có chứa itemset."""
    s = set(itemset)
    return sum(1 for t in D if s <= t)


def chuan_hoa(D):
    """Đưa danh sách giao dịch về danh sách các set."""
    return [set(t) for t in D]


# ---------------------------------------------------------------- APRIORI
def apriori_gen(Lk, k):
    """Sinh ứng viên (k+1) phần tử từ Lk: bước kết nối + bước tỉa."""
    Lk_set = set(Lk)
    Ck1 = set()
    for a, b in combinations(sorted(Lk), 2):
        if a[: k - 1] == b[: k - 1] and a[k - 1] < b[k - 1]:        # join
            cand = tuple(sorted(set(a) | set(b)))
            if all(tuple(sorted(sub)) in Lk_set                      # prune
                   for sub in combinations(cand, k)):
                Ck1.add(cand)
    return sorted(Ck1)


def apriori(D, minsup, ghi_nhat_ky=False):
    """
    Khai phá tập phổ biến bằng Apriori.
    Trả về (freq, nhat_ky) với freq = {itemset(tuple): support(float)}.
    """
    D = chuan_hoa(D)
    N = len(D)
    min_count = minsup * N
    nhat_ky = []

    items = sorted({i for t in D for i in t})
    L = [(i,) for i in items if dem_ho_tro((i,), D) >= min_count]
    freq = {fs: dem_ho_tro(fs, D) / N for fs in L}
    if ghi_nhat_ky:
        nhat_ky.append(f"C1: {len(items)} ứng viên → L1: {len(L)} tập phổ biến")

    k = 1
    while L:
        C = apriori_gen(L, k)
        L_moi = []
        for c in C:
            if dem_ho_tro(c, D) >= min_count:
                L_moi.append(c)
                freq[c] = dem_ho_tro(c, D) / N
        if ghi_nhat_ky and C:
            nhat_ky.append(
                f"C{k+1}: {len(C)} ứng viên → L{k+1}: {len(L_moi)} tập phổ biến")
        L = L_moi
        k += 1
    return freq, nhat_ky


# ---------------------------------------------------------------- FP-GROWTH
class _Node:
    __slots__ = ("item", "count", "parent", "children")

    def __init__(self, item, parent):
        self.item, self.parent = item, parent
        self.count, self.children = 0, {}


def _dung_cay(giao_dich_da_sap, header):
    root = _Node(None, None)
    for t, c in giao_dich_da_sap:
        cur = root
        for it in t:
            if it not in cur.children:
                cur.children[it] = _Node(it, cur)
                header[it].append(cur.children[it])
            cur = cur.children[it]
            cur.count += c
    return root


def _khai_pha(header, rank, min_count, hau_to, ket_qua):
    # duyệt bảng đầu mục theo thứ tự support tăng dần (mục hiếm trước)
    for item in sorted(header, key=lambda i: -rank[i]):
        mau = tuple(sorted((item,) + hau_to))
        sup = sum(n.count for n in header[item])
        if sup < min_count:
            continue
        ket_qua[mau] = sup

        # cơ sở mẫu có điều kiện
        co_so = []
        for node in header[item]:
            duong_di, p = [], node.parent
            while p.item is not None:
                duong_di.append(p.item)
                p = p.parent
            if duong_di:
                co_so.append((list(reversed(duong_di)), node.count))

        # đếm lại trong phạm vi có điều kiện, loại mục không đạt ngưỡng
        dem = defaultdict(int)
        for duong_di, c in co_so:
            for x in duong_di:
                dem[x] += c
        giu = {x for x, v in dem.items() if v >= min_count}
        if not giu:
            continue

        cond = [([x for x in dd if x in giu], c) for dd, c in co_so]
        cond = [(dd, c) for dd, c in cond if dd]
        if not cond:
            continue

        header_con = defaultdict(list)
        _dung_cay(cond, header_con)
        _khai_pha(header_con, rank, min_count, mau, ket_qua)


def fp_growth(D, minsup):
    """Khai phá tập phổ biến bằng FP-Growth. Trả về {itemset: support}."""
    D = chuan_hoa(D)
    N = len(D)
    min_count = minsup * N

    dem = defaultdict(int)
    for t in D:
        for i in t:
            dem[i] += 1
    f1 = {i: c for i, c in dem.items() if c >= min_count}
    thu_tu = sorted(f1, key=lambda i: (-f1[i], i))          # F-list
    rank = {it: n for n, it in enumerate(thu_tu)}

    giao_dich = []
    for t in D:
        loc = sorted([i for i in t if i in f1], key=lambda i: rank[i])
        if loc:
            giao_dich.append((loc, 1))

    header = defaultdict(list)
    _dung_cay(giao_dich, header)

    ket_qua = {}
    _khai_pha(header, rank, min_count, tuple(), ket_qua)
    return {k: v / N for k, v in ket_qua.items()}


def fp_tree_text(D, minsup, max_dong=40):
    """Vẽ FP-tree dạng văn bản để minh họa trên giao diện."""
    D = chuan_hoa(D)
    N = len(D)
    min_count = minsup * N
    dem = defaultdict(int)
    for t in D:
        for i in t:
            dem[i] += 1
    f1 = {i: c for i, c in dem.items() if c >= min_count}
    if not f1:
        return "(không có mục nào đạt ngưỡng minsup)"
    thu_tu = sorted(f1, key=lambda i: (-f1[i], i))
    rank = {it: n for n, it in enumerate(thu_tu)}

    giao_dich = [(sorted([i for i in t if i in f1], key=lambda i: rank[i]), 1)
                 for t in D]
    giao_dich = [(t, c) for t, c in giao_dich if t]
    root = _dung_cay(giao_dich, defaultdict(list))

    dong = ["root"]

    def ve(node, muc):
        if len(dong) >= max_dong:
            return
        for it in sorted(node.children, key=lambda x: rank[x]):
            ch = node.children[it]
            dong.append("   " * muc + f"|-- {it}: {ch.count}")
            ve(ch, muc + 1)

    ve(root, 1)
    if len(dong) >= max_dong:
        dong.append("... (cây quá lớn, chỉ hiển thị một phần)")
    return "\n".join(dong)


# ---------------------------------------------------------------- ECLAT
def eclat(D, minsup):
    """Khai phá tập phổ biến bằng ECLAT (biểu diễn dọc). Trả về {itemset: support}."""
    D = chuan_hoa(D)
    N = len(D)
    min_count = minsup * N

    tid = defaultdict(set)
    for idx, t in enumerate(D):
        for i in t:
            tid[i].add(idx)

    P = [((i,), s) for i, s in tid.items() if len(s) >= min_count]
    P.sort()
    ket_qua = {}

    def de_quy(P):
        for idx, (Xi, ti) in enumerate(P):
            ket_qua[Xi] = len(ti) / N
            P_con = []
            for Xj, tj in P[idx + 1:]:
                giao = ti & tj
                if len(giao) >= min_count:
                    P_con.append((tuple(sorted(set(Xi) | set(Xj))), giao))
            if P_con:
                de_quy(P_con)

    de_quy(P)
    return ket_qua


# ---------------------------------------------------------------- SINH LUẬT
def sinh_luat(freq, minconf):
    """
    Sinh luật X -> Y từ tập phổ biến.
    Trả về danh sách dict: tien_de, ket_luan, support, confidence, lift, leverage.
    """
    luat = []
    for fs, sup_fs in freq.items():
        if len(fs) < 2:
            continue
        for r in range(1, len(fs)):
            for ante in combinations(sorted(fs), r):
                cons = tuple(sorted(set(fs) - set(ante)))
                sup_a, sup_c = freq.get(ante), freq.get(cons)
                if not sup_a or not sup_c:
                    continue
                conf = sup_fs / sup_a
                if conf < minconf:
                    continue
                luat.append({
                    "tien_de": ", ".join(ante),
                    "ket_luan": ", ".join(cons),
                    "support": round(sup_fs, 4),
                    "confidence": round(conf, 4),
                    "lift": round(sup_fs / (sup_a * sup_c), 4),
                    "leverage": round(sup_fs - sup_a * sup_c, 4),
                    "_ante": set(ante),
                    "_cons": set(cons),
                })
    luat.sort(key=lambda x: (-x["confidence"], -x["lift"]))
    return luat


def goi_y_mua_kem(gio_hang, luat, so_luong=5):
    """
    Gợi ý mặt hàng mua kèm: lấy các luật có tiền đề nằm trọn trong giỏ hàng,
    kết luận chưa có trong giỏ, xếp hạng theo lift rồi tới confidence.
    """
    gio = set(gio_hang)
    if not gio:
        return []
    ung_vien = {}
    for r in luat:
        if r["_ante"] <= gio and not (r["_cons"] & gio):
            for mh in r["_cons"]:
                cu = ung_vien.get(mh)
                if cu is None or (r["lift"], r["confidence"]) > (cu["lift"], cu["confidence"]):
                    ung_vien[mh] = {
                        "mat_hang": mh,
                        "lift": r["lift"],
                        "confidence": r["confidence"],
                        "support": r["support"],
                        "luat": f'{{{r["tien_de"]}}} → {{{r["ket_luan"]}}}',
                    }
    kq = sorted(ung_vien.values(),
                key=lambda x: (-x["lift"], -x["confidence"]))
    return kq[:so_luong]


# ---------------------------------------------------------------- ĐO TỐC ĐỘ
def do_toc_do(D, minsup):
    """Chạy thật cả ba thuật toán và đo thời gian. Không có số liệu dựng sẵn."""
    kq = []
    for ten, ham in (("Apriori", lambda d, m: apriori(d, m)[0]),
                     ("FP-Growth", fp_growth),
                     ("ECLAT", eclat)):
        t0 = time.perf_counter()
        freq = ham(D, minsup)
        t1 = time.perf_counter()
        kq.append({
            "Thuật toán": ten,
            "Số tập phổ biến": len(freq),
            "Thời gian (giây)": round(t1 - t0, 4),
        })
    return kq


# ---------------------------------------------------------------- DỮ LIỆU MẪU
DU_LIEU_CHUONG_3 = [
    ["Bánh mì", "Sữa"],
    ["Bánh mì", "Bia", "Bỉm", "Trứng"],
    ["Sữa", "Bia", "Bỉm", "Coca"],
    ["Bánh mì", "Sữa", "Bia", "Bỉm"],
    ["Bánh mì", "Sữa", "Bia", "Coca"],
    ["Sữa", "Bia", "Bỉm"],
]


# ---------------------------------------------------------------- TỰ KIỂM TRA
if __name__ == "__main__":
    D = DU_LIEU_CHUONG_3
    freq_a, nk = apriori(D, 0.5, ghi_nhat_ky=True)
    freq_f = fp_growth(D, 0.5)
    freq_e = eclat(D, 0.5)
    luat = sinh_luat(freq_a, 0.7)

    print("Nhật ký Apriori:")
    for d in nk:
        print("   ", d)
    print("Apriori   :", len(freq_a), "tập phổ biến")
    print("FP-Growth :", len(freq_f), "tập phổ biến")
    print("ECLAT     :", len(freq_e), "tập phổ biến")
    print("Ba thuật toán cho cùng kết quả:",
          set(freq_a) == set(freq_f) == set(freq_e))
    print("Số luật đạt minconf = 0,7:", len(luat))
    for r in luat[:3]:
        print(f'   {{{r["tien_de"]}}} -> {{{r["ket_luan"]}}} '
              f'conf={r["confidence"]} lift={r["lift"]}')
    print("\nGợi ý khi giỏ hàng có Bỉm:")
    for g in goi_y_mua_kem(["Bỉm"], luat):
        print("   ", g["mat_hang"], "lift =", g["lift"])
