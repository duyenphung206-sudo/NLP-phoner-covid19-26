"""xuat_du_doan.py - Gộp dự đoán test của mọi mô hình vào 1 file CSV dễ đọc (Issue T27, đầu vào cho T31–T35).

Người phụ trách: Hoàng Duyên · Chạy trên máy (VS Code), không cần GPU:   python src/xuat_du_doan.py --seed 42
Đầu ra: results/du_doan/predictions_test.csv — 3.000 dòng (1 dòng = 1 câu test), các cột:
  cau_so | cau (âm tiết) | that | crf | zeroshot | phobert | xlmr | mbert | so_mo_hinh_sai
Mỗi ô là danh sách thực thể "LOẠI: văn bản" nối bằng " ; ". Mô hình mức từ (PhoBERT, CRF) được quy về âm tiết
("Bệnh_viện" = 2 âm tiết) để mọi cột cùng đơn vị.
"""

import argparse
import os
import sys

THU_MUC_SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC_SRC)
from data import THU_MUC_GOC, tai_du_lieu  # noqa: E402
from phan_tich_loi import TEN, doc_du_doan, thuc_the_am_tiet  # noqa: E402

import pandas as pd  # noqa: E402


def dinh_dang(tap_tt, cac_am_tiet):
    return " ; ".join(f"{l}: {' '.join(cac_am_tiet[s:e + 1])}" for l, s, e in sorted(tap_tt, key=lambda x: (x[1], x[2])))


def main(seed=42, cac_khoa=("crf", "zeroshot", "phobert", "xlmr", "mbert")):
    tu, am = tai_du_lieu("word")["test"], tai_du_lieu("syllable")["test"]
    cau_am, nhan_am = am
    vang = [thuc_the_am_tiet(n) for n in nhan_am]
    cot = {}
    for khoa in cac_khoa:
        dd = doc_du_doan(khoa, seed)
        if dd is None:
            print(f"  (bỏ qua {khoa}: chưa có file dự đoán)")
            continue
        if len(dd["du_doan"]) != len(cau_am):
            raise ValueError(f"{khoa}: có {len(dd['du_doan'])} câu, mong đợi {len(cau_am)}")
        cot[khoa] = [thuc_the_am_tiet(n, tu[0][i] if dd["muc_du_lieu"] == "word" else None)
                     for i, n in enumerate(dd["du_doan"])]
    dong = []
    for i in range(len(cau_am)):
        r = {"cau_so": i, "cau": " ".join(cau_am[i]), "that": dinh_dang(vang[i], cau_am[i])}
        for k, v in cot.items():
            r[k] = dinh_dang(v[i], cau_am[i])
        r["so_mo_hinh_sai"] = sum(v[i] != vang[i] for v in cot.values())
        dong.append(r)
    df = pd.DataFrame(dong)
    ra = os.path.join(THU_MUC_GOC, "results", "du_doan", "predictions_test.csv")
    os.makedirs(os.path.dirname(ra), exist_ok=True)
    df.to_csv(ra, index=False, encoding="utf-8-sig")
    print(f"Đã ghi {len(df)} câu × {len(cot)} mô hình ({', '.join(TEN.get(k, k) for k in cot)}) -> {ra}")
    print("Số câu mọi mô hình đều đúng:", int((df["so_mo_hinh_sai"] == 0).sum()))
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    main(ap.parse_args().seed)
