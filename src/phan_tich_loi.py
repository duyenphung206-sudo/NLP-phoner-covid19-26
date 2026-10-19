"""phan_tich_loi.py - Phân tích lỗi có hệ thống cho 3 kiến trúc (và CRF nếu có) trên tập test.

Người phụ trách: Đức Tâm · Issue T31 + T38 (đọc lỗi từng model: T32 Duyên, T33 Tâm, T34 Trinh)
Chạy trên máy cá nhân (VS Code) hoặc Colab, KHÔNG cần GPU:   python src/phan_tich_loi.py --seed 42
CRF và zero-shot (của Phúc) tự được đưa vào nếu có file du_doan_test.json (xem FILE_CRF_ZEROSHOT).

Phân loại lỗi theo đúng khung của bài báo gốc (Truong et al., 2021, mục 5 — Error analysis):
  1. Sai loại      : đúng ranh giới, sai loại thực thể (vd. LOCATION ↔ ORGANIZATION)
  2. Sai biên      : đúng loại, lệch ranh giới (thiếu/thừa âm tiết)
  3. Sai cả hai    : chồng lấn nhưng sai cả biên lẫn loại
  4. Bỏ sót        : thực thể thật không được dự đoán (không chồng lấn với dự đoán nào)
  5. Dự đoán thừa  : dự đoán thực thể ở chỗ nhãn thật là O
So sánh công bằng giữa mô hình mức TỪ (PhoBERT) và mức ÂM TIẾT (XLM-R, mBERT): mọi thực thể được quy đổi về
vị trí ÂM TIẾT (tách "Bệnh_viện" -> "Bệnh", "viện"), nên cùng một thực thể có cùng tọa độ ở mọi mô hình.

Đầu ra (results/phan_tich_loi/): bang_nhom_loi.csv/.md, ma_tran_nham_loai.csv, loi_chung_rieng.md,
vi_du_<nhom>.csv (câu thật), hinh_nhom_loi.png, tom_tat.md
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

THU_MUC_SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC_SRC)
from data import THU_MUC_GOC, lay_thuc_the, tai_du_lieu  # noqa: E402

import pandas as pd  # noqa: E402

THU_MUC_RA = os.path.join(THU_MUC_GOC, "results", "phan_tich_loi")
TEN = {"phobert": "PhoBERT", "xlmr": "XLM-R", "mbert": "mBERT", "crf": "CRF", "zeroshot": "Zero-shot", "phobert_khong_tach_tu": "PhoBERT-không-tách-từ"}
NHOM_LOI = ["Sai loại", "Sai biên", "Sai cả hai", "Bỏ sót", "Dự đoán thừa"]
TEN_FILE = {"Sai loại": "sai_loai", "Sai biên": "sai_bien", "Sai cả hai": "sai_ca_hai", "Bỏ sót": "bo_sot",
            "Dự đoán thừa": "du_doan_thua"}
LOAI_DAC_THU = ["PATIENT_ID", "ORGANIZATION", "JOB", "SYMPTOM_AND_DISEASE"]


def tu_sang_am_tiet(cac_tu):
    """Chỉ số âm tiết bắt đầu của từng từ + tổng số âm tiết. 'Bệnh_viện' = 2 âm tiết."""
    dau, n = [], 0
    for tu in cac_tu:
        dau.append(n)
        n += len(tu.split("_"))
    return dau, n


def thuc_the_am_tiet(nhan, cac_tu=None):
    """Tập thực thể (loai, dau, cuoi) theo vị trí ÂM TIẾT. cac_tu=None nghĩa là dữ liệu đã ở mức âm tiết."""
    tt = lay_thuc_the(nhan)
    if cac_tu is None:
        return set(tt)
    dau, _ = tu_sang_am_tiet(cac_tu)
    return {(l, dau[s], dau[e] + len(cac_tu[e].split("_")) - 1) for l, s, e in tt}


def chong_lan(a, b):
    return a[1] <= b[2] and b[1] <= a[2]


def phan_loai_loi(vang, doan):
    """vang, doan: tập (loai, dau, cuoi). Trả về list (nhom_loi, thuc_the_vang | None, thuc_the_doan | None)."""
    loi = []
    for g in sorted(vang - doan, key=lambda x: (x[1], x[2], x[0])):
        cac_p = [p for p in doan if chong_lan(g, p)]
        if not cac_p:
            loi.append(("Bỏ sót", g, None))
            continue
        # chọn dự đoán khớp nhất (ưu tiên: trùng biên > chồng lấn nhiều > cùng loại > đứng trước) -> kết quả cố định
        p = max(cac_p, key=lambda p: ((p[1], p[2]) == (g[1], g[2]), min(g[2], p[2]) - max(g[1], p[1]), p[0] == g[0], -p[1]))
        cung_bien, cung_loai = (g[1], g[2]) == (p[1], p[2]), g[0] == p[0]
        loi.append(("Sai loại" if cung_bien else "Sai biên" if cung_loai else "Sai cả hai", g, p))
    for p in sorted(doan - vang, key=lambda x: (x[1], x[2], x[0])):
        if not any(chong_lan(p, g) for g in vang):
            loi.append(("Dự đoán thừa", None, p))
    return loi


# File dự đoán test của Phúc (notebook Baseline_CRF_ZeroShot) có khóa crf_tach_tu (mức từ) và zero_shot (âm tiết)
FILE_CRF_ZEROSHOT = ["results/du_doan/du_doan_test.json", "results/phan_tich/du_doan_test.json", "ket_qua/du_doan_test.json",
                     "results/du_doan_test.json"]
KHOA_PHUC = {"crf": ("crf_tach_tu", "word"), "zeroshot": ("zero_shot", "syllable")}


def doc_du_doan(khoa, seed):
    """Đọc dự đoán test của 1 mô hình. Fine-tune: results/du_doan/{khoa}_seed{seed}.json (train_ner.py ghi).
    CRF / zero-shot (chỉ 1 lượt, không có seed): đọc từ file du_doan_test.json của Phúc."""
    p = os.path.join(THU_MUC_GOC, "results", "du_doan", f"{khoa}_seed{seed}.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    if khoa in KHOA_PHUC:
        for f in FILE_CRF_ZEROSHOT:
            f = os.path.join(THU_MUC_GOC, f)
            if os.path.exists(f):
                d = json.load(open(f, encoding="utf-8"))
                khoa_file, muc = KHOA_PHUC[khoa]
                if khoa_file in d:
                    return {"khoa_mo_hinh": khoa, "muc_du_lieu": muc, "du_doan": d[khoa_file]}
    return None


def to_dam(cac_am_tiet, dau, cuoi):
    return " ".join(cac_am_tiet[:dau] + ["【" + " ".join(cac_am_tiet[dau:cuoi + 1]) + "】"] + cac_am_tiet[cuoi + 1:])


def main(seed=42, cac_khoa=("crf", "zeroshot", "phobert", "xlmr", "mbert"), so_vi_du=5):
    du_lieu = {"word": tai_du_lieu("word")["test"], "syllable": tai_du_lieu("syllable")["test"]}
    cau_am_tiet, nhan_am_tiet = du_lieu["syllable"]
    vang = [thuc_the_am_tiet(n) for n in nhan_am_tiet]             # nhãn thật, quy về âm tiết
    os.makedirs(THU_MUC_RA, exist_ok=True)

    dem, nham_loai, loi_cua = {}, {}, {}
    vi_du = defaultdict(list)
    for khoa in cac_khoa:
        dd = doc_du_doan(khoa, seed)
        if dd is None:
            print(f"  (bỏ qua {khoa}: chưa có results/du_doan/{khoa}_seed{seed}.json)")
            continue
        muc = dd["muc_du_lieu"]
        cau_goc = du_lieu[muc][0]
        dem[khoa], nham_loai[khoa], loi_cua[khoa] = Counter(), Counter(), set()
        for i, nhan in enumerate(dd["du_doan"]):
            doan = thuc_the_am_tiet(nhan, cau_goc[i] if muc == "word" else None)
            for nhom, g, p in phan_loai_loi(vang[i], doan):
                dem[khoa][nhom] += 1
                if nhom == "Sai loại":
                    nham_loai[khoa][(g[0], p[0])] += 1
                if g is not None:
                    loi_cua[khoa].add((i, g))                        # thực thể thật mà model này làm sai
                if len(vi_du[(khoa, nhom)]) < 200:
                    tt = g or p
                    vi_du[(khoa, nhom)].append({"cau_so": i, "mo_hinh": TEN.get(khoa, khoa), "nhom_loi": nhom,
                                                 "that": f"{g[0]}: {' '.join(cau_am_tiet[i][g[1]:g[2] + 1])}" if g else "O",
                                                 "du_doan": f"{p[0]}: {' '.join(cau_am_tiet[i][p[1]:p[2] + 1])}" if p else "O",
                                                 "cau": to_dam(cau_am_tiet[i], tt[1], tt[2])})
    if not dem:
        print("Chưa có file dự đoán nào. Chạy notebook huấn luyện trước.")
        return

    # 1) Bảng số lỗi theo nhóm × mô hình
    tong_vang = sum(len(v) for v in vang)
    bang = pd.DataFrame([{"Nhóm lỗi": n, **{TEN[k]: dem[k][n] for k in dem}} for n in NHOM_LOI])
    bang.loc[len(bang)] = ["Tổng lỗi", *[sum(dem[k].values()) for k in dem]]
    bang.to_csv(os.path.join(THU_MUC_RA, "bang_nhom_loi.csv"), index=False, encoding="utf-8-sig")

    # 2) Ma trận nhầm loại (chỉ nhóm "Sai loại")
    dong = [{"Mô hình": TEN[k], "Thật → Dự đoán": f"{a} → {b}", "Số lần": c}
            for k in nham_loai for (a, b), c in nham_loai[k].most_common(8)]
    pd.DataFrame(dong).to_csv(os.path.join(THU_MUC_RA, "ma_tran_nham_loai.csv"), index=False, encoding="utf-8-sig")

    # 3) Lỗi chung / lỗi riêng: 3 kiến trúc có mắc CÙNG lỗi không?
    cac_k = [k for k in loi_cua if k in ("phobert", "xlmr", "mbert")] or list(loi_cua)   # so sánh 3 kiến trúc fine-tune
    chung_tat_ca = set.intersection(*[loi_cua[k] for k in cac_k]) if len(cac_k) > 1 else set()
    dong_cr = [f"- Thực thể thật bị **mọi** mô hình ({', '.join(TEN[k] for k in cac_k)}) làm sai: **{len(chung_tat_ca)}**"]
    for k in cac_k:
        rieng = loi_cua[k] - set().union(*[loi_cua[j] for j in cac_k if j != k])  # noqa: E501
        dong_cr.append(f"- Chỉ riêng {TEN[k]} sai: {len(rieng)} (tổng {TEN[k]} sai {len(loi_cua[k])})")
    loai_chung = Counter(g[0] for _, g in chung_tat_ca)
    dong_cr.append(f"- Loại thực thể hay bị cả {len(cac_k)} mô hình cùng sai: " + ", ".join(f"{l} ({c})" for l, c in loai_chung.most_common(5)))
    open(os.path.join(THU_MUC_RA, "loi_chung_rieng.md"), "w", encoding="utf-8").write("\n".join(dong_cr))

    # 4) Ví dụ thật cho từng nhóm lỗi (mỗi nhóm mỗi mô hình 1 file gộp)
    for nhom in NHOM_LOI:
        dong_vd = [x for k in dem for x in vi_du[(k, nhom)][:so_vi_du * 4]]
        pd.DataFrame(dong_vd).to_csv(os.path.join(THU_MUC_RA, f"vi_du_{TEN_FILE[nhom]}.csv"),
                                     index=False, encoding="utf-8-sig")

    # 5) Thực thể đặc thù: tỉ lệ sai theo loại
    sai_theo_loai = pd.DataFrame([{"Loại": l, "Số thực thể thật": sum(1 for v in vang for g in v if g[0] == l),
                                   **{TEN[k]: sum(1 for _, g in loi_cua[k] if g[0] == l) for k in loi_cua}}
                                  for l in LOAI_DAC_THU])
    sai_theo_loai.to_csv(os.path.join(THU_MUC_RA, "loi_thuc_the_dac_thu.csv"), index=False, encoding="utf-8-sig")

    # 6) Hình
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ax = bang[bang["Nhóm lỗi"] != "Tổng lỗi"].set_index("Nhóm lỗi").plot(kind="bar", figsize=(9, 4), rot=0)
    ax.set_ylabel("Số lỗi trên test")
    ax.set_title(f"Số lỗi theo nhóm và mô hình (seed {seed})")
    plt.tight_layout()
    plt.savefig(os.path.join(THU_MUC_RA, "hinh_nhom_loi.png"), dpi=200)
    plt.close()

    def md(df):
        cot = list(df.columns)
        return "\n".join(["| " + " | ".join(map(str, cot)) + " |", "|" + "---|" * len(cot)] +
                         ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)])
    tom_tat = [f"# Tóm tắt phân tích lỗi (test, seed {seed}; {tong_vang} thực thể thật)", "", "## Số lỗi theo nhóm", md(bang),
               "", "## Nhầm loại hay gặp nhất", md(pd.DataFrame(dong)) if dong else "(không có)",
               "", "## Lỗi chung và lỗi riêng", *dong_cr, "", "## Thực thể đặc thù", md(sai_theo_loai)]
    open(os.path.join(THU_MUC_RA, "tom_tat.md"), "w", encoding="utf-8").write("\n".join(tom_tat))
    open(os.path.join(THU_MUC_RA, "bang_nhom_loi.md"), "w", encoding="utf-8").write(md(bang))
    print("\n".join(tom_tat))
    print(f"\nĐã ghi kết quả vào {THU_MUC_RA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mo_hinh", nargs="+", default=["crf", "zeroshot", "phobert", "xlmr", "mbert"])
    a = ap.parse_args()
    main(a.seed, a.mo_hinh)
