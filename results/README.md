# results/ — kết quả của mọi lượt chạy

Mỗi lượt chạy = **1 file JSON** (nhỏ, được commit). Checkpoint mô hình KHÔNG để ở đây (lưu Google Drive chung).

| File | Nội dung | Người | Trạng thái |
|---|---|---|---|
| `crf.json` | Baseline CRF (A) | Phúc | ✅ có (đưa lên ở T03) |
| `zeroshot.json` | Zero-shot (B) | Phúc | ✅ có (đưa lên ở T03) |
| `phobert_seed{42,123,2024}.json` | PhoBERT-base, bản mức từ | Hoàng Duyên | hạn 18/10 |
| `xlmr_seed{42,123,2024}.json` | XLM-R-base, bản âm tiết | Đức Tâm | hạn 18/10 |
| `mbert_seed{42,123,2024}.json` | mBERT-cased, bản âm tiết | Yến Trinh | hạn 18/10 |
| `phobert_khong_tach_tu_seed{…}.json` | Nâng cao: PhoBERT không tách từ | Phúc | sau BC1 |
| `bang_tong_hop.csv` | Bảng mean ± std do `src/aggregate.py` sinh ra | Hoàng Duyên | hạn 19/10 |
| `phan_tich/` | File CSV phân tích lỗi, dự đoán (phục vụ phân tích lỗi chung) | mọi người | — |

**Định dạng bắt buộc:** giống [`_MAU_ket_qua_finetune.json`](_MAU_ket_qua_finetune.json) — 8 trường đầu lấy nguyên từ `metrics.tinh_metrics()` của Phúc, phần sau do `train_ner.py` ghi thêm (seed, model, siêu tham số, thời gian, phiên bản thư viện).

**Chấm điểm:** `seqeval`, `mode="strict"`, `scheme=IOB2`, trên tập **test**; chọn checkpoint theo `f1_micro` trên **dev**.
