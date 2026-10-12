"""aggregate.py - Gộp các file results/*.json thành bảng so sánh mean ± std.

Người phụ trách: Hoàng Duyên · Issue T20 (bản đầu, hạn 19/10) → T27 (bản đầy đủ, sau BC1)
Cách chạy: python src/aggregate.py
Đầu ra   : results/bang_tong_hop.csv và in bảng Markdown để dán vào báo cáo.

Quy ước: std MẪU (chia n-1) = numpy.std(x, ddof=1). CRF và zero-shot chỉ có 1 lượt -> không có std.
Bỏ qua file bắt đầu bằng "_" (file mẫu).
"""

import glob
import json
import os

import numpy as np
import pandas as pd


def doc_tat_ca(thu_muc="results"):
    """Đầu ra: list dict - mỗi dict là 1 file kết quả (không tính file bắt đầu bằng "_")."""
    ds = []
    for duong_dan in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        if os.path.basename(duong_dan).startswith("_"):
            continue
        with open(duong_dan, encoding="utf-8") as f:
            ds.append(json.load(f))
    return ds


def gop_mean_std(ds):
    """Nhóm theo khoa_mo_hinh (CRF/zero-shot dùng ten_mo_hinh), tính mean ± std của f1_micro, f1_macro.
    Đầu ra: DataFrame 1 dòng / phương pháp."""
    # TODO (Duyên): nhóm, tính np.mean và np.std(ddof=1) khi có >= 2 seed; ghi số seed đã có
    raise NotImplementedError("TODO - Duyên (T20)")


if __name__ == "__main__":
    bang = gop_mean_std(doc_tat_ca())
    bang.to_csv(os.path.join("results", "bang_tong_hop.csv"), index=False, encoding="utf-8-sig")
    print(bang.to_markdown(index=False))
