"""aggregate.py - Gộp các file results/*.json thành bảng mean ± std + biểu đồ cho báo cáo.

Người phụ trách: Hoàng Duyên · Issue T20 (bản đầu) → T27 + T39 (bản đầy đủ, biểu đồ)
Chạy được trên máy cá nhân (VS Code) hoặc Colab, KHÔNG cần GPU:   python src/aggregate.py

Đầu ra (thư mục results/tong_hop/):
  bang_tong_hop.csv / .md     mean ± std (micro/macro F1, P, R) của từng phương pháp + số liệu bài báo để đối chiếu
  bang_theo_seed.csv / .md    từng seed của từng kiến trúc
  bang_f1_tung_loai.csv / .md F1 từng loại thực thể (mean qua seed)
  kiem_dinh.md                kiểm định Welch t-test giữa các kiến trúc (kèm cảnh báo n = 3)
  hinh_f1_kien_truc.png       cột mean ± std
  hinh_f1_tung_loai.png       F1 từng loại
Quy ước: std MẪU (chia n-1, numpy ddof=1). CRF và zero-shot chỉ có 1 lượt -> không có std.
"""

import glob
import json
import os

import numpy as np
import pandas as pd

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_KQ = os.path.join(THU_MUC_GOC, "results")
THU_MUC_RA = os.path.join(THU_MUC_KQ, "tong_hop")
CAC_LOAI = ["PATIENT_ID", "NAME", "AGE", "GENDER", "JOB", "LOCATION", "ORGANIZATION",
            "SYMPTOM_AND_DISEASE", "TRANSPORTATION", "DATE"]
TEN_HIEN_THI = {"crf": "(A) CRF", "zeroshot": "(B) Zero-shot", "phobert": "(C) PhoBERT-base",
                "xlmr": "(C) XLM-R-base", "mbert": "(C) mBERT-cased",
                "phobert_khong_tach_tu": "Nâng cao: PhoBERT không tách từ"}
THU_TU = list(TEN_HIEN_THI)
# Số liệu bài báo gốc (Truong et al., NAACL 2021, Bảng 3 — test, trung bình 5 seed) để đối chiếu
BAI_BAO = [("Bài báo: BiLSTM-CNN-CRF (mức từ)", 0.910, 0.875), ("Bài báo: XLM-R base (âm tiết)", 0.925, 0.879),
           ("Bài báo: PhoBERT base (mức từ)", 0.942, 0.920), ("Bài báo: PhoBERT large (mức từ)", 0.945, 0.931)]


def doc_ket_qua(thu_muc=THU_MUC_KQ):
    """Đọc mọi results/*.json (bỏ file bắt đầu bằng "_"). Đầu ra: list dict có thêm khóa 'khoa'."""
    ds = []
    for p in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        ten = os.path.basename(p)
        if ten.startswith("_"):
            continue
        kq = json.load(open(p, encoding="utf-8"))
        kq["khoa"] = kq.get("khoa_mo_hinh") or os.path.splitext(ten)[0]     # crf.json, zeroshot.json của Phúc
        if kq.get("thu_nhanh"):
            continue
        ds.append(kq)
    return ds


def dinh_dang(gia_tri):
    m = np.mean(gia_tri)
    if len(gia_tri) < 2:
        return f"{m:.4f}"
    return f"{m:.4f} ± {np.std(gia_tri, ddof=1):.4f}"


def bang_markdown(df):
    cot = list(df.columns)
    dong = ["| " + " | ".join(cot) + " |", "|" + "|".join(["---"] * len(cot)) + "|"]
    dong += ["| " + " | ".join(str(x) for x in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(dong)


def tong_hop(ds):
    nhom = {}
    for kq in ds:
        nhom.setdefault(kq["khoa"], []).append(kq)
    khoa_sap = sorted(nhom, key=lambda k: THU_TU.index(k) if k in THU_TU else 99)

    dong_tong, dong_seed, dong_loai = [], [], []
    for k in khoa_sap:
        g = sorted(nhom[k], key=lambda x: x.get("seed", 0))
        dong_tong.append({
            "Phương pháp": TEN_HIEN_THI.get(k, k), "Số lượt (seed)": len(g),
            "Micro-F1": dinh_dang([x["f1_micro"] for x in g]), "Macro-F1": dinh_dang([x["f1_macro"] for x in g]),
            "Precision": dinh_dang([x["precision_micro"] for x in g]), "Recall": dinh_dang([x["recall_micro"] for x in g]),
            "_mean": float(np.mean([x["f1_micro"] for x in g])),
            "_std": float(np.std([x["f1_micro"] for x in g], ddof=1)) if len(g) > 1 else 0.0,
        })
        for x in g:
            if "seed" in x:
                dong_seed.append({"Kiến trúc": TEN_HIEN_THI.get(k, k), "Seed": x["seed"], "Micro-F1": x["f1_micro"],
                                  "Macro-F1": x["f1_macro"], "F1 dev": x.get("f1_micro_dev"),
                                  "Epoch tốt nhất": x.get("best_epoch"), "Thời gian (phút)": round(x.get("thoi_gian_train_giay", 0) / 60, 1)})
        dong_loai.append({"Phương pháp": TEN_HIEN_THI.get(k, k),
                          **{l: round(float(np.mean([x["f1_tung_loai"].get(l, 0) for x in g])), 4) for l in CAC_LOAI}})
    for ten, mi, ma in BAI_BAO:
        dong_tong.append({"Phương pháp": ten, "Số lượt (seed)": 5, "Micro-F1": f"{mi:.3f}", "Macro-F1": f"{ma:.3f}",
                          "Precision": "—", "Recall": "—", "_mean": mi, "_std": 0.0})
    return nhom, pd.DataFrame(dong_tong), pd.DataFrame(dong_seed), pd.DataFrame(dong_loai)


def kiem_dinh(nhom):
    """Welch t-test trên Micro-F1 giữa các cặp kiến trúc fine-tune (Dror et al., ACL 2018 khuyến nghị kiểm định
    ý nghĩa thống kê; với n = 3 seed, độ mạnh kiểm định thấp -> chỉ dùng tham khảo)."""
    try:
        from scipy.stats import ttest_ind
    except ImportError:
        return "Chưa cài scipy nên bỏ qua kiểm định."
    cac_kt = [k for k in ("phobert", "xlmr", "mbert", "phobert_khong_tach_tu") if len(nhom.get(k, [])) >= 2]
    dong = ["| Cặp so sánh | Chênh lệch mean Micro-F1 | p-value (Welch) | Kết luận ở mức 0,05 |", "|---|---|---|---|"]
    for i in range(len(cac_kt)):
        for j in range(i + 1, len(cac_kt)):
            a = [x["f1_micro"] for x in nhom[cac_kt[i]]]
            b = [x["f1_micro"] for x in nhom[cac_kt[j]]]
            p = ttest_ind(a, b, equal_var=False).pvalue
            dong.append(f"| {TEN_HIEN_THI[cac_kt[i]]} vs {TEN_HIEN_THI[cac_kt[j]]} | {np.mean(a) - np.mean(b):+.4f} | "
                        f"{p:.4f} | {'khác biệt có ý nghĩa' if p < 0.05 else 'chưa đủ bằng chứng khác biệt'} |")
    return "\n".join(dong) + "\n\n*Lưu ý: chỉ 3 seed/kiến trúc nên kiểm định có độ mạnh thấp; kết luận cần thận trọng.*"


def ve_hinh(df_tong, df_loai):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(THU_MUC_RA, exist_ok=True)
    d = df_tong[~df_tong["Phương pháp"].str.startswith("Bài báo")]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(d["Phương pháp"], d["_mean"], yerr=d["_std"], capsize=6, color="#2b6cb0")
    for i, (m, s) in enumerate(zip(d["_mean"], d["_std"])):
        ax.text(i, m + s + 0.005, f"{m:.3f}", ha="center", fontsize=9)
    ax.set_ylim(max(0, d["_mean"].min() - 0.1), 1.0)
    ax.set_ylabel("Micro-F1 (test)")
    ax.set_title("Micro-F1 trên tập test (thanh lỗi = độ lệch chuẩn qua 3 seed)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    fig.savefig(os.path.join(THU_MUC_RA, "hinh_f1_kien_truc.png"), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    w = 0.8 / max(1, len(df_loai))
    x = np.arange(len(CAC_LOAI))
    for i, r in enumerate(df_loai.itertuples(index=False)):
        ax.bar(x + i * w, [getattr(r, l) for l in CAC_LOAI], w, label=r[0])
    ax.set_xticks(x + w * (len(df_loai) - 1) / 2)
    ax.set_xticklabels(CAC_LOAI, rotation=30, ha="right")
    ax.set_ylabel("F1 (test)")
    ax.set_title("F1 theo từng loại thực thể")
    ax.legend(fontsize=8, ncol=3)
    plt.tight_layout()
    fig.savefig(os.path.join(THU_MUC_RA, "hinh_f1_tung_loai.png"), dpi=200)
    plt.close(fig)


def main():
    ds = doc_ket_qua()
    if not ds:
        print("Chưa có file kết quả nào trong results/.")
        return
    nhom, df_tong, df_seed, df_loai = tong_hop(ds)
    os.makedirs(THU_MUC_RA, exist_ok=True)
    cot = [c for c in df_tong.columns if not c.startswith("_")]
    for ten, df in (("bang_tong_hop", df_tong[cot]), ("bang_theo_seed", df_seed), ("bang_f1_tung_loai", df_loai)):
        df.to_csv(os.path.join(THU_MUC_RA, ten + ".csv"), index=False, encoding="utf-8-sig")
        open(os.path.join(THU_MUC_RA, ten + ".md"), "w", encoding="utf-8").write(bang_markdown(df))
    open(os.path.join(THU_MUC_RA, "kiem_dinh.md"), "w", encoding="utf-8").write(kiem_dinh(nhom))
    ve_hinh(df_tong, df_loai)
    print("== Bảng tổng hợp ==\n" + bang_markdown(df_tong[cot]))
    print("\n== Theo seed ==\n" + bang_markdown(df_seed))
    print("\n== Kiểm định ==\n" + kiem_dinh(nhom))
    print(f"\nĐã ghi bảng và hình vào {THU_MUC_RA}")


if __name__ == "__main__":
    main()
