# Quy ước chung ("hợp đồng chung") — Đề 26

> Mục đích: 3 kiến trúc chỉ khác nhau ở **mô hình**, mọi thứ khác giống hệt nhau → so sánh mới công bằng (cô sẽ hỏi điểm này khi phản biện).
> Giá trị máy đọc nằm trong [`configs/common.json`](../configs/common.json). Trang này giải thích **vì sao** và ghi lại **lịch sử thay đổi**.

**Trạng thái:** ĐỀ XUẤT — chốt ở buổi họp 12/10/2026 (ghi kết quả vào mục 5).

## 1. Dữ liệu

| Mục | Quy ước |
|---|---|
| Nguồn | Repo VinAI `PhoNER_COVID19`, giữ nguyên cách chia train 5.027 / dev 2.000 / test 3.000 câu |
| Bản mức từ (`data/word`) | Đã tách từ bằng RDRSegmenter (VnCoreNLP) — dùng cho **PhoBERT**, **CRF** |
| Bản âm tiết (`data/syllable`) | Dùng cho **XLM-R**, **mBERT**, **zero-shot**, **PhoBERT không tách từ** (nâng cao) |
| Nhãn | 21 nhãn BIO theo đúng thứ tự trong `configs/common.json` (tên thật: `NAME`, `JOB`, `SYMPTOM_AND_DISEASE`…) |
| Tự tách lại bằng underthesea | **Không** dùng để train/đánh giá (lệch ranh giới thực thể); chỉ dùng cho câu nhập ở demo nếu cần |

## 2. Chấm điểm

| Mục | Quy ước | Lý do |
|---|---|---|
| Thư viện | `seqeval` qua `src/metrics.py` → hàm `tinh_metrics()` (Phúc) | Mọi người dùng chung 1 hàm |
| Chế độ | `mode="strict"`, `scheme=IOB2` | Thực thể đúng khi đúng cả ranh giới và loại; giống cách chấm của bài báo |
| Chỉ số | Micro-F1 (chính), Macro-F1, P/R, F1 từng loại | Đề yêu cầu F1 theo từng loại |
| Chọn checkpoint | Micro-F1 cao nhất trên **dev** | Test chỉ dùng để báo cáo, không chỉnh theo test |
| mean ± std | Qua 3 seed, std **mẫu** (`ddof=1`) | Ghi rõ trong báo cáo |
| CRF, zero-shot | 1 lượt, không có std | Không có yếu tố ngẫu nhiên đáng kể |

## 3. Huấn luyện

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Seed | 42, 123, 2024 | Đặt `set_seed(seed)` **trước** khi tạo model |
| Learning rate | 5e-5 | Theo bài báo |
| Batch | 16 × gradient accumulation 2 = 32 | Vừa GPU T4 của Colab |
| Epoch tối đa / dừng sớm | 15 / 3 | Bài báo 30 / 5; giảm để kịp 3 seed trước 18/10 |
| max_length | 256 | Giới hạn của PhoBERT; ghi số câu bị cắt (lấy từ EDA) |
| fp16 | Bật | Nhanh hơn, ít bộ nhớ hơn |
| Model | `vinai/phobert-base` · `xlm-roberta-base` · `bert-base-multilingual-cased` | mBERT dùng bản **cased** (bản uncased bỏ dấu tiếng Việt) |
| Script | `src/train_ner.py` cho cả 3 | Chỉ đổi `--mo_hinh` |

## 4. Lưu trữ

| Thứ | Để ở đâu |
|---|---|
| File JSON kết quả | `results/{khoa_mo_hinh}_seed{seed}.json` — commit lên repo |
| Checkpoint | Google Drive chung `NLP_De26/checkpoints/{khoa_mo_hinh}_seed{seed}/` — **không** commit |
| Dữ liệu | Máy/Colab của từng người, thư mục `data/` — **không** commit |
| Báo cáo đang viết | OneDrive/Google Drive (sửa chung); bản đã nộp đưa vào `reports/` |

## 5. Lịch sử thay đổi

| Ngày | Thay đổi | Lý do | Ai đồng ý |
|---|---|---|---|
| 12/10/2026 | Khởi tạo bản đề xuất | — | (điền sau buổi họp) |
