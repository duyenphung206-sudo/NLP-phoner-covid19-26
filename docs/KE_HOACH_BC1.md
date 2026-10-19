# Kế hoạch đến Báo cáo tiến độ 1 (12/10 → 22/10/2026)

> Bản chính là file `PhanCong_NLP_De26_v3.xlsx` của nhóm; trang này là bản rút gọn để xem nhanh trên GitHub.
> Mỗi dòng ứng với 1 Issue có cùng mã `T..`. Tiến độ thật xem ở **Issues → Milestones → BC1**.

## Mốc chính

| Ngày | Mốc |
|---|---|
| Thứ 2, 12/10 | Repo GitHub sẵn sàng (Milestone BC1 + Issue + Project) · họp online chốt lịch mới |
| Thứ 3, 13/10 | data.py + môi trường của 4 người xong; ai cũng đã mở được 1 Pull Request |
| Thứ 7, 17/10 | Đưa gói code + notebook (train_ner, eda, phân tích lỗi, Streamlit) lên repo; bản nháp báo cáo các mục của Duyên/Tâm/Trinh |
| Chủ nhật, 18/10 | EDA (Tâm) xong · 3 người chạy thử + Grid Search |
| Thứ 2, 19/10 | Random Search + 3 seed × 3 kiến trúc xong, kết quả đã lên repo |
| Thứ 3, 20/10 | Bảng mean ± std sơ bộ (aggregate.py) · mọi người viết xong phần mình |
| Thứ 4, 21/10 | Ráp BC1 (sáng) · kiểm tra chéo (chiều) · họp rà soát (tối) |

## Bốn vai trò

| Vai trò | Người | Phụ trách chính |
|---|---|---|
| Vai trò 1 — Baseline (A) + Zero-shot (B) | Phúc | CRF (sklearn-crfsuite) + zero-shot bằng model NER tiếng Việt có sẵn; sau BC1: Yêu cầu nâng cao (PhoBERT có/không tách từ) |
| Vai trò 2 — Kiến trúc 1: PhoBERT-base | Hoàng Duyên | Fine-tune PhoBERT (bản mức từ) × 3 seed |
| Vai trò 3 — Kiến trúc 2: XLM-RoBERTa-base | Đức Tâm | Fine-tune XLM-R (bản âm tiết) × 3 seed |
| Vai trò 4 — Kiến trúc 3: mBERT-cased + Demo (D) | Yến Trinh | Fine-tune mBERT (bản âm tiết) × 3 seed + demo Streamlit (yêu cầu của cô) với mô hình tốt nhất |

## Danh sách việc

| Mã | Người | Việc | Bắt đầu → Hạn | Trạng thái lúc lập |
|---|---|---|---|---|
| T01 | Cả nhóm | Họp online 30 phút tối 12/10 (Hoàng Duyên chủ trì): chốt lịch mới 12/10 → 22/10, hợp đồng chung, cách làm việc trên GitHub | 12/10 → **12/10** | Xong |
| T02 | Hoàng Duyên | Tạo repo GitHub (private) + đưa bộ khung lên + mời 3 bạn + bật Project board + chạy workflow tạo Issue cho BC1 | 12/10 → **12/10** | Xong |
| T03 | Phúc | Setup + đưa phần baseline/zero-shot đã làm lên repo (qua Pull Request) | 12/10 → **13/10** | Đang làm |
| T04 | Hoàng Duyên | Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử | 12/10 → **13/10** | Xong |
| T05 | Đức Tâm | Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử | 12/10 → **13/10** | Chưa làm |
| T06 | Yến Trinh | Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử | 12/10 → **13/10** | Chưa làm |
| T07 | Đức Tâm | Viết data.py + file cấu hình chung (danh sách 21 nhãn, label2id cố định, đường dẫn 2 bản dữ liệu) | 12/10 → **18/10** | Đang làm |
| T08 | Phúc | Viết metrics.py: chấm F1 mức thực thể bằng seqeval (mode=strict, IOB2), micro/macro + F1 từng loại, lưu JSON | 01/10 → **12/10** | Xong |
| T09 | Yến Trinh | Tóm tắt bài báo nền tảng + mục tiêu đề tài bằng lời của nhóm | 12/10 → **14/10** | Chưa làm |
| T10 | Hoàng Duyên | Viết train_ner.py dùng chung cho cả 3 kiến trúc (căn nhãn subword, huấn luyện, chọn checkpoint theo dev, lưu JSON) | 13/10 → **17/10** | Đang làm |
| T11 | Đức Tâm | EDA: chạy notebooks/02_eda_tam.ipynb (src/eda.py) — thống kê, độ dài, subword 3 tokenizer, NFC, thực thể mới | 17/10 → **18/10** | Đang làm |
| T12 | Phúc | Baseline (A): CRF với đặc trưng từ (sklearn-crfsuite) | 01/10 → **12/10** | Xong |
| T13 | Yến Trinh | Viết Chương 2 – cơ sở lý thuyết: NER & nhãn BIO, Transformer/BERT, fine-tune vs zero-shot | 15/10 → **16/10** | Chưa làm |
| T14 | Phúc | Zero-shot (B): áp model NER tiếng Việt có sẵn, KHÔNG train lại | 01/10 → **12/10** | Xong |
| T15 | Hoàng Duyên | PhoBERT-base (mức từ): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất | 18/10 → **19/10** | Chưa làm |
| T16 | Đức Tâm | XLM-R-base (âm tiết): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất | 18/10 → **19/10** | Chưa làm |
| T17 | Yến Trinh | mBERT-cased (âm tiết): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất | 18/10 → **19/10** | Chưa làm |
| T18 | Phúc | Viết phần baseline + zero-shot vào báo cáo (kèm đoạn giải thích vì sao zero-shot yếu) | 13/10 → **15/10** | Chưa làm |
| T19 | Hoàng Duyên | Viết phần PhoBERT + quy trình huấn luyện chung vào báo cáo | 19/10 → **20/10** | Chưa làm |
| T20 | Hoàng Duyên | Chạy src/aggregate.py (VS Code) → bảng mean ± std sơ bộ 3 kiến trúc + kiểm định (làm hơn yêu cầu BC1) | 20/10 → **20/10** | Chưa làm |
| T21 | Đức Tâm | Viết phần XLM-R + tiền xử lý (bản âm tiết vs mức từ) vào báo cáo | 19/10 → **20/10** | Chưa làm |
| T22 | Yến Trinh | Viết phần mBERT vào báo cáo | 19/10 → **20/10** | Chưa làm |
| T23 | Yến Trinh | Ráp file Báo cáo tiến độ lần 1 (ngắn, đúng 5 mục theo thứ tự của cô) | 20/10 → **21/10** | Chưa làm |
| T24 | Đức Tâm | Kiểm tra chéo số liệu BC1: đối chiếu từng con số với file JSON / notebook | 21/10 → **21/10** | Chưa làm |
| T25 | Cả nhóm | Họp rà soát BC1 (45 phút, tối 21/10) | 21/10 → **21/10** | Chưa làm |
| T26 | Yến Trinh | NỘP Báo cáo tiến độ lần 1 | 22/10 → **22/10** | Chưa làm |

## Theo từng người

### Phúc
- [ ] **T03** (12/10 → 13/10): Setup + đưa phần baseline/zero-shot đã làm lên repo (qua Pull Request)
- [x] **T08** (01/10 → 12/10): Viết metrics.py: chấm F1 mức thực thể bằng seqeval (mode=strict, IOB2), micro/macro + F1 từng loại, lưu JSON
- [x] **T12** (01/10 → 12/10): Baseline (A): CRF với đặc trưng từ (sklearn-crfsuite)
- [x] **T14** (01/10 → 12/10): Zero-shot (B): áp model NER tiếng Việt có sẵn, KHÔNG train lại
- [ ] **T18** (13/10 → 15/10): Viết phần baseline + zero-shot vào báo cáo (kèm đoạn giải thích vì sao zero-shot yếu)

### Hoàng Duyên
- [x] **T02** (12/10 → 12/10): Tạo repo GitHub (private) + đưa bộ khung lên + mời 3 bạn + bật Project board + chạy workflow tạo Issue cho BC1
- [x] **T04** (12/10 → 13/10): Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử
- [ ] **T10** (13/10 → 17/10): Viết train_ner.py dùng chung cho cả 3 kiến trúc (căn nhãn subword, huấn luyện, chọn checkpoint theo dev, lưu JSON)
- [ ] **T15** (18/10 → 19/10): PhoBERT-base (mức từ): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất
- [ ] **T19** (19/10 → 20/10): Viết phần PhoBERT + quy trình huấn luyện chung vào báo cáo
- [ ] **T20** (20/10 → 20/10): Chạy src/aggregate.py (VS Code) → bảng mean ± std sơ bộ 3 kiến trúc + kiểm định (làm hơn yêu cầu BC1)

### Đức Tâm
- [ ] **T05** (12/10 → 13/10): Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử
- [ ] **T07** (12/10 → 18/10): Viết data.py + file cấu hình chung (danh sách 21 nhãn, label2id cố định, đường dẫn 2 bản dữ liệu)
- [ ] **T11** (17/10 → 18/10): EDA: chạy notebooks/02_eda_tam.ipynb (src/eda.py) — thống kê, độ dài, subword 3 tokenizer, NFC, thực thể mới
- [ ] **T16** (18/10 → 19/10): XLM-R-base (âm tiết): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất
- [ ] **T21** (19/10 → 20/10): Viết phần XLM-R + tiền xử lý (bản âm tiết vs mức từ) vào báo cáo
- [ ] **T24** (21/10 → 21/10): Kiểm tra chéo số liệu BC1: đối chiếu từng con số với file JSON / notebook

### Yến Trinh
- [ ] **T06** (12/10 → 13/10): Setup Colab/Kaggle + nhận lời mời repo + clone bằng GitHub Desktop + mở 1 Pull Request thử
- [ ] **T09** (12/10 → 14/10): Tóm tắt bài báo nền tảng + mục tiêu đề tài bằng lời của nhóm
- [ ] **T13** (15/10 → 16/10): Viết Chương 2 – cơ sở lý thuyết: NER & nhãn BIO, Transformer/BERT, fine-tune vs zero-shot
- [ ] **T17** (18/10 → 19/10): mBERT-cased (âm tiết): Grid Search + Random Search trên dev (mục 4.3) → 3 seed với cấu hình tốt nhất
- [ ] **T22** (19/10 → 20/10): Viết phần mBERT vào báo cáo
- [ ] **T23** (20/10 → 21/10): Ráp file Báo cáo tiến độ lần 1 (ngắn, đúng 5 mục theo thứ tự của cô)
- [ ] **T26** (22/10 → 22/10): NỘP Báo cáo tiến độ lần 1
