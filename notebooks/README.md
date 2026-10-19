# notebooks/ — chạy ở đâu, ai chạy, ra file gì

`NN_noi-dung_ten.ipynb` · `NN` là thứ tự theo luồng công việc, `ten` là `phuc | duyen | tam | trinh`.
Mọi notebook **tự ghi code của nhóm** (`%%writefile`) và **tự tải dữ liệu công khai của VinAI** → không cần token GitHub, không cần clone repo trên Colab.

| File | Nội dung | Chạy ở đâu | Người | Issue | Ra file |
|---|---|---|---|---|---|
| `00_setup_<ten>.ipynb` | Kiểm tra GPU, thư viện, dữ liệu, seed, tokenizer | Colab GPU | mỗi người | T03–T06 | `results/moi_truong/<ten>.json` |
| `01_baseline-crf-zeroshot_phuc.ipynb` | Baseline CRF + zero-shot (đã xong) | Colab | Phúc | T12, T14 | `results/crf.json`, `zeroshot.json` |
| `02_eda_tam.ipynb` | Thống kê dữ liệu, độ dài, subword 3 tokenizer, NFC, thực thể mới | Colab (CPU được) | Đức Tâm | T11 | `results/eda/*` |
| `03_train-phobert_duyen.ipynb` | Grid + Random Search (4.3) → PhoBERT × 3 seed | **Colab GPU T4** | Hoàng Duyên | T15 | `results/phobert_seed*.json`, `results/du_doan/`, `results/tim_kiem/` |
| `04_train-xlmr_tam.ipynb` | như trên cho XLM-R | **Colab GPU T4** | Đức Tâm | T16 | `results/xlmr_*` |
| `05_train-mbert_trinh.ipynb` | như trên cho mBERT | **Colab GPU T4** | Yến Trinh | T17 | `results/mbert_*` |
| `06_tong-hop-ket-qua_duyen.ipynb` | `aggregate.py` (mean ± std, kiểm định, biểu đồ) + `phan_tich_loi.py` | **VS Code** (không cần GPU) | Duyên, Tâm | T20, T27, T31 | `results/tong_hop/*`, `results/phan_tich_loi/*` |

Nâng cao (Phúc, T29): mở notebook 03, đổi `KHOA = "phobert_khong_tach_tu"`, **bỏ qua ô 7** (không tìm lại siêu tham số) và đặt
`CAU_HINH_TOT = <cấu hình tốt nhất của phobert>` (đọc từ `results/tim_kiem/phobert_*.json`) → hai điều kiện chỉ khác đúng đầu vào.

**Trước khi commit notebook:** xóa output quá dài (Edit → Clear all outputs nếu cần). Checkpoint/mô hình lưu ở Google Drive `NLP_De26/`, **không** vào repo.
