"""
app_goi_y_mua_kem.py — Ứng dụng demo khai phá luật kết hợp và gợi ý mua kèm.

Chạy:  streamlit run app_goi_y_mua_kem.py
Yêu cầu: pip install streamlit pandas

Ứng dụng minh họa cho tiểu luận "Kỹ thuật luật kết hợp và các thuật toán
khai phá luật kết hợp". Ba thuật toán Apriori, FP-Growth, ECLAT đều được tự
cài đặt trong arm_core.py, không dùng thư viện khai phá bên ngoài.
"""

import collections
import csv
import io

import pandas as pd
import streamlit as st

import arm_core as core

st.set_page_config(page_title="Demo luật kết hợp — Gợi ý mua kèm",
                   page_icon="🛒", layout="wide")


# ----------------------------------------------------------------- dữ liệu
def doc_csv(noi_dung: str):
    """
    Đọc CSV thành danh sách giao dịch. Hỗ trợ hai định dạng:
      (a) 2 cột: MaHoaDon, MatHang  → nhóm theo mã hóa đơn
      (b) 1 cột : mỗi dòng là một giao dịch, các mặt hàng cách nhau bởi dấu phẩy
    """
    dong = [d for d in noi_dung.splitlines() if d.strip()]
    if not dong:
        return []
    mau = csv.reader(io.StringIO("\n".join(dong[:5])))
    so_cot = max(len(r) for r in mau)

    if so_cot >= 2:
        reader = csv.reader(io.StringIO("\n".join(dong)))
        rows = list(reader)
        dau = [c.strip().lower().lstrip("\ufeff") for c in rows[0]]
        if any(k in dau[0] for k in ("ma", "invoice", "id", "hoa")):
            rows = rows[1:]
        nhom = collections.defaultdict(set)
        for r in rows:
            if len(r) >= 2 and r[0].strip() and r[1].strip():
                nhom[r[0].strip()].add(r[1].strip())
        return [sorted(v) for v in nhom.values()]

    gd = []
    for d in dong:
        mh = [x.strip() for x in d.replace(";", ",").split(",") if x.strip()]
        if mh:
            gd.append(sorted(set(mh)))
    return gd


@st.cache_data(show_spinner=False)
def khai_pha(D_tuple, minsup, thuat_toan):
    D = [list(t) for t in D_tuple]
    if thuat_toan == "Apriori":
        freq, nhat_ky = core.apriori(D, minsup, ghi_nhat_ky=True)
    elif thuat_toan == "FP-Growth":
        freq, nhat_ky = core.fp_growth(D, minsup), []
    else:
        freq, nhat_ky = core.eclat(D, minsup), []
    return freq, nhat_ky


# ----------------------------------------------------------------- sidebar
st.sidebar.header("⚙️ Thiết lập")

nguon = st.sidebar.radio(
    "Nguồn dữ liệu",
    ["Ví dụ Chương 3 (6 giao dịch)", "Dữ liệu mô phỏng (365 giao dịch)",
     "Tải lên file CSV"],
)

D = []
ghi_chu_nguon = ""
if nguon.startswith("Ví dụ"):
    D = [list(t) for t in core.DU_LIEU_CHUONG_3]
    ghi_chu_nguon = ("Cơ sở dữ liệu minh họa trong Chương 3 của tiểu luận. "
                     "Với minsup = 50% và minconf = 70%, kết quả đúng phải là "
                     "10 tập phổ biến và 11 luật.")
elif nguon.startswith("Dữ liệu mô phỏng"):
    try:
        with open("du_lieu_mo_phong.csv", encoding="utf-8-sig") as f:
            D = doc_csv(f.read())
        ghi_chu_nguon = ("Dữ liệu SINH NGẪU NHIÊN có chủ đích bằng "
                         "tao_du_lieu_mo_phong.py, KHÔNG phải dữ liệu bán lẻ "
                         "thật. Chỉ dùng để minh họa giao diện và cách hoạt "
                         "động của thuật toán.")
    except FileNotFoundError:
        st.sidebar.error("Chưa có du_lieu_mo_phong.csv. "
                         "Chạy: python tao_du_lieu_mo_phong.py")
else:
    up = st.sidebar.file_uploader("Chọn file CSV", type=["csv", "txt"])
    if up is not None:
        D = doc_csv(up.getvalue().decode("utf-8-sig", errors="replace"))
        ghi_chu_nguon = f"Dữ liệu do người dùng tải lên: {up.name}"
    else:
        st.sidebar.caption(
            "Định dạng chấp nhận:\n\n"
            "• 2 cột `MaHoaDon, MatHang`\n\n"
            "• hoặc mỗi dòng một giao dịch, mặt hàng cách nhau bởi dấu phẩy")

minsup = st.sidebar.slider("minsup — ngưỡng hỗ trợ tối thiểu",
                           0.01, 1.0, 0.5, 0.01)
minconf = st.sidebar.slider("minconf — ngưỡng tin cậy tối thiểu",
                            0.05, 1.0, 0.7, 0.05)
thuat_toan = st.sidebar.selectbox("Thuật toán khai phá tập phổ biến",
                                  ["Apriori", "FP-Growth", "ECLAT"])

st.sidebar.caption("Ba thuật toán luôn cho cùng tập kết quả; chúng chỉ khác "
                   "nhau về cách duyệt không gian tìm kiếm.")

# ----------------------------------------------------------------- nội dung
st.title("🛒 Khai phá luật kết hợp & gợi ý mua kèm")
st.caption("Ứng dụng demo cho tiểu luận *Kỹ thuật luật kết hợp và các thuật "
           "toán khai phá luật kết hợp*")

if not D:
    st.info("Hãy chọn nguồn dữ liệu ở thanh bên trái để bắt đầu.")
    st.stop()

with st.spinner("Đang khai phá..."):
    freq, nhat_ky = khai_pha(tuple(tuple(t) for t in D), minsup, thuat_toan)
    luat = core.sinh_luat(freq, minconf)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Số giao dịch", len(D))
c2.metric("Số mặt hàng", len({i for t in D for i in t}))
c3.metric("Tập phổ biến", len(freq))
c4.metric("Luật đạt ngưỡng", len(luat))

tab_dl, tab_tap, tab_luat, tab_goiy, tab_ss, tab_gt = st.tabs(
    ["📦 Dữ liệu", "🔎 Tập phổ biến", "📐 Luật kết hợp",
     "🛍️ Gợi ý mua kèm", "⏱️ So sánh tốc độ", "ℹ️ Giới thiệu"])

# --- tab dữ liệu
with tab_dl:
    st.info(ghi_chu_nguon)
    df_gd = pd.DataFrame({
        "Mã giao dịch": [f"T{i+1}" for i in range(len(D))],
        "Số mặt hàng": [len(t) for t in D],
        "Danh sách mặt hàng": [", ".join(t) for t in D],
    })
    st.dataframe(df_gd, use_container_width=True, hide_index=True)

    dem = collections.Counter(i for t in D for i in t)
    df_item = pd.DataFrame(
        [{"Mặt hàng": k, "Số giao dịch": v, "Support": round(v / len(D), 4)}
         for k, v in dem.most_common()])
    st.subheader("Tần suất từng mặt hàng")
    st.dataframe(df_item, use_container_width=True, hide_index=True)

# --- tab tập phổ biến
with tab_tap:
    if nhat_ky:
        st.subheader("Nhật ký sinh ứng viên của Apriori")
        for d in nhat_ky:
            st.text("   " + d)

    if freq:
        kich_co = sorted({len(k) for k in freq})
        chon = st.multiselect("Lọc theo số phần tử của tập mục",
                              kich_co, default=kich_co)
        df_f = pd.DataFrame(
            [{"Số phần tử": len(k), "Tập mục": "{" + ", ".join(k) + "}",
              "Support": round(v, 4), "Số giao dịch": round(v * len(D))}
             for k, v in sorted(freq.items(), key=lambda x: (len(x[0]), -x[1]))
             if len(k) in chon])
        st.dataframe(df_f, use_container_width=True, hide_index=True)
    else:
        st.warning("Không có tập mục nào đạt ngưỡng minsup. Hãy giảm minsup.")

    if thuat_toan == "FP-Growth":
        st.subheader("FP-tree (dạng văn bản)")
        st.code(core.fp_tree_text(D, minsup), language="text")

# --- tab luật
with tab_luat:
    if luat:
        df_l = pd.DataFrame([{
            "Luật": f'{{{r["tien_de"]}}} → {{{r["ket_luan"]}}}',
            "Support": r["support"], "Confidence": r["confidence"],
            "Lift": r["lift"], "Leverage": r["leverage"],
        } for r in luat])

        sap_xep = st.radio("Sắp xếp theo", ["Confidence", "Lift", "Support"],
                           horizontal=True)
        chi_lift = st.checkbox("Chỉ hiện luật có lift > 1 (tương quan dương)")
        if chi_lift:
            df_l = df_l[df_l["Lift"] > 1]
        df_l = df_l.sort_values(sap_xep, ascending=False)
        st.dataframe(df_l, use_container_width=True, hide_index=True)

        st.download_button("⬇️ Tải danh sách luật (CSV)",
                           df_l.to_csv(index=False).encode("utf-8-sig"),
                           "luat_ket_hop.csv", "text/csv")

        so_lift_thap = int((pd.DataFrame(luat)["lift"] <= 1).sum())
        if so_lift_thap:
            st.warning(
                f"Có {so_lift_thap} luật đạt ngưỡng confidence nhưng lift ≤ 1. "
                "Những luật này không mang thông tin: vế phải vốn đã phổ biến "
                "nên confidence cao là điều hiển nhiên (xem mục 1.7.1 của "
                "tiểu luận).")
    else:
        st.warning("Không có luật nào đạt ngưỡng. Hãy giảm minsup hoặc minconf.")

# --- tab gợi ý
with tab_goiy:
    st.subheader("Thử vai người mua hàng")
    tat_ca = sorted({i for t in D for i in t})
    gio = st.multiselect("Giỏ hàng hiện tại", tat_ca)
    so_luong = st.slider("Số gợi ý tối đa", 1, 10, 5)

    if not gio:
        st.info("Chọn một vài mặt hàng để xem hệ thống gợi ý mua kèm.")
    else:
        gy = core.goi_y_mua_kem(gio, luat, so_luong)
        if not gy:
            st.warning("Chưa có gợi ý nào. Nguyên nhân thường gặp: ngưỡng "
                       "minsup/minconf đang quá cao, hoặc tổ hợp trong giỏ "
                       "hàng không xuất hiện đủ nhiều trong dữ liệu.")
        else:
            st.success(f"Gợi ý {len(gy)} mặt hàng nên mua kèm:")
            st.dataframe(pd.DataFrame([{
                "Mặt hàng gợi ý": g["mat_hang"], "Lift": g["lift"],
                "Confidence": g["confidence"], "Support": g["support"],
                "Dựa trên luật": g["luat"],
            } for g in gy]), use_container_width=True, hide_index=True)
            st.caption("Gợi ý được xếp hạng theo lift trước, confidence sau — "
                       "để tránh ưu tiên nhầm những mặt hàng vốn đã bán chạy.")

# --- tab so sánh
with tab_ss:
    st.subheader("So sánh ba thuật toán trên chính dữ liệu đang chọn")
    st.caption("Bấm nút để chạy thật cả ba thuật toán và đo thời gian. "
               "Ứng dụng không hiển thị bất kỳ số liệu dựng sẵn nào.")
    if st.button("▶️ Chạy đo"):
        with st.spinner("Đang chạy cả ba thuật toán..."):
            kq = core.do_toc_do(D, minsup)
        st.dataframe(pd.DataFrame(kq), use_container_width=True,
                     hide_index=True)
        st.caption(
            "Lưu ý khi đọc kết quả: đây là cài đặt phục vụ minh họa, viết "
            "bằng Python thuần và ưu tiên tính dễ đọc hơn tốc độ. Thời gian đo "
            "được chỉ phản ánh ba cài đặt cụ thể này trên tập dữ liệu này, "
            "không phải kết luận tổng quát về hiệu năng của ba thuật toán.")

# --- tab giới thiệu
with tab_gt:
    st.markdown("""
### Ứng dụng này làm gì

1. Đọc cơ sở dữ liệu giao dịch (dữ liệu mẫu hoặc file CSV bạn tải lên).
2. Khai phá **tập mục phổ biến** bằng một trong ba thuật toán: Apriori,
   FP-Growth hoặc ECLAT — cả ba đều được tự cài đặt trong `arm_core.py`.
3. Sinh **luật kết hợp** kèm bốn độ đo: support, confidence, lift, leverage.
4. **Gợi ý mua kèm** dựa trên tập luật, xếp hạng theo lift.
5. Chạy thật và **đo thời gian** cả ba thuật toán để so sánh.

### Kiểm chứng tính đúng đắn

Chọn nguồn *Ví dụ Chương 3*, đặt minsup = 0,50 và minconf = 0,70. Kết quả phải
là **10 tập phổ biến** và **11 luật**, khớp với Bảng 3.5 và Bảng 3.9 trong tiểu
luận. Đổi thuật toán sang FP-Growth hoặc ECLAT, con số phải giữ nguyên.

### Công thức đang dùng

| Độ đo | Công thức |
|---|---|
| Support | support(X) = số giao dịch chứa X / tổng số giao dịch |
| Confidence | confidence(X→Y) = support(X ∪ Y) / support(X) |
| Lift | lift(X→Y) = support(X ∪ Y) / (support(X) × support(Y)) |
| Leverage | leverage(X→Y) = support(X ∪ Y) − support(X) × support(Y) |

### Nguồn thuật toán

- Apriori: R. Agrawal, R. Srikant, *Fast Algorithms for Mining Association
  Rules*, VLDB 1994, pp. 487–499.
- FP-Growth: J. Han, J. Pei, Y. Yin, *Mining Frequent Patterns without Candidate
  Generation*, SIGMOD 2000. doi:10.1145/342009.335372
- ECLAT: M. J. Zaki, *Scalable Algorithms for Association Mining*, IEEE TKDE
  12(3), 2000, pp. 372–390. doi:10.1109/69.846291
""")
