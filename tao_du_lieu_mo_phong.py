"""
tao_du_lieu_mo_phong.py — Sinh bộ dữ liệu giao dịch MÔ PHỎNG để chạy demo.

LƯU Ý: đây là dữ liệu sinh ngẫu nhiên có chủ đích (không phải dữ liệu bán lẻ
thật). Dùng để minh họa giao diện và cách hoạt động của thuật toán. Khi cần số
liệu thực nghiệm cho báo cáo, hãy dùng bộ Online Retail của UCI
(doi:10.24432/C5BW33) như đã ghi ở Chương 4.

Cách chạy:  python tao_du_lieu_mo_phong.py
Kết quả  :  du_lieu_mo_phong.csv  (cột MaHoaDon, MatHang)
"""

import csv
import random

random.seed(20260922)          # cố định để kết quả tái lập được

CATALOG = [
    "Bánh mì", "Sữa tươi", "Trứng gà", "Bơ lạt", "Mứt dâu",
    "Bỉm em bé", "Sữa bột", "Khăn ướt", "Bia lon", "Snack khoai tây",
    "Nước ngọt", "Cà phê gói", "Đường trắng", "Mì gói", "Xúc xích",
    "Rau xà lách", "Cà chua", "Dầu ăn", "Nước mắm", "Gạo 5kg",
]

# Các "nhóm mua kèm" được cài vào dữ liệu để thuật toán có gì để tìm ra
NHOM = [
    (["Bánh mì", "Bơ lạt", "Mứt dâu"], 0.22),
    (["Bỉm em bé", "Sữa bột", "Khăn ướt"], 0.20),
    (["Bia lon", "Snack khoai tây", "Xúc xích"], 0.18),
    (["Cà phê gói", "Đường trắng", "Sữa tươi"], 0.17),
    (["Mì gói", "Trứng gà", "Xúc xích"], 0.15),
    (["Rau xà lách", "Cà chua", "Dầu ăn"], 0.14),
    (["Gạo 5kg", "Nước mắm", "Dầu ăn"], 0.12),
]

SO_GIAO_DICH = 400


def sinh():
    giao_dich = []
    for _ in range(SO_GIAO_DICH):
        gio = set()
        for nhom, p in NHOM:
            if random.random() < p:
                # lấy phần lớn (không phải luôn luôn) các món trong nhóm
                for mh in nhom:
                    if random.random() < 0.85:
                        gio.add(mh)
        # thêm vài món mua lẻ ngẫu nhiên
        for mh in random.sample(CATALOG, random.randint(0, 3)):
            gio.add(mh)
        if gio:
            giao_dich.append(sorted(gio))
    return giao_dich


if __name__ == "__main__":
    gd = sinh()
    with open("du_lieu_mo_phong.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["MaHoaDon", "MatHang"])
        for i, t in enumerate(gd, 1):
            for mh in t:
                w.writerow([f"HD{i:04d}", mh])
    print(f"Đã ghi du_lieu_mo_phong.csv: {len(gd)} giao dịch, "
          f"{sum(len(t) for t in gd)} dòng, {len(CATALOG)} mặt hàng.")
