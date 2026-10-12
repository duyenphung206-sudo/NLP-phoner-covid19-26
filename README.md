# Nhận dạng thực thể tiếng Việt về COVID-19 (PhoNER_COVID19)

**Đồ án cuối kỳ môn Xử lý Ngôn ngữ Tự nhiên — Đề tài 26 · HUFLIT · HK1 2026–2027**

So sánh 5 cách làm NER trên tin tức tiếng Việt về COVID-19 (10 loại thực thể: mã bệnh nhân, tuổi, địa điểm, tổ chức y tế…):
**(A)** baseline CRF · **(B)** zero-shot bằng model NER có sẵn · **(C)** fine-tune PhoBERT, XLM-R, mBERT (mỗi kiến trúc 3 seed, báo cáo mean ± std) · **(D)** demo Gradio · **Nâng cao:** PhoBERT có và không có bước tách từ.

> 📌 **Mốc gần nhất: nộp Báo cáo tiến độ lần 1 ngày 22/10/2026.**
> Xem tiến độ: [**Milestone BC1**](../../milestones) · [**Bảng Project**](../../projects) · [**Việc của tôi**](../../issues/assigned/@me) · [Kế hoạch chi tiết](docs/KE_HOACH_BC1.md)

---

## Mục lục
- [Thành viên và vai trò](#thành-viên-và-vai-trò)
- [Kết quả hiện tại](#kết-quả-hiện-tại)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Quy trình làm việc của nhóm](#quy-trình-làm-việc-của-nhóm)
- [Dữ liệu và giấy phép](#dữ-liệu-và-giấy-phép)
- [Tài liệu tham khảo](#tài-liệu-tham-khảo)

## Thành viên và vai trò

| Vai trò (theo đề) | Thành viên | GitHub | Phụ trách chính |
|---|---|---|---|
| 1 · Baseline (A) + Zero-shot (B) | Phúc | @… | CRF, zero-shot, `src/metrics.py`; sau BC1: Yêu cầu nâng cao |
| 2 · Kiến trúc 1 — PhoBERT-base | Phùng Thị Hoàng Duyên | @duyenphung206-sudo | `src/train_ner.py` dùng chung, PhoBERT × 3 seed, tổng hợp kết quả |
| 3 · Kiến trúc 2 — XLM-RoBERTa-base | Đức Tâm | @… | `src/data.py`, EDA, XLM-R × 3 seed, phân tích lỗi |
| 4 · Kiến trúc 3 — mBERT-cased + Demo (D) | Yến Trinh | @… | Tóm tắt bài báo, mBERT × 3 seed, demo Gradio |

## Kết quả hiện tại

Chấm trên tập **test**, F1 mức thực thể bằng `seqeval` (`mode="strict"`, `scheme=IOB2`). Nguồn số: các file trong [`results/`](results/).

| Phương pháp | Đầu vào | Micro-F1 | Macro-F1 | Người chạy | Trạng thái |
|---|---|---|---|---|---|
| (A) CRF, c1 = c2 = 0,05 | mức từ | 0,9199 | 0,8771 | Phúc | ✅ xong |
| (B) Zero-shot `NlpHUST/ner-vietnamese-electra-base` | âm tiết | 0,4760 | 0,1996 | Phúc | ✅ xong |
| (C) PhoBERT-base | mức từ | … ± … | … ± … | Hoàng Duyên | ⏳ hạn 18/10 |
| (C) XLM-R-base | âm tiết | … ± … | … ± … | Đức Tâm | ⏳ hạn 18/10 |
| (C) mBERT-cased | âm tiết | … ± … | … ± … | Yến Trinh | ⏳ hạn 18/10 |

## Cấu trúc thư mục

```
nlp-de26-phoner-covid19/
├── configs/common.json        # "Hợp đồng chung": nhãn, seed, siêu tham số, tên model
├── data/                      # Dữ liệu PhoNER_COVID19 (KHÔNG commit, xem data/README.md)
├── src/
│   ├── metrics.py             # Chấm F1 dùng chung (Phúc)
│   ├── data.py                # Đọc dữ liệu, label2id (Đức Tâm)
│   ├── train_ner.py           # Fine-tune dùng chung cho 3 kiến trúc (Hoàng Duyên)
│   └── aggregate.py           # Gộp kết quả thành mean ± std (Hoàng Duyên)
├── notebooks/                 # Notebook Colab, đặt tên NN_noi-dung_ten.ipynb
├── results/                   # File JSON kết quả mỗi lượt chạy + phan_tich/
├── app/                       # Demo Gradio (Yến Trinh, sau BC1)
├── reports/                   # Bản báo cáo đã nộp (BC1, BC2, cuối kỳ)
├── docs/                      # Hướng dẫn, quy ước, kế hoạch, biên bản họp
├── plan/                      # Kế hoạch dạng JSON để tạo Issue tự động
└── .github/                   # Mẫu Issue/PR, workflow tạo Issue
```

## Bắt đầu nhanh

**Trên Google Colab** (cell đầu tiên của mỗi notebook):

```python
# 1) Lấy code của nhóm (repo private: dùng token cá nhân, xem docs/HUONG_DAN_2_THANH_VIEN.md mục E)
!git clone https://github.com/duyenphung206-sudo/nlp-de26-phoner-covid19.git
%cd nlp-de26-phoner-covid19
!pip install -q -r requirements.txt

# 2) Tải dữ liệu vào data/ (không commit)
!git clone -q https://github.com/VinAIResearch/PhoNER_COVID19.git /content/PhoNER_COVID19
!cp -r /content/PhoNER_COVID19/data/word /content/PhoNER_COVID19/data/syllable data/

# 3) Kiểm tra hàm chấm điểm
!python src/metrics.py
```

## Quy trình làm việc của nhóm

1. Mỗi việc là **1 Issue** (`T01`…`T26`, gắn Milestone **BC1**), có sẵn *Đầu vào – Đầu ra – Xong khi*.
2. Làm trên **nhánh riêng** `ten/Txx-mo-ta` (ví dụ `tam/T07-data-py`), không làm thẳng trên `main`.
3. Xong thì mở **Pull Request** có dòng `Closes #<số issue>` → 1 bạn khác review → merge → Issue tự đóng, thanh % của Milestone tự tăng.
4. Mỗi tối comment 3 dòng vào Issue đang làm: *Đã xong / Mai làm / Đang vướng*.

Chi tiết: [CONTRIBUTING.md](CONTRIBUTING.md) · [Hướng dẫn cho thành viên](docs/HUONG_DAN_2_THANH_VIEN.md) · [Quy ước chung](docs/QUY_UOC_CHUNG.md)

## Dữ liệu và giấy phép

Dữ liệu **PhoNER_COVID19** (VinAI Research) chỉ được dùng cho nghiên cứu/học tập, **không được phát tán lại**. Vì vậy repo này để **private** và **không chứa file dữ liệu**; xem cách tải ở [`data/README.md`](data/README.md).

## Tài liệu tham khảo

1. T. H. Truong, M. H. Dao, and D. Q. Nguyen, "COVID-19 named entity recognition for Vietnamese," in *Proc. NAACL-HLT*, 2021. https://aclanthology.org/2021.naacl-main.173/
2. D. Q. Nguyen and A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," in *Findings of EMNLP*, 2020.
3. A. Conneau *et al.*, "Unsupervised cross-lingual representation learning at scale," in *Proc. ACL*, 2020.
4. J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," in *Proc. NAACL-HLT*, 2019.
