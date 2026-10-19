"""ve_so_do.py - Vẽ sơ đồ kiến trúc tổng thể hệ thống (báo cáo mục 5.1) và sơ đồ luồng xử lý của demo (mục 4.7).

Chạy:  python src/ve_so_do.py   ->  reports/hinh/so_do_tong_the.png, reports/hinh/so_do_demo.png
Muốn sửa chữ trong sơ đồ: sửa trực tiếp các chuỗi trong file này rồi chạy lại (không cần phần mềm vẽ).
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_RA = os.path.join(THU_MUC_GOC, "reports", "hinh")
plt.rcParams["font.family"] = "DejaVu Sans"

MAU = {"nguon": ("#e8f1fb", "#2b6cb0"), "xu_ly": ("#e9f7ef", "#2f855a"), "mo_hinh": ("#fff4e5", "#c05621"),
       "toi_uu": ("#f3e8ff", "#6b46c1"), "danh_gia": ("#fdecec", "#c53030"), "trien_khai": ("#e6fffa", "#2c7a7b"),
       "ha_tang": ("#f7f7f7", "#4a5568")}


def hop(ax, x, y, w, h, tieu_de, dong, loai, co_chu=8.6, co_tieu_de=10, dy=None):
    nen, vien = MAU[loai]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                fc=nen, ec=vien, lw=1.6))
    dy = dy or (0.014, 0.036 if h < 0.08 else 0.045)
    ax.text(x + w / 2, y + h - dy[0], tieu_de, ha="center", va="top", fontsize=co_tieu_de, weight="bold", color=vien)
    ax.text(x + w / 2, y + h - dy[1], "\n".join(dong), ha="center", va="top", fontsize=co_chu, color="#1a202c",
            linespacing=1.35)


def mui_ten(ax, a, b, nhan=None, cong=0.0, mau="#4a5568"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, lw=1.4, color=mau,
                                 connectionstyle=f"arc3,rad={cong}"))
    if nhan:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.012, nhan, ha="center", fontsize=7.8, color=mau, style="italic")


def nhan_tang(ax, y, h, ten):
    ax.text(0.012, y + h / 2, ten, rotation=90, ha="center", va="center", fontsize=9, weight="bold", color="#718096")
    ax.plot([0.026, 0.026], [y, y + h], color="#cbd5e0", lw=2)


def so_do_tong_the():
    fig = plt.figure(figsize=(15, 10.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.985, "Kiến trúc tổng thể hệ thống nhận dạng thực thể COVID-19 tiếng Việt (Đề 26)",
            ha="center", va="top", fontsize=15, weight="bold", color="#1a202c")
    A, B, C = (0.045, 0.225), (0.295, 0.225), (0.555, 0.425)          # 3 cột: CRF | zero-shot | fine-tune
    XA, XB, XC = A[0] + A[1] / 2, B[0] + B[1] / 2, C[0] + C[1] / 2

    # Tầng 1 - Dữ liệu
    nhan_tang(ax, 0.745, 0.205, "1. DỮ LIỆU")
    hop(ax, 0.045, 0.835, 0.30, 0.115, "PhoNER_COVID19 (VinAI, NAACL 2021)",
        ["10.027 câu tin tức COVID-19 · 34.980 thực thể", "10 loại thực thể → 21 nhãn BIO",
         "train / dev / test = 5.027 / 2.000 / 3.000"], "nguon")
    hop(ax, 0.385, 0.835, 0.36, 0.115, "Hai phiên bản của cùng dữ liệu",
        ["âm tiết  data/syllable → XLM-R, mBERT, zero-shot", "mức từ  data/word (RDRSegmenter) → PhoBERT, CRF",
         "mỗi dòng 1 câu: {\"words\": [...], \"tags\": [...]}"], "nguon")
    hop(ax, 0.785, 0.835, 0.195, 0.115, "Khám phá dữ liệu", ["src/eda.py: phân bố loại,", "độ dài câu / thực thể,",
                                                             "subword, NFC, thực thể mới"], "xu_ly")
    mui_ten(ax, (0.345, 0.892), (0.385, 0.892))
    mui_ten(ax, (0.745, 0.892), (0.785, 0.892))
    hop(ax, 0.045, 0.745, 0.935, 0.06, "Đọc & chuẩn hóa — src/data.py",
        ["chuẩn hóa Unicode NFC (1.052 token/phiên bản) · kiểm tra số token = số nhãn và IOB2 · label2id cố định 21 nhãn"],
        "xu_ly", co_tieu_de=9.5)
    mui_ten(ax, (0.565, 0.835), (0.565, 0.805))

    # Tầng 2 - Biểu diễn đầu vào cho từng hướng
    nhan_tang(ax, 0.615, 0.105, "2. BIỂU DIỄN")
    hop(ax, A[0], 0.615, A[1], 0.105, "Đặc trưng thủ công", ["từ viết thường, tiền/hậu tố,", "viết hoa, là số, vị trí,",
                                                              "đặc trưng từ lân cận"], "xu_ly")
    hop(ax, B[0], 0.615, B[1], 0.105, "Căn đầu ra pipeline", ["thực thể của model có sẵn", "→ nhãn BIO theo âm tiết",
                                                             "ánh xạ PER/LOC/ORG"], "xu_ly")
    hop(ax, C[0], 0.615, C[1], 0.105, "Mã hóa subword + căn nhãn",
        ["BPE (PhoBERT) · SentencePiece (XLM-R) · WordPiece (mBERT)", "nhãn ở subword ĐẦU của token, các mảnh còn lại = −100",
         "max_length 256 · dynamic padding"], "xu_ly")
    for x in (XA, XB, XC):
        mui_ten(ax, (x, 0.745), (x, 0.72))

    # Tầng 3 - Mô hình
    nhan_tang(ax, 0.42, 0.165, "3. MÔ HÌNH")
    hop(ax, A[0], 0.42, A[1], 0.165, "(A) Baseline CRF",
        ["sklearn-crfsuite, L-BFGS", "c1 (L1), c2 (L2) chọn trên dev", "chấm điểm cả chuỗi nhãn:", "đặc trưng + chuyển nhãn"],
        "mo_hinh")
    hop(ax, B[0], 0.42, B[1], 0.165, "(B) Zero-shot",
        ["NER tiếng Việt có sẵn", "(NlpHUST ELECTRA, VLSP 2018)", "KHÔNG huấn luyện lại", "loại không có → F1 = 0"], "mo_hinh")
    hop(ax, C[0], 0.42, C[1], 0.165, "(C) Fine-tune — src/train_ner.py (1 script cho 3 kiến trúc)",
        ["PhoBERT-base (mức từ) · XLM-R-base (âm tiết) · mBERT-cased (âm tiết)",
         "encoder pretrained → tuyến tính 768 → 21 → softmax từng token",
         "cross-entropy · AdamW + warmup · fp16 · dừng sớm 3 epoch",
         "3 seed (42, 123, 2024) · nâng cao: PhoBERT không tách từ"], "mo_hinh")
    for x in (XA, XB, XC):
        mui_ten(ax, (x, 0.615), (x, 0.585))

    # Tầng 4 - Tối ưu + đánh giá
    nhan_tang(ax, 0.225, 0.165, "4. TỐI ƯU & ĐÁNH GIÁ")
    hop(ax, C[0], 0.225, C[1], 0.165, "Tìm siêu tham số trên DEV (mục 4.3)",
        ["Grid Search (ParameterGrid): lr {2e-5, 3e-5, 5e-5} × batch {16, 32}",
         "Random Search (ParameterSampler): thêm warmup, weight decay",
         "cùng không gian + cùng ngân sách cho 3 kiến trúc",
         "chọn theo Micro-F1 dev → huấn luyện lại 3 seed"], "toi_uu")
    hop(ax, A[0], 0.225, B[0] + B[1] - A[0], 0.165, "Đánh giá trên TEST — src/aggregate.py",
        ["seqeval: F1 mức thực thể, mode strict, IOB2", "Micro-F1, Macro-F1, P, R, F1 từng loại",
         "mean ± std mẫu (n−1) qua 3 seed · Welch t-test", "đối chiếu số liệu bài báo gốc"], "danh_gia")
    mui_ten(ax, (XC, 0.42), (XC, 0.39))
    mui_ten(ax, (XA, 0.42), (XA, 0.39))
    mui_ten(ax, (XB, 0.42), (XB, 0.39))
    mui_ten(ax, (C[0], 0.29), (B[0] + B[1], 0.29))
    ax.text((C[0] + B[0] + B[1]) / 2, 0.30, "3 seed", ha="center", fontsize=7.8, color="#4a5568", style="italic")

    # Tầng 5 - Phân tích + ứng dụng
    nhan_tang(ax, 0.055, 0.14, "5. PHÂN TÍCH & ỨNG DỤNG")
    hop(ax, A[0], 0.055, A[1], 0.14, "Phân tích lỗi", ["src/phan_tich_loi.py", "sai loại · sai biên · sai cả hai",
                                                      "bỏ sót · dự đoán thừa", "lỗi chung / riêng 3 kiến trúc"], "danh_gia")
    hop(ax, B[0], 0.055, B[1], 0.14, "Có / không tách từ", ["PhoBERT mức từ vs âm tiết", "cùng seed + siêu tham số",
                                                           "F1 theo loại, theo độ dài", "thực thể (số âm tiết)"], "danh_gia")
    hop(ax, C[0], 0.055, C[1], 0.14, "Ứng dụng Streamlit — app/app.py",
        ["mô hình tốt nhất · văn bản → NFC → tách từ → mô hình → BIO → thực thể",
         "tô màu thực thể + độ tin cậy · các bước xử lý bên trong",
         "nhập 1 đoạn hoặc file .txt → tải CSV / JSON"], "trien_khai")
    mui_ten(ax, (XA, 0.225), (XA, 0.195))
    mui_ten(ax, (XB, 0.225), (XB, 0.195))
    mui_ten(ax, (XC, 0.225), (XC, 0.195))
    ax.text(XC + 0.01, 0.205, "mô hình tốt nhất", fontsize=7.8, color="#4a5568", style="italic", va="center")

    ax.text(0.5, 0.012, "Hạ tầng:  GitHub (mã nguồn, Issue, Pull Request, Project board)  ·  Google Colab GPU T4 (huấn luyện)  ·  "
            "Google Drive (sao lưu kết quả, mô hình)  ·  VS Code (tổng hợp, phân tích lỗi, chạy demo)",
            ha="center", va="bottom", fontsize=8.8, color="#4a5568",
            bbox=dict(boxstyle="round,pad=0.35", fc=MAU["ha_tang"][0], ec=MAU["ha_tang"][1], lw=1))
    os.makedirs(THU_MUC_RA, exist_ok=True)
    fig.savefig(os.path.join(THU_MUC_RA, "so_do_tong_the.png"), dpi=200)
    plt.close(fig)


def so_do_demo():
    fig = plt.figure(figsize=(15, 3.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, "Luồng xử lý của ứng dụng demo (app/ner_core.py) — giống hệt lúc huấn luyện",
            ha="center", va="top", fontsize=13, weight="bold")
    buoc = [("Đầu vào", ["đoạn văn tiếng Việt", "hoặc file .txt"], "nguon"),
            ("① Chuẩn hóa", ["Unicode NFC", "bỏ khoảng trắng thừa"], "xu_ly"),
            ("② Tách token", ["âm tiết + dấu câu;", "PhoBERT: tách từ", "VnCoreNLP / underthesea"], "xu_ly"),
            ("③ Subword", ["tokenizer của mô hình", "chia cửa sổ ≤ 256"], "xu_ly"),
            ("④ Mô hình", ["encoder + softmax", "nhãn ở subword đầu"], "mo_hinh"),
            ("⑤ Hậu xử lý", ["sửa I- lạc → B-", "gộp B-/I- thành", "thực thể + độ tin cậy"], "danh_gia"),
            ("Đầu ra", ["văn bản tô màu,", "bảng thực thể,", "tải CSV / JSON"], "trien_khai")]
    w, gap = 0.12, (1 - 0.04 - 7 * 0.12) / 6
    for i, (t, d, l) in enumerate(buoc):
        x = 0.02 + i * (w + gap)
        hop(ax, x, 0.1, w, 0.68, t, d, l, co_chu=9.5, co_tieu_de=11, dy=(0.07, 0.24))
        if i:
            mui_ten(ax, (x - gap, 0.44), (x, 0.44))
    fig.savefig(os.path.join(THU_MUC_RA, "so_do_demo.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    so_do_tong_the()
    so_do_demo()
    print("Đã vẽ:", os.listdir(THU_MUC_RA))
