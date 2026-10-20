"""eda.py - Khám phá dữ liệu PhoNER_COVID19 (báo cáo mục 3.1 – 3.2, BC1 mục 2).

Người phụ trách: Đức Tâm · Issue T11
Chạy:  python src/eda.py                 (máy cá nhân hoặc Colab, KHÔNG cần GPU)
       python src/eda.py --tokenizer     (thêm phần đếm subword - cần internet để tải 3 tokenizer, nên chạy trên Colab)

Đầu ra (results/eda/):
  bang_thuc_the_theo_loai.csv/.md   số thực thể theo loại × tập, so với Bảng 2 của bài báo
  bang_tong_quan.md                 số câu, số token, số thực thể, % token nhãn O, token không ở dạng NFC
  do_dai_cau.csv                    thống kê độ dài câu (âm tiết / từ)
  do_dai_thuc_the.csv               số thực thể theo độ dài (âm tiết) - lý do lỗi "sai biên"
  thuc_the_chua_gap.csv             % thực thể ở test chưa từng xuất hiện trong train (theo loại)
  subword.csv                       (nếu --tokenizer) số subword/câu và % câu > 256 subword cho 3 tokenizer
  hinh_*.png                        biểu đồ cho báo cáo
"""

import argparse
import os
import sys
import unicodedata
from collections import Counter

THU_MUC_SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC_SRC)
from data import CAC_TAP, THU_MUC_GOC, dem_thuc_the_theo_loai, lay_thuc_the, tai_du_lieu  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

THU_MUC_RA = os.path.join(THU_MUC_GOC, "results", "eda")
CAC_LOAI = ["PATIENT_ID", "NAME", "AGE", "GENDER", "JOB", "LOCATION", "ORGANIZATION",
            "SYMPTOM_AND_DISEASE", "TRANSPORTATION", "DATE"]
# Bảng 2 của bài báo (Truong et al., NAACL 2021): số thực thể theo loại ở train / dev / test
BAI_BAO = {"PATIENT_ID": (3240, 1276, 2005), "NAME": (349, 188, 318), "AGE": (682, 361, 582),
           "GENDER": (542, 277, 462), "JOB": (205, 132, 173), "LOCATION": (5398, 2737, 4441),
           "ORGANIZATION": (1137, 551, 771), "SYMPTOM_AND_DISEASE": (1439, 766, 1136),
           "TRANSPORTATION": (226, 87, 193), "DATE": (2549, 1103, 1654)}


def bang_md(df):
    cot = [str(c) for c in df.columns]
    dong = ["| " + " | ".join(cot) + " |", "|" + "---|" * len(cot)]
    return "\n".join(dong + ["| " + " | ".join(str(x) for x in r) + " |" for r in df.itertuples(index=False)])


def ghi(df, ten):
    df.to_csv(os.path.join(THU_MUC_RA, ten + ".csv"), index=False, encoding="utf-8-sig")
    open(os.path.join(THU_MUC_RA, ten + ".md"), "w", encoding="utf-8").write(bang_md(df))


def thong_ke(gia_tri):
    a = np.array(gia_tri)
    return {"Trung bình": round(a.mean(), 1), "Trung vị": int(np.median(a)), "Phân vị 95": int(np.percentile(a, 95)),
            "Lớn nhất": int(a.max()), "Nhỏ nhất": int(a.min())}


def main(dem_subword=False):
    os.makedirs(THU_MUC_RA, exist_ok=True)
    tu, am = tai_du_lieu("word"), tai_du_lieu("syllable")
    tu_goc = tai_du_lieu("word", nfc=False)

    # 1) Thực thể theo loại × tập, đối chiếu bài báo
    dem = {t: dem_thuc_the_theo_loai(am[t][1]) for t in CAC_TAP}
    dong = []
    for l in CAC_LOAI:
        dong.append({"Loại": l, **{t.capitalize(): dem[t][l] for t in CAC_TAP},
                     "Tổng": sum(dem[t][l] for t in CAC_TAP),
                     "Khớp bài báo": "✓" if tuple(dem[t][l] for t in CAC_TAP) == BAI_BAO[l] else "✗"})
    dong.append({"Loại": "Tổng", **{t.capitalize(): sum(dem[t].values()) for t in CAC_TAP},
                 "Tổng": sum(sum(dem[t].values()) for t in CAC_TAP), "Khớp bài báo": ""})
    df_loai = pd.DataFrame(dong)
    ghi(df_loai, "bang_thuc_the_theo_loai")
    tong_bai_bao = sum(sum(v) for v in BAI_BAO.values())

    # 2) Tổng quan
    tq = []
    for t in CAC_TAP:
        n_am = sum(len(c) for c in am[t][0])
        n_tu = sum(len(c) for c in tu[t][0])
        n_o = sum(x == "O" for n in am[t][1] for x in n)
        n_o_tu = sum(x == "O" for n in tu[t][1] for x in n)
        khong_nfc = sum(unicodedata.normalize("NFC", w) != w for c in tu_goc[t][0] for w in c)
        tq.append({"Tập": t, "Số câu": len(am[t][0]), "Số âm tiết": n_am, "Số từ (sau tách từ)": n_tu,
                   "Âm tiết / từ": round(n_am / n_tu, 3), "Số thực thể": sum(dem[t].values()),
                   "% âm tiết nhãn O": round(100 * n_o / n_am, 1),
                   "% từ nhãn O": round(100 * n_o_tu / n_tu, 1), "Token chưa ở dạng NFC": khong_nfc})
    df_tq = pd.DataFrame(tq)
    ghi(df_tq, "bang_tong_quan")

    # 3) Độ dài câu
    dd = []
    for t in CAC_TAP:
        dd.append({"Tập": t, "Đơn vị": "âm tiết", **thong_ke([len(c) for c in am[t][0]])})
        dd.append({"Tập": t, "Đơn vị": "từ", **thong_ke([len(c) for c in tu[t][0]])})
    df_dd = pd.DataFrame(dd)
    ghi(df_dd, "do_dai_cau")

    # 4) Độ dài thực thể (âm tiết) theo loại - thực thể dài dễ "sai biên"
    dai = Counter()
    dai_loai = {l: [] for l in CAC_LOAI}
    for t in CAC_TAP:
        for n in am[t][1]:
            for l, s, e in lay_thuc_the(n):
                dai[min(e - s + 1, 6)] += 1
                dai_loai[l].append(e - s + 1)
    df_dai = pd.DataFrame([{"Số âm tiết": ("≥ 6" if k == 6 else k), "Số thực thể": v,
                            "%": round(100 * v / sum(dai.values()), 1)} for k, v in sorted(dai.items())])
    ghi(df_dai, "do_dai_thuc_the")
    df_dai_loai = pd.DataFrame([{"Loại": l, "Độ dài TB (âm tiết)": round(np.mean(v), 2), "Dài nhất": max(v)}
                                for l, v in dai_loai.items()])
    ghi(df_dai_loai, "do_dai_thuc_the_theo_loai")

    # 5) Thực thể ở test chưa từng gặp trong train (khả năng tổng quát hóa, không chỉ "nhớ")
    def tap_tt(cau, nhan):
        return [(l, " ".join(c[s:e + 1]).lower()) for c, n in zip(cau, nhan) for l, s, e in lay_thuc_the(n)]
    da_gap = set(tap_tt(*am["train"]))
    tt_test = tap_tt(*am["test"])
    df_moi = pd.DataFrame([{"Loại": l, "Số thực thể test": sum(1 for x in tt_test if x[0] == l),
                            "% chưa gặp trong train": round(100 * np.mean([x not in da_gap for x in tt_test if x[0] == l]), 1)}
                           for l in CAC_LOAI] +
                          [{"Loại": "Tất cả", "Số thực thể test": len(tt_test),
                            "% chưa gặp trong train": round(100 * np.mean([x not in da_gap for x in tt_test]), 1)}])
    ghi(df_moi, "thuc_the_chua_gap")

    # 6) Số subword theo từng tokenizer (độ dài thật mà mô hình nhìn thấy)
    df_sw = None
    if dem_subword:
        from transformers import AutoTokenizer
        cau_hinh = [("PhoBERT-base (mức từ)", "vinai/phobert-base", tu), ("XLM-R-base (âm tiết)", "xlm-roberta-base", am),
                    ("mBERT-cased (âm tiết)", "bert-base-multilingual-cased", am)]
        dong_sw = []
        for ten, ma, dl in cau_hinh:
            tok = AutoTokenizer.from_pretrained(ma)
            cache = {}

            def so_manh(w):
                if w not in cache:
                    cache[w] = max(1, len(tok.encode(w, add_special_tokens=False)))
                return cache[w]
            for t in CAC_TAP:
                n = [sum(so_manh(w) for w in c) + 2 for c in dl[t][0]]
                tong_tok = sum(len(c) for c in dl[t][0])
                dong_sw.append({"Tokenizer": ten, "Tập": t, "Subword/câu TB": round(np.mean(n), 1),
                                "Subword/token": round((sum(n) - 2 * len(n)) / tong_tok, 2), "Lớn nhất": max(n),
                                "Số câu > 256": sum(x > 256 for x in n), "% câu > 256": round(100 * np.mean([x > 256 for x in n]), 2),
                                "Lượt token chứa <unk>": sum(tok.unk_token_id in tok.encode(w, add_special_tokens=False)
                                                         for c in dl[t][0] for w in set(c))})
        df_sw = pd.DataFrame(dong_sw)
        ghi(df_sw, "subword")

    # 7) Hình
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = df_loai[df_loai["Loại"] != "Tổng"].set_index("Loại")[["Train", "Dev", "Test"]]
    ax = d.plot(kind="bar", figsize=(10, 4.2), color=["#2b6cb0", "#68d391", "#f6ad55"], rot=30)
    ax.set_ylabel("Số thực thể")
    ax.set_title("Số thực thể theo loại trên 3 tập (PhoNER_COVID19)")
    plt.xticks(ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(THU_MUC_RA, "hinh_thuc_the_theo_loai.png"), dpi=200)
    plt.close()

    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    ax[0].hist([len(c) for c in am["train"][0]], bins=40, color="#2b6cb0", alpha=0.8, label="âm tiết")
    ax[0].hist([len(c) for c in tu["train"][0]], bins=40, color="#f6ad55", alpha=0.7, label="từ")
    ax[0].set_title("Độ dài câu (tập train)")
    ax[0].set_xlabel("Số token / câu")
    ax[0].set_ylabel("Số câu")
    ax[0].legend()
    ax[1].bar(df_dai["Số âm tiết"].astype(str), df_dai["Số thực thể"], color="#805ad5")
    ax[1].set_title("Độ dài thực thể (cả 3 tập)")
    ax[1].set_xlabel("Số âm tiết / thực thể")
    plt.tight_layout()
    plt.savefig(os.path.join(THU_MUC_RA, "hinh_do_dai.png"), dpi=200)
    plt.close()

    # 8) Tóm tắt
    tom_tat = [
        "# Tóm tắt EDA - PhoNER_COVID19", "",
        "## Số thực thể theo loại (cột 'Khớp bài báo' đối chiếu Bảng 2 của Truong et al., 2021)", bang_md(df_loai), "",
        f"Ghi chú: tổng đếm được = {int(df_loai.iloc[-1]['Tổng'])}; cộng các ô trong Bảng 2 của bài báo = {tong_bai_bao}. "
        "Phần chữ của bài báo ghi tổng 34.984 thực thể - lệch 4 so với chính bảng của bài báo (nhiều khả năng lỗi đánh máy); "
        "nhóm dùng 34.980 vì khớp cả dữ liệu lẫn bảng.", "",
        "## Tổng quan", bang_md(df_tq), "", "## Độ dài câu", bang_md(df_dd), "",
        "## Độ dài thực thể (âm tiết)", bang_md(df_dai), "", bang_md(df_dai_loai), "",
        "## Thực thể ở test chưa từng gặp trong train", bang_md(df_moi),
    ]
    if df_sw is not None:
        tom_tat += ["", "## Subword theo tokenizer", bang_md(df_sw)]
    open(os.path.join(THU_MUC_RA, "tom_tat.md"), "w", encoding="utf-8").write("\n".join(tom_tat))
    print("\n".join(tom_tat))
    print(f"\nĐã ghi vào {THU_MUC_RA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", action="store_true", help="đếm subword bằng 3 tokenizer (cần internet)")
    main(ap.parse_args().tokenizer)
