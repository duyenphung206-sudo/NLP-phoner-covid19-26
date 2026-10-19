# Sổ tay kỹ thuật — Đề 26 (PhoNER_COVID19)

> **Mục đích:** cô yêu cầu không chỉ *đọc* bài báo / dữ liệu mà phải **nắm được kỹ thuật bên trong**. File này liệt kê, cho từng
> tài liệu nhóm dùng: *kỹ thuật gì* → *nhóm dùng nó ở đâu trong code* → *bài giảng nào trên lớp nói về nó* → *câu hỏi phản biện hay gặp*.
>
> **Nguồn:** chỉ bài báo bình duyệt (ACL Anthology, JMLR, ICML…), tài liệu chính thức của tác giả (README GitHub, model card của
> chính tác giả trên Hugging Face), giáo trình *Speech and Language Processing* (Jurafsky & Martin, SLP3) và slide môn học
> (`NLP_LT/Session 1–6`). **Không** dùng nội dung do ChatGPT hay công cụ AI sinh ra làm nguồn. Mỗi con số dưới đây đều có nguồn
> ghi ngay bên cạnh — ai viết báo cáo thì **mở nguồn gốc ra kiểm tra lại** trước khi chép.
>
> Ai đọc phần nào: **Trinh** đọc §1–§4 (viết Chương 1–2, mBERT, demo) · **Tâm** đọc §1, §2, §5, §8 (dữ liệu, XLM-R, phân tích lỗi) ·
> **Duyên** đọc §3, §6, §7 (PhoBERT, huấn luyện, tìm siêu tham số, tổng hợp). Cả nhóm đọc §9 trước buổi bảo vệ.

---

## 1. Bài báo nền tảng — Truong, Dao & Nguyen (NAACL 2021), *COVID-19 Named Entity Recognition for Vietnamese*

Nguồn: https://aclanthology.org/2021.naacl-main.173/ · dữ liệu: https://github.com/VinAIResearch/PhoNER_COVID19

| Giai đoạn | Kỹ thuật bài báo dùng | Ý nghĩa (nói bằng lời của mình) |
|---|---|---|
| Thu thập | Lấy tin COVID-19 từ VnExpress, ZingNews, BaoMoi, ThanhNien (2–8/2020); dùng **BM25Plus** (một biến thể của hàm xếp hạng BM25 trong truy hồi thông tin) để chọn câu liên quan, ~15K câu → lọc còn **10.027 câu** | Không gán nhãn ngẫu nhiên mọi câu mà *truy hồi* câu có khả năng chứa thông tin ca bệnh → dữ liệu "đậm" thực thể |
| Định nghĩa nhãn | 10 loại thực thể **đặc thù miền** (PATIENT_ID, AGE, GENDER, JOB, SYMPTOM_AND_DISEASE, TRANSPORTATION, …) thay vì chỉ PER/LOC/ORG | Đây là lý do **zero-shot** bằng model NER tổng quát làm rất kém: model đó không hề biết 7/10 loại |
| Gán nhãn | Hướng dẫn gán nhãn (guideline) + pha thử với 2 người: độ đồng thuận mức thực thể **F1 = 0,88**; sau đó 10 người gán nhãn, mỗi người phải đạt ≥ 0,92 trên phần kiểm tra | **Inter-annotator agreement** đo chất lượng nhãn: nếu người còn bất đồng thì mô hình khó vượt ngưỡng đó |
| Biểu diễn nhãn | **BIO** (IOB2): 10 loại → 2·10 + 1 = **21 nhãn** | Slide Session 6: "For n entity types, BIO uses 2n + 1 labels" |
| Hai phiên bản | **Âm tiết** (gốc) và **mức từ** — tách từ bằng **RDRSegmenter** (VnCoreNLP) | Tiếng Việt: khoảng trắng tách *âm tiết*, không tách *từ* (Slide Session 2 & 6) |
| Mô hình | **BiLSTM-CNN-CRF** (CNN lấy đặc trưng ký tự, BiLSTM ngữ cảnh, CRF giải mã chuỗi), **XLM-R** (base/large, âm tiết), **PhoBERT** (base/large, mức từ) | So sánh "đặc trưng học từ đầu" với "mô hình pretrained", và đa ngữ với đơn ngữ |
| Huấn luyện | lr 5e-5, batch 32, tối đa 30 epoch, dừng sớm 5 epoch; kết quả **trung bình 5 lần chạy** (5 seed) | Báo cáo trung bình nhiều seed thay vì 1 lần chạy may mắn |
| Đánh giá | Micro-F1 và Macro-F1 mức thực thể trên test | Macro-F1 nhạy với loại hiếm (JOB, TRANSPORTATION) |
| Kết quả chính | PhoBERT-large 0,945 / 0,931 (mức từ) tốt nhất; PhoBERT-base 0,942 / 0,920; XLM-R-base 0,925 / 0,879 (âm tiết); BiLSTM-CNN-CRF 0,906 / 0,858 (âm tiết), 0,910 / 0,875 (mức từ) | (i) pretrained > BiLSTM-CNN-CRF; (ii) **tách từ tự động giúp** (mức từ ≥ âm tiết); (iii) PhoBERT đơn ngữ > XLM-R đa ngữ |
| Phân tích lỗi | Trên dev, PhoBERT-large còn 353 lỗi: 211 dự đoán thực thể ở chỗ nhãn thật là O (thường là địa điểm chung chung), 69 đúng biên sai loại (hay nhầm LOCATION ↔ ORGANIZATION, JOB), 65 đúng loại sai biên (tên tổ chức nhiều từ), 8 sai cả hai | Khung 4 nhóm lỗi này chính là khung **nhóm dùng lại** ở `src/phan_tich_loi.py` (thêm nhóm "bỏ sót") |

**Nhóm đã tự kiểm chứng (EDA):** số thực thể theo loại × tập khớp **từng ô** của Bảng 2 bài báo; tổng là **34.980**
(phần chữ của bài báo ghi 34.984 — lệch 4 so với chính bảng của bài báo). Đây là một chi tiết "đọc kỹ" đáng nêu trong báo cáo.

## 2. Dữ liệu và tiền xử lý tiếng Việt

| Kỹ thuật | Nguồn | Nhóm dùng ở đâu | Bài giảng |
|---|---|---|---|
| Chuẩn hóa Unicode **NFC** (dựng sẵn) — cùng chữ "ệ" có thể mã hóa 1 hoặc 2–3 code point | Unicode Standard Annex #15 | `src/data.py::chuan_hoa_nfc` (mỗi phiên bản có 1.052 token chưa NFC); `app/ner_core.py::chuan_hoa` | Session 2: "normalize to ONE single form… NFC… is the safe default… Vietnamese included" |
| **Tách từ** RDRSegmenter (luật dạng *Single Classification Ripple Down Rules*) | Nguyen et al., *A Fast and Accurate Vietnamese Word Segmenter*, LREC 2018; Vu et al., *VnCoreNLP*, NAACL 2018 Demo | Bản `data/word`; demo dùng `py_vncorenlp` (cùng công cụ với lúc tạo dữ liệu) | Session 2 slide 32 "Vietnamese word segmentation — directly relevant to the class project" |
| Định dạng mỗi dòng `{"words": [...], "tags": [...]}` | README PhoNER_COVID19 | `src/data.py::doc_file_json` | — |
| Ràng buộc hợp lệ của IOB2 (I-X phải đi sau B-X/I-X) | Ramshaw & Marcus 1995 (chunking); CoNLL-2003 | `kiem_tra_du_lieu` đếm nhãn I- đứng sai chỗ (= 0) | Session 6 |

## 3. Ba mô hình pretrained — khác nhau ở **dữ liệu pretrain** và **tokenizer**

| | PhoBERT-base | XLM-RoBERTa-base | mBERT-cased |
|---|---|---|---|
| Nguồn | Nguyen & Nguyen, *Findings of EMNLP 2020*; README `VinAIResearch/PhoBERT` | Conneau et al., *ACL 2020*; model card `xlm-roberta-base` | Devlin et al., *NAACL 2019*; `google-research/bert/multilingual.md` |
| Cách pretrain | RoBERTa (Liu et al., 2019): chỉ masked LM, bỏ NSP | RoBERTa đa ngữ, masked LM | BERT: masked LM + next-sentence prediction |
| Dữ liệu | **20 GB** tiếng Việt (Wikipedia + tin tức), **đã tách từ bằng RDRSegmenter** | **2,5 TB** CommonCrawl đã lọc, **100 ngôn ngữ** | Wikipedia của **104 ngôn ngữ** (lấy mẫu làm mượt mũ để ngôn ngữ ít dữ liệu không bị lấn át) |
| Tokenizer | **BPE** (fastBPE, ~64K đơn vị) trên văn bản đã tách từ | **SentencePiece** (~250K đơn vị) | **WordPiece** dùng chung ~110K–120K đơn vị, mảnh nối có tiền tố `##` |
| Số tham số | 135M (README) | ~270M (bài báo; model card ghi 0,3B) — phần lớn nằm ở bảng embedding 250K | README ghi 110M; thực tế cao hơn vì từ vựng đa ngữ lớn (embedding 119.547 × 768) |
| max length | **256** (README) | 512 | 512 |
| Đầu vào trong đề | `data/word` (bắt buộc đã tách từ — README: "INPUT TEXT MUST BE ALREADY WORD-SEGMENTED") | `data/syllable` | `data/syllable` |
| Vì sao chọn bản này | Đơn ngữ, khớp miền tiếng Việt | Đa ngữ mạnh nhất cỡ base | Bản **cased**: bản uncased *xóa dấu* (README Google) → "bệnh"/"bênh" thành một → vô dụng với tiếng Việt |

Bài giảng: Session 2 (BPE, WordPiece, SentencePiece; "BERT-base uses about 30,000 WordPiece tokens" — mBERT phải chia ~110K cho
hơn 100 ngôn ngữ nên tiếng Việt bị cắt vụn hơn → xem cột *Subword/token* trong `results/eda/subword.md`).

**Giả thuyết nhóm kiểm chứng:** (1) PhoBERT > XLM-R > mBERT vì lượng và độ "chuyên" của dữ liệu tiếng Việt khi pretrain;
(2) mBERT cắt từ tiếng Việt thành nhiều subword nhất → ngữ cảnh bị loãng, thực thể dài dễ sai biên; (3) bỏ tách từ làm PhoBERT tụt
vì lệch với cách nó được pretrain (yêu cầu nâng cao của Phúc).

## 4. Hai hướng không fine-tune: CRF và zero-shot

| Kỹ thuật | Nguồn | Ý chính | Bài giảng |
|---|---|---|---|
| **CRF tuyến tính** | Lafferty, McCallum & Pereira, ICML 2001; thư viện sklearn-crfsuite (CRFsuite, Okazaki 2007) | Mô hình xác suất **cả chuỗi nhãn** p(y\|x) ∝ exp(Σ đặc trưng·trọng số + điểm chuyển nhãn) → học được "I-LOC không đứng sau B-ORG"; c1/c2 = phạt L1/L2 | Session 6: "A CRF layer can score entire tag sequences and learn transition… sequence-aware decoding" |
| **Zero-shot** | model card NlpHUST/ner-vietnamese-electra-base (ELECTRA, Clark et al., ICLR 2020; dữ liệu VLSP 2018) | Dùng nguyên model đã học tác vụ khác; chỉ ánh xạ nhãn PER→NAME, LOC→LOCATION, ORG→ORGANIZATION; 7 loại còn lại không có → F1 = 0 → Macro-F1 thấp | — |

## 5. Fine-tune cho gán nhãn chuỗi (`src/train_ner.py`)

| Kỹ thuật | Nguồn | Code |
|---|---|---|
| Token classification: thêm **1 lớp tuyến tính** lên vector cuối của encoder, softmax từng vị trí | Devlin et al. 2019 (§5.3, NER CoNLL-2003: dùng biểu diễn của **subword đầu tiên** của mỗi từ) | `AutoModelForTokenClassification` |
| **Căn nhãn với subword**: nhãn ở mảnh đầu, mảnh còn lại = −100 (bị bỏ qua khi tính loss) | Devlin et al. 2019; tài liệu Hugging Face Transformers (Wolf et al., EMNLP 2020 Demo) | `BoMaHoa.ma_hoa` (mã hóa từng token → chạy được cả tokenizer PhoBERT không có `word_ids()`) |
| Loss **cross-entropy** trên các vị trí có nhãn | SLP3 (chương mạng nơ-ron và gán nhãn chuỗi); slide Session 5 | Trainer mặc định |
| **AdamW** (weight decay tách khỏi gradient) + warmup tuyến tính | Loshchilov & Hutter, ICLR 2019 | `weight_decay`, `warmup_ratio` |
| **Dừng sớm** + chọn checkpoint theo F1 dev | Slide Session 5 "Dropout · Weight decay · Early stopping" | `EarlyStoppingCallback`, `load_best_model_at_end` |
| fp16 (mixed precision) | Micikevicius et al., ICLR 2018 | `fp16=True` trên T4 |
| Hậu xử lý BIO: I-X lạc (sau O hoặc loại khác) → B-X | Thực hành chuẩn khi không có lớp CRF; Session 6: softmax từng token "can violate BIO structure" | `sua_chuoi_bio` |

## 6. Tìm siêu tham số — báo cáo mục 4.3

| Kỹ thuật | Nguồn | Nhóm áp dụng |
|---|---|---|
| **Grid Search** — duyệt mọi tổ hợp của lưới | scikit-learn `ParameterGrid` (bộ sinh cấu hình của `GridSearchCV`) — Pedregosa et al., JMLR 2011 | lr {2e-5, 3e-5, 5e-5} × batch {16, 32} = 6 cấu hình |
| **Random Search** — lấy mẫu ngẫu nhiên trong không gian | Bergstra & Bengio, *Random Search for Hyper-Parameter Optimization*, JMLR 13 (2012) 281–305; `ParameterSampler` (bộ sinh của `RandomizedSearchCV`) | thêm warmup {0, 0,1} × weight decay {0, 0,01}; lấy 6/24 cấu hình, `random_state=42` |
| Chọn trên **dev**, test chỉ dùng 1 lần | Slide Session 3 "Training, Development and Test Sets — … Choose hyperparameters & models · Final unbiased evaluation" | `tim_sieu_tham_so` không bao giờ đọc test |
| **Cùng ngân sách** tìm kiếm cho mọi mô hình khi so sánh; báo cáo ngân sách | Dodge et al., *Show Your Work*, EMNLP 2019 | cùng 6 + 6 cấu hình × 3 epoch cho cả 3 kiến trúc |

**Vì sao không gọi thẳng `GridSearchCV`?** `GridSearchCV` cần (1) estimator theo giao diện scikit-learn (`fit/predict`) và (2)
**k-fold cross-validation** — với Transformer, 5-fold tốn gấp 5 lần GPU, trong khi bộ dữ liệu đã có **tập dev chuẩn** do tác giả chia.
Nhóm dùng *đúng bộ sinh cấu hình* của hai lớp đó (`ParameterGrid`, `ParameterSampler`) với **hold-out validation** trên dev — đây là
cách làm chuẩn khi fine-tune mô hình lớn. (CRF của Phúc nhỏ, có thể dùng thẳng `RandomizedSearchCV` + `make_scorer` nếu muốn.)

**Hạn chế cần ghi:** mỗi cấu hình chỉ chạy 3 epoch, 1 seed (đánh giá "độ trung thực thấp") → có thể ưu tiên learning rate lớn hội tụ nhanh.

## 7. Báo cáo kết quả có độ tin cậy (`src/aggregate.py`)

| Kỹ thuật | Nguồn | Ý chính |
|---|---|---|
| **F1 mức thực thể, strict** | Tjong Kim Sang & De Meulder, CoNLL-2003; seqeval (Nakayama, 2018) `mode="strict", scheme=IOB2` | Thực thể đúng khi **đúng cả biên lẫn loại**; strict không "đoán hộ" khi chuỗi BIO lỗi |
| Micro vs Macro F1 | Slide Session 3 "Macro vs Micro Averaging… For imbalanced multiclass NLP, Macro-F1 is often more informative" | Micro bị LOCATION/PATIENT_ID chi phối; Macro đối xử 10 loại như nhau |
| **Nhiều seed, báo mean ± std** | Reimers & Gurevych, EMNLP 2017 (chính trên gán nhãn chuỗi: chỉ đổi seed đã đủ làm thứ hạng mô hình đảo lộn) | 3 seed; std **mẫu** (chia n−1) |
| Kiểm định ý nghĩa thống kê | Dror et al., *The Hitchhiker's Guide to Testing Statistical Significance in NLP*, ACL 2018 | Welch t-test giữa các cặp kiến trúc + cảnh báo n = 3 có độ mạnh thấp |
| Ghi môi trường để tái lập | Slide Session 5: "Record random seed, data split, optimizer, learning rate, batch size and epochs"; Pineau et al., JMLR 2021 | Mỗi file JSON ghi GPU, phiên bản thư viện, siêu tham số, thời gian |

## 8. Phân tích lỗi (`src/phan_tich_loi.py`)

- **Khung:** theo đúng 4 nhóm của bài báo gốc §1 + nhóm *bỏ sót* → 5 nhóm: sai loại · sai biên · sai cả hai · bỏ sót · dự đoán thừa.
- **So sánh công bằng giữa mức từ và mức âm tiết:** mọi thực thể quy về **vị trí âm tiết** (`Bệnh_viện` = 2 âm tiết) → cùng một
  thực thể có cùng tọa độ ở PhoBERT, XLM-R, mBERT, CRF.
- **Lỗi chung / lỗi riêng:** giao các tập lỗi → trả lời câu hỏi của đề "3 kiến trúc có mắc **cùng** loại lỗi không?".
- **Thực thể đặc thù:** PATIENT_ID (dễ nhầm với AGE vì đều là số), ORGANIZATION (dài trung bình 5,5 âm tiết — xem EDA), JOB, triệu chứng.
- Bài giảng: Session 6 "NER — entity view… a predicted entity is correct only when span and type match"; SLP3 Ch. 18 (khó khăn của NER:
  *segmentation*, *type ambiguity*, *sparse entities* — đúng với 3 nhóm lỗi sai biên / sai loại / bỏ sót).

## 9. Ứng dụng demo Streamlit (`app/`)

| Thành phần | Nguồn / tham khảo | Lý do thiết kế |
|---|---|---|
| Tô màu thực thể ngay trong câu, nhãn loại nhỏ cạnh thực thể | Cách hiển thị của **displaCy** (spaCy, Explosion AI) và **Hosted Inference widget** trên Hugging Face — hai giao diện NER phổ biến nhất | Người dùng thấy ngay thực thể ở đâu, không phải đọc bảng |
| Câu mẫu bấm 1 lần, thanh bên cấu hình, tab "nhiều câu" tải file | Thực hành của các demo trong Streamlit Gallery | Người chưa biết gõ gì vẫn thử được trong 5 giây |
| Ngưỡng độ tin cậy + cột thanh tiến trình | — | Cho thấy mô hình *không chắc* ở đâu — cầu nối sang phần phân tích lỗi |
| "Các bước xử lý bên trong" (NFC → tách từ → subword → BIO) | — | Chứng minh nhóm hiểu pipeline, đúng tinh thần "nắm kỹ thuật" |
| `st.cache_resource` | Tài liệu Streamlit (docs.streamlit.io) | Tải mô hình 1 lần, các lượt sau ~vài chục ms |
| Tách từ bằng VnCoreNLP khi dùng PhoBERT | README PhoBERT: "recommended to also use the same word segmenter for PhoBERT-based downstream applications" | Đầu vào lúc dùng phải giống lúc huấn luyện |

## 10. Câu hỏi phản biện dự kiến (mỗi người chuẩn bị phần mình)

1. *Vì sao PhoBERT cần tách từ còn XLM-R thì không?* → dữ liệu pretrain của PhoBERT đã tách từ; BPE học trên "từ" có dấu `_`.
2. *Vì sao không dùng accuracy mức token?* → ~72–77 % âm tiết (74–79 % từ) là O; đoán toàn O vẫn có accuracy cao (EDA: bảng tổng quan).
3. *Std nói gì?* → độ ổn định theo khởi tạo/thứ tự dữ liệu; nếu chênh lệch mean giữa 2 kiến trúc nhỏ hơn std thì chưa thể kết luận.
4. *Vì sao zero-shot yếu?* → khác tập nhãn (7/10 loại không có), khác miền (VLSP tổng quát vs tin COVID).
5. *Vì sao chọn checkpoint theo dev?* → chọn theo test là "nhìn trộm" đáp án → kết quả test bị lạc quan.
6. *Grid hay Random tốt hơn?* → Bergstra & Bengio 2012: cùng ngân sách, random phủ được nhiều giá trị hơn của tham số quan trọng.
7. *Vì sao mBERT dùng bản cased?* → bản uncased xóa dấu tiếng Việt.
8. *Câu dài hơn 256 subword xử lý thế nào?* → train: cắt và đếm (`so_cau_bi_cat`); chấm điểm: token bị cắt tính là O (không gian lận); demo: chia cửa sổ.
9. *CRF mạnh như vậy (~0,92) thì fine-tune có đáng không?* → so Macro-F1 và loại hiếm/thực thể mới (EDA: % thực thể test chưa gặp trong train).

## Tài liệu tham khảo (chuẩn IEEE — chép vào báo cáo khi trích)

1. T. H. Truong, M. H. Dao, D. Q. Nguyen, "COVID-19 named entity recognition for Vietnamese," *NAACL-HLT*, 2021.
2. D. Q. Nguyen, A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," *Findings of EMNLP*, 2020.
3. A. Conneau et al., "Unsupervised cross-lingual representation learning at scale," *ACL*, 2020.
4. J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," *NAACL-HLT*, 2019.
5. J. Lafferty, A. McCallum, F. Pereira, "Conditional random fields: Probabilistic models for segmenting and labeling sequence data," *ICML*, 2001.
6. T. Vu et al., "VnCoreNLP: A Vietnamese natural language processing toolkit," *NAACL-HLT Demonstrations*, 2018.
7. D. Q. Nguyen et al., "A fast and accurate Vietnamese word segmenter," *LREC*, 2018.
8. J. Bergstra, Y. Bengio, "Random search for hyper-parameter optimization," *JMLR*, vol. 13, pp. 281–305, 2012.
9. J. Dodge et al., "Show your work: Improved reporting of experimental results," *EMNLP-IJCNLP*, 2019.
10. N. Reimers, I. Gurevych, "Reporting score distributions makes a difference: Performance study of LSTM-networks for sequence tagging," *EMNLP*, 2017.
11. R. Dror, G. Baumer, S. Shlomov, R. Reichart, "The hitchhiker's guide to testing statistical significance in natural language processing," *ACL*, 2018.
12. I. Loshchilov, F. Hutter, "Decoupled weight decay regularization," *ICLR*, 2019.
13. F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *JMLR*, vol. 12, pp. 2825–2830, 2011.
14. E. F. Tjong Kim Sang, F. De Meulder, "Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition," *CoNLL*, 2003.
15. T. Wolf et al., "Transformers: State-of-the-art natural language processing," *EMNLP: System Demonstrations*, 2020.
16. D. Jurafsky, J. H. Martin, *Speech and Language Processing*, 3rd ed. draft — chương gán nhãn chuỗi & NER (slide Session 6 trích "SLP3 Ch. 18").
