# results/ — kết quả của mọi lượt chạy (file nhỏ, được commit)

Checkpoint và mô hình KHÔNG để ở đây (Google Drive `NLP_De26/`). Dữ liệu gốc KHÔNG để ở đây.

| Đường dẫn | Nội dung | Ai tạo (bằng gì) |
|---|---|---|
| `crf.json`, `zeroshot.json` | Baseline CRF (A), zero-shot (B) | Phúc (notebook 01) |
| `phobert_seed{42,123,2024}.json` | PhoBERT-base mức từ — điểm test + dev, siêu tham số, môi trường, thời gian | Duyên (notebook 03 / `train_ner.py`) |
| `xlmr_seed*.json`, `mbert_seed*.json` | XLM-R-base, mBERT-cased (âm tiết) | Tâm (04), Trinh (05) |
| `phobert_khong_tach_tu_seed*.json` | Nâng cao: PhoBERT trên bản âm tiết | Phúc |
| `du_doan/<khoa>_seed<seed>.json` | Nhãn dự đoán trên test (chỉ chuỗi nhãn, không có câu) → đầu vào phân tích lỗi | `train_ner.py` tự ghi |
| `du_doan/du_doan_test.json` | Dự đoán test của CRF và zero-shot (Phúc chép từ `ket_qua/`) | Phúc |
| `tim_kiem/<khoa>_{grid,random}.json` | Bảng Grid Search / Random Search trên dev (mục 4.3) | `train_ner.py` |
| `eda/` | Bảng + hình khám phá dữ liệu (mục 3.1–3.2) | Tâm (`src/eda.py`) |
| `tong_hop/` | Bảng mean ± std, theo seed, F1 từng loại, kiểm định, 2 biểu đồ (mục 5.3) | Duyên (`src/aggregate.py`) |
| `phan_tich_loi/` | 5 nhóm lỗi × mô hình, nhầm loại, lỗi chung/riêng, ví dụ, hình (mục 5.4) | Tâm (`src/phan_tich_loi.py`) |
| `_MAU_ket_qua_finetune.json` | Mẫu định dạng | — |

**Chấm điểm:** seqeval, `mode="strict"`, `scheme=IOB2`, trên **test**; chọn checkpoint theo `f1_micro` trên **dev**; std mẫu (n−1).
File bắt đầu bằng `_` và lượt `thu_nhanh` bị `aggregate.py` bỏ qua.
