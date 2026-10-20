"""app.py - Demo Streamlit: Nhận dạng thực thể tiếng Việt về COVID-19 (Đề 26 · PhoNER_COVID19).

Người phụ trách: Yến Trinh · Issue T30 (+ T37 triển khai, T40 viết báo cáo)
Chạy (máy cá nhân, VS Code):   streamlit run app/app.py
Mô hình: mỗi thư mục con trong app/mo_hinh/ là 1 mô hình đã fine-tune (tạo bởi notebook huấn luyện, ô "Lưu mô hình
cho demo"); hoặc đặt biến môi trường NER_MODEL = tên repo Hugging Face Hub.
"""

import io
import json
import os
import sys
import time

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ner_core import LOAI, MAU_CHU, BoTachTu, MoHinhNER, html_to_mau, nhan_dang  # noqa: E402

THU_MUC_MO_HINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mo_hinh")
VI_DU = {
    "Ca bệnh mới": "Bệnh nhân 1234 là nữ, 35 tuổi, nhân viên văn phòng, trú tại phường Bến Nghé, Quận 1, TP. Hồ Chí Minh. "
                   "Ngày 15/3/2020, bệnh nhân về nước trên chuyến bay VN0054 và có triệu chứng sốt, ho khan.",
    "Tiếp xúc gần": "Ông Nguyễn Văn An, 62 tuổi, là người tiếp xúc gần với bệnh nhân 418, hiện được cách ly tại "
                    "Bệnh viện Bệnh Nhiệt đới Trung ương cơ sở 2.",
    "Thông báo y tế": "Ngày 20/7, Sở Y tế Đà Nẵng thông báo bệnh nhân 416 có bệnh nền tiểu đường và suy thận, "
                      "đang điều trị tại Bệnh viện C Đà Nẵng.",
}

st.set_page_config(page_title="NER COVID-19 tiếng Việt", page_icon="🩺", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; max-width: 1200px;}
.ket-qua {font-size: 1.12rem; line-height: 2.4; padding: 1rem 1.2rem; border: 1px solid #e5e7eb;
          border-radius: 12px; background: #ffffff;}
.tt {padding: 0.15rem 0.35rem; border-radius: 6px; border: 1px solid; font-weight: 600; color: #111827;}
.nhan {font-size: 0.68rem; color: #fff; padding: 0.05rem 0.35rem; border-radius: 4px; margin-left: 0.35rem;
       vertical-align: middle; font-weight: 600;}
.chu-thich {display: inline-block; margin: 0.15rem 0.3rem 0.15rem 0; padding: 0.1rem 0.5rem; border-radius: 6px;
            font-size: 0.85rem; border: 1px solid;}
</style>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ tải mô hình (1 lần, dùng lại giữa các lượt)
def liet_ke_mo_hinh():
    ds = {}
    if os.path.isdir(THU_MUC_MO_HINH):
        for ten in sorted(os.listdir(THU_MUC_MO_HINH)):
            p = os.path.join(THU_MUC_MO_HINH, ten)
            if os.path.exists(os.path.join(p, "config.json")):
                ds[ten] = p
    if os.environ.get("NER_MODEL"):
        ds[os.environ["NER_MODEL"]] = os.environ["NER_MODEL"]

    def f1(ten):                                     # mô hình có Micro-F1 test cao nhất đứng đầu danh sách
        p = os.path.join(ds[ten], "thong_tin_de26.json")
        return json.load(open(p, encoding="utf-8")).get("f1_micro") or 0 if os.path.exists(p) else 0
    return {k: ds[k] for k in sorted(ds, key=f1, reverse=True)}


@st.cache_resource(show_spinner="Đang tải mô hình (chỉ lần đầu)...")
def tai_mo_hinh(duong_dan):
    return MoHinhNER(duong_dan)


@st.cache_resource(show_spinner="Đang chuẩn bị bộ tách từ tiếng Việt...")
def tai_bo_tach_tu():
    return BoTachTu()


# ------------------------------------------------------------------ thanh bên
cac_mo_hinh = liet_ke_mo_hinh()
with st.sidebar:
    st.header("⚙️ Cấu hình")
    if not cac_mo_hinh:
        st.error("Chưa có mô hình. Chép thư mục mô hình đã huấn luyện vào `app/mo_hinh/<tên>/` rồi tải lại trang.")
        st.stop()
    ten_mo_hinh = st.selectbox("Mô hình", list(cac_mo_hinh), help="Mặc định nên chọn mô hình tốt nhất trong 3 kiến trúc.")
    mo_hinh = tai_mo_hinh(cac_mo_hinh[ten_mo_hinh])
    tt = mo_hinh.thong_tin
    if tt:
        c1, c2 = st.columns(2)
        c1.metric("Micro-F1 test", f"{tt.get('f1_micro', 0):.3f}" if tt.get("f1_micro") else "—")
        c2.metric("Macro-F1 test", f"{tt.get('f1_macro', 0):.3f}" if tt.get("f1_macro") else "—")
        st.caption(f"{tt.get('model', '')} · đầu vào {'mức từ' if mo_hinh.muc_tu else 'âm tiết'} · seed {tt.get('seed', '—')}")
    nguong = st.slider("Ngưỡng độ tin cậy", 0.0, 0.95, 0.0, 0.05,
                       help="Ẩn các thực thể mô hình không chắc chắn (độ tin cậy = xác suất softmax trung bình).")
    hien_buoc = st.toggle("Hiện các bước xử lý", value=True)
    st.divider()
    st.subheader("10 loại thực thể")
    st.markdown("".join(f'<span class="chu-thich" style="background:{LOAI[k][1]};border-color:{MAU_CHU[k]}">'
                        f'{LOAI[k][0]}</span>' for k in LOAI), unsafe_allow_html=True)

bo_tach_tu = tai_bo_tach_tu() if mo_hinh.muc_tu else None

# ------------------------------------------------------------------ nội dung chính
st.title("🩺 Nhận dạng thực thể tiếng Việt về COVID-19")
st.caption("Đồ án Xử lý ngôn ngữ tự nhiên · Đề 26 · Dữ liệu PhoNER_COVID19 (Truong et al., NAACL 2021)")

tab_1, tab_nhieu, tab_gioi_thieu = st.tabs(["✍️ Nhập 1 đoạn văn", "📄 Nhiều câu (file .txt)", "ℹ️ Giới thiệu"])

with tab_1:
    st.write("**Câu mẫu:**")
    cot = st.columns(len(VI_DU))
    for c, (ten, cau) in zip(cot, VI_DU.items()):
        if c.button(ten, width="stretch"):
            st.session_state["van_ban"] = cau
    van_ban = st.text_area("Nhập văn bản tin tức tiếng Việt về COVID-19", key="van_ban", height=130,
                           placeholder="Ví dụ: Bệnh nhân 91 là phi công người Anh, đang điều trị tại Bệnh viện Chợ Rẫy...")
    if st.button("🔍 Nhận dạng thực thể", type="primary", disabled=not van_ban.strip()):
        bat_dau = time.time()
        kq = nhan_dang(van_ban, mo_hinh, bo_tach_tu)
        thoi_gian = time.time() - bat_dau
        tt_hien = [t for t in kq["thuc_the"] if t["do_tin_cay"] >= nguong]
        m1, m2, m3 = st.columns(3)
        m1.metric("Số thực thể", len(tt_hien))
        m2.metric("Số loại", len({t["loai"] for t in tt_hien}))
        m3.metric("Thời gian xử lý", f"{thoi_gian * 1000:.0f} ms")
        st.markdown(f'<div class="ket-qua">{html_to_mau(kq, nguong)}</div>', unsafe_allow_html=True)
        if tt_hien:
            bang = pd.DataFrame([{"Thực thể": t["van_ban"], "Loại": LOAI[t["loai"]][0], "Nhãn": t["loai"],
                                  "Độ tin cậy": round(t["do_tin_cay"], 3)} for t in tt_hien])
            st.dataframe(bang, width="stretch", hide_index=True,
                         column_config={"Độ tin cậy": st.column_config.ProgressColumn(min_value=0.0, max_value=1.0, format="%.3f")})
            st.download_button("⬇️ Tải kết quả (JSON)", json.dumps(kq["thuc_the"], ensure_ascii=False, indent=2),
                               file_name="thuc_the.json", mime="application/json")
        else:
            st.info("Không tìm thấy thực thể nào (hoặc tất cả dưới ngưỡng độ tin cậy).")
        if hien_buoc:
            with st.expander("🔬 Các bước xử lý bên trong mô hình", expanded=False):
                st.markdown(f"**Bước 1 — Chuẩn hóa Unicode NFC:** `{kq['van_ban_chuan_hoa'][:300]}`")
                st.markdown(f"**Bước 2 — Tách token:** {kq['cach_tach']} · {len(kq['token'])} token")
                st.markdown("**Bước 3–4 — Subword và nhãn BIO dự đoán cho từng token:**")
                st.dataframe(pd.DataFrame({"Token": kq["token"], "Subword": [" ".join(m) for m in kq["subword"]],
                                           "Nhãn BIO": kq["nhan"], "Xác suất": [round(x, 3) for x in kq["xac_suat"]]}),
                             width="stretch", hide_index=True, height=300)
                st.caption("Nhãn đặt ở subword đầu của mỗi token; B- = bắt đầu thực thể, I- = bên trong, O = không phải thực thể.")

with tab_nhieu:
    st.write("Tải file `.txt`, **mỗi dòng 1 câu**. Kết quả là bảng thực thể của từng câu, tải về dạng CSV.")
    tep = st.file_uploader("Chọn file .txt (UTF-8)", type=["txt"])
    if tep is not None:
        cac_dong = [d.strip() for d in io.TextIOWrapper(tep, encoding="utf-8-sig") if d.strip()][:500]
        tien_do = st.progress(0.0, text="Đang xử lý...")
        dong_kq = []
        for i, cau in enumerate(cac_dong):
            for t in nhan_dang(cau, mo_hinh, bo_tach_tu)["thuc_the"]:
                if t["do_tin_cay"] >= nguong:
                    dong_kq.append({"Câu số": i + 1, "Thực thể": t["van_ban"], "Nhãn": t["loai"],
                                    "Loại": LOAI[t["loai"]][0], "Độ tin cậy": round(t["do_tin_cay"], 3)})
            tien_do.progress((i + 1) / len(cac_dong), text=f"{i + 1}/{len(cac_dong)} câu")
        df = pd.DataFrame(dong_kq)
        st.success(f"Xong {len(cac_dong)} câu · {len(df)} thực thể")
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8-sig"), "ket_qua_ner.csv", "text/csv")

with tab_gioi_thieu:
    st.markdown("""
**Bài toán.** Nhận dạng thực thể có tên (NER) trong tin tức tiếng Việt về COVID-19: với mỗi từ, mô hình dự đoán từ đó
thuộc 1 trong 10 loại thực thể (mã bệnh nhân, tên, tuổi, giới tính, nghề nghiệp, địa điểm, tổ chức, triệu chứng/bệnh,
phương tiện, ngày tháng) hay không, theo sơ đồ nhãn **BIO** (21 nhãn).

**Dữ liệu.** PhoNER_COVID19 (VinAI Research): 10.027 câu, 34.980 thực thể, chia train/dev/test = 5.027/2.000/3.000 câu.

**Mô hình.** Fine-tune PhoBERT-base (mức từ), XLM-RoBERTa-base và mBERT-cased (mức âm tiết), mỗi kiến trúc 3 seed;
so sánh với baseline CRF và zero-shot. Demo dùng mô hình tốt nhất.

**Lưu ý.** Đây là sản phẩm học tập; kết quả có thể sai với văn bản khác xa miền tin tức COVID-19 năm 2020.
""")
