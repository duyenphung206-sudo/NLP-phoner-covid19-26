# notebooks/ — quy ước đặt tên

`NN_noi-dung_ten.ipynb` · `NN` là số thứ tự theo luồng công việc, `ten` là `phuc | duyen | tam | trinh`.

| File | Nội dung | Người | Issue |
|---|---|---|---|
| `00_setup_<ten>.ipynb` | Kiểm tra GPU + đọc được dữ liệu | mỗi người | T03–T06 |
| `01_baseline-crf-zeroshot_phuc.ipynb` | Baseline CRF + zero-shot (đã xong) | Phúc | T03, T12, T14 |
| `02_eda_tam.ipynb` | Thống kê dữ liệu, độ dài câu, số subword | Đức Tâm | T11 |
| `03_train-phobert_duyen.ipynb` | Gọi `src/train_ner.py` cho PhoBERT × 3 seed | Hoàng Duyên | T15 |
| `04_train-xlmr_tam.ipynb` | XLM-R × 3 seed | Đức Tâm | T16 |
| `05_train-mbert_trinh.ipynb` | mBERT × 3 seed | Yến Trinh | T17 |
| `06_tong-hop-ket-qua_duyen.ipynb` | Bảng mean ± std, biểu đồ | Hoàng Duyên | T20 |

**Trước khi commit notebook:** Runtime → *Restart and run all* để chắc chạy từ đầu không lỗi; xóa output quá dài (in cả nghìn dòng).
Trên Colab, lưu checkpoint vào Google Drive chung (`/content/drive/MyDrive/NLP_De26/checkpoints/`), **không** lưu vào repo.
