# Hướng dẫn 3 — Từ hôm nay (17/10) đến Báo cáo tiến độ 2 · Duyên, Tâm, Trinh

> Đọc mục 0 và 1 trước (cả 3 người). Sau đó mỗi người chỉ cần đọc **mục của mình** (2 = Duyên, 3 = Tâm, 4 = Trinh).
> Mục 5 là cách đưa kết quả lên GitHub (dùng lại nhiều lần), mục 6 là xử lý lỗi thường gặp.

---

## 0. Việc gì chạy ở đâu

| Công cụ | Dùng cho | Vì sao |
|---|---|---|
| **Google Colab** (trình duyệt, GPU T4 miễn phí) | Notebook `00`, `02`, `03`, `04`, `05`: kiểm tra môi trường, EDA, tìm siêu tham số + huấn luyện 3 seed | Cần GPU; máy cá nhân thường không có GPU NVIDIA |
| **VS Code** (trên máy) | `aggregate.py` (bảng mean ± std), `phan_tich_loi.py`, `ve_so_do.py`, **chạy app Streamlit** | Không cần GPU; Streamlit phải chạy trên máy (Colab không mở được giao diện web ổn định) |
| **GitHub Desktop** | Tạo nhánh, commit, push, mở Pull Request | Như đã làm ở T04 |
| **github.com** | Xem Issue, review + merge Pull Request, Project board | |
| **Google Drive** `NLP_De26/` | Sao lưu kết quả khi Colab ngắt, chứa file mô hình `.zip` (nặng, không lên GitHub) | |

**Dữ liệu PhoNER_COVID19 (câu hỏi "có dataset không?" — có, công khai):**
- Trang gốc: https://github.com/VinAIResearch/PhoNER_COVID19
- Tải zip: https://github.com/VinAIResearch/PhoNER_COVID19/archive/refs/heads/main.zip → giải nén → dùng 2 thư mục `data/word` và `data/syllable`.
- Trên Colab **không cần tải tay**: ô "Tải dữ liệu" của notebook tự `git clone`. Chỉ khi ô đó lỗi mạng mới tải zip ở trên rồi kéo 2 thư mục
  vào `/content/de26/data/` trong khung **Files** (biểu tượng 📁 bên trái Colab).
- Trên máy (VS Code): giải nén, chép `word` và `syllable` vào `NLP-phoner-covid19-26/data/` (`.gitignore` đã chặn, không bao giờ lên GitHub — giấy phép chỉ cho học tập/nghiên cứu, không phát tán lại).

---

## 1. Việc chung (làm 1 lần)

### 1.1 Duyên đưa gói code lên repo (17/10, ~20 phút)
Gói `GOI_17-10_Duyen_Tam_Trinh.zip` có 4 thư mục: `0_chung`, `1_Duyen`, `2_Tam`, `3_Trinh`. Mỗi thư mục có cấu trúc **giống hệt repo**.
Để GitHub ghi đúng ai làm phần nào, mỗi người đưa phần của mình bằng **Pull Request của chính mình**:

| Thư mục | Ai đưa lên | Nhánh | PR đóng Issue |
|---|---|---|---|
| `0_chung` + `1_Duyen` | Duyên | `duyen/T10-train-ner` | `Closes #<số Issue T10>` |
| `2_Tam` | Tâm | `tam/T07-data-eda` | `Closes #<T07>` (T11 đóng khi có `results/eda`) |
| `3_Trinh` | Trinh | `trinh/T30-streamlit` | không đóng (T30 xong khi có mô hình thật) |

Cách chép (mỗi người với thư mục của mình): mở thư mục gói → **Ctrl + A** → **Ctrl + C** → mở thư mục repo `NLP-phoner-covid19-26` trên máy
(đúng thư mục có `README.md`, `src/`…) → **Ctrl + V** → chọn **Replace the files in the destination**. Rồi làm theo mục 5.
> `README.md` của repo **không** có trong gói (để giữ username các bạn đã điền). Duyên sửa tay trên github.com: mở `README.md` → biểu tượng ✏️ → đổi 2 chữ "Gradio" thành "Streamlit" → *Commit changes*.
>
> Thứ tự merge: PR của Duyên trước (có `requirements.txt`, `.gitignore`), rồi Tâm, rồi Trinh. Người sau bấm **Fetch origin → Pull origin** trước khi tạo nhánh.

### 1.2 Cài VS Code + Python trên máy (người cần: Duyên, Tâm, Trinh — mỗi người 1 lần, ~20 phút)
1. Cài **Python 3.11** từ https://www.python.org/downloads/ — màn hình đầu tiên **tích ô "Add python.exe to PATH"** → Install Now.
2. Cài **VS Code** từ https://code.visualstudio.com → mở VS Code → biểu tượng Extensions (4 ô vuông bên trái) → cài **Python** và **Jupyter** (của Microsoft).
3. VS Code → **File → Open Folder…** → chọn thư mục repo `NLP-phoner-covid19-26`.
4. **Terminal → New Terminal**, gõ lần lượt (Windows):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Dòng lệnh hiện `(.venv)` ở đầu là đúng. `seqeval` lỗi khi cài thì kệ (code tự nạp). Cài torch lâu ~5 phút.
   Nếu báo *"running scripts is disabled"*: gõ `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` → Y → chạy lại dòng activate.
5. Chép dữ liệu vào `data/` (mục 0) rồi gõ `python src/data.py` → phải thấy train 5027 / dev 2000 / test 3000, `lech_do_dai: 0`.
6. Khi mở notebook `.ipynb` trong VS Code: góc trên phải bấm **Select Kernel → Python Environments → .venv**.

### 1.3 Mở notebook của mình trên Colab
Cách dễ nhất: https://colab.research.google.com → **File → Upload notebook** → chọn file trong `notebooks/` của repo trên máy.
→ **Runtime → Change runtime type → T4 GPU → Save** → chạy từng ô bằng nút ▶ (hoặc **Runtime → Run all**).
Ô 2 hỏi quyền Google Drive → chọn tài khoản → **Continue / Cho phép tất cả**. Không gắn được Drive vẫn chạy được, nhưng nhớ tải kết quả về trước khi đóng tab.

---

## 2. HOÀNG DUYÊN — PhoBERT-base + hạ tầng huấn luyện + tổng hợp kết quả

### Đến BC1 (22/10)
| Ngày | Việc | Ở đâu | Xong khi |
|---|---|---|---|
| 17/10 tối | Mục 1.1: PR `0_chung + 1_Duyen` (T10) · nhắc Tâm, Trinh đưa phần của họ | GitHub Desktop | PR merge |
| 18/10 | Notebook **03**: ô 1–6 (chạy thử ~2 phút) → ô 7 **Grid Search** (~40 phút) | Colab T4 | `results/tim_kiem/phobert_grid.json` |
| 18–19/10 | Ô 7 tiếp **Random Search** (~40 phút) → ô 8 **3 seed** (~60–90 phút) → ô 9 → ô 10 tải `ket_qua_phobert.zip` → ô 11 lưu mô hình lên Drive | Colab T4 | 3 file `results/phobert_seed*.json` |
| 19/10 | Giải nén `ket_qua_phobert.zip` vào repo (chọn Replace) → PR `duyen/T15-phobert` · `Closes #T15` | GitHub Desktop | PR merge |
| 20/10 | Khi Tâm, Trinh đã merge kết quả: **Fetch + Pull** → VS Code: `python src/aggregate.py` → PR `duyen/T20-aggregate` (có thư mục `results/tong_hop/`) | VS Code | `bang_tong_hop.md` có 3 dòng mean ± std |
| 20/10 | Viết báo cáo (T19): mục 3.3.2–3.3.3, **4.3**, 4.4.1–4.4.2, 4.5, **5.1** và dòng của mình ở 4.6 — đã có **bản nháp**, sửa bằng lời của mình + điền số từ ô 7, 9 | Word | xóa hết dòng tô vàng của mục mình |

**Đọc hiểu trước khi bảo vệ (bắt buộc):** `docs/SO_TAY_KY_THUAT.md` §3, §5, §6, §7. Tự trả lời được: vì sao nhãn đặt ở subword đầu và −100 ở phần còn lại;
vì sao không gọi thẳng `GridSearchCV`; vì sao chọn checkpoint theo dev; std mẫu (n−1) khác std tổng thể thế nào.

**Kiểm tra kết quả hợp lý:** Micro-F1 test của PhoBERT-base nên quanh 0,93–0,94 (bài báo 0,942 với 5 seed, 30 epoch). Dưới 0,85 → báo nhóm trước khi chạy tiếp.

### Đến BC2 (12/11)
| Hạn | Việc | Ở đâu |
|---|---|---|
| 23/10 | Tạo Issue cho BC2: tab **Actions** → *Tạo Issue từ kế hoạch* → **Run workflow** → ô file kế hoạch gõ `plan/tasks_bc2.json` → Run (Milestone BC2 + 17 Issue T27–T43) | github.com |
| 26/10 (T28) | Xác định mô hình tốt nhất (cột Micro-F1 trong `bang_tong_hop.md`), chia sẻ `mo_hinh_<khoa>.zip` trên Drive cho Trinh (chuột phải → Share → thêm email Trinh) · tùy chọn ô 12 đẩy lên Hugging Face Hub (private) | Drive |
| 28/10 (T27) | Chạy lại `aggregate.py` khi đủ cả kết quả nâng cao của Phúc → bảng chính thức + 2 hình → PR | VS Code |
| 02/11 (T32) | Đọc lỗi PhoBERT: mở `results/phan_tich_loi/vi_du_*.csv` (Tâm tạo), viết 1 đoạn nhận xét + chọn 3 ví dụ (câu, nhãn thật, nhãn dự đoán, nhóm lỗi) gửi Tâm | Excel / VS Code |
| 07/11 (T39) | Mục **5.3** (bảng + 2 hình từ `results/tong_hop/`) + nháp **5.6 Thảo luận**: kiến trúc nào tốt/kém nhất và vì sao (dữ liệu pretrain, tách từ, số subword/token ở EDA), std nói gì, kết quả `kiem_dinh.md` (kèm cảnh báo n = 3) | Word |
| BC2 | Chạy lại `python src/ve_so_do.py` nếu sơ đồ 5.1 cần sửa chữ | VS Code |

---

## 3. ĐỨC TÂM — XLM-R-base + dữ liệu/EDA + phân tích lỗi

### Đến BC1 (22/10)
| Ngày | Việc | Ở đâu | Xong khi |
|---|---|---|---|
| 17/10 tối | Nếu chưa xong T05: chạy `notebooks/00_setup_tam.ipynb` (Colab, ~10 phút) · Mục 1.1: PR `2_Tam` (T07) — trước đó chạy `python src/data.py` trên máy để hiểu và kiểm tra | Colab · GitHub Desktop | PR merge |
| 18/10 sáng | Notebook **02_eda** (Colab, CPU được, ~10 phút) → tải `ket_qua_eda.zip` → giải nén vào repo → PR `tam/T11-eda` · `Closes #T11` | Colab | `results/eda/subword.md` có 9 dòng |
| 18–19/10 | Notebook **04** (XLM-R): giống hệt các bước của Duyên ở mục 2 (ô 1–11) | Colab T4 | 3 file `results/xlmr_seed*.json` |
| 19/10 | PR `tam/T16-xlmr` · `Closes #T16` | GitHub Desktop | |
| 20/10 | Viết (T21): mục **3.1–3.2** (đã có bản nháp + số thật; thêm bảng subword từ `results/eda/subword.md`), **3.3.1**, 4.4.3, dòng của mình ở 4.6 | Word | |
| 21/10 chiều | **Kiểm tra chéo (T24)**: mỗi con số trong bản ráp BC1 của Trinh phải truy được về 1 file trong `results/` — ghi danh sách sai gửi Trinh | Word + repo | |

**XLM-R nặng hơn PhoBERT** (~270M tham số): nếu báo *CUDA out of memory* ở cấu hình batch 32 → xem mục 6.
**Kết quả hợp lý:** XLM-R-base quanh 0,92–0,93 (bài báo 0,925).

### Đến BC2 (12/11) — phần quan trọng nhất của Tâm là **phân tích lỗi**
| Hạn | Việc | Ở đâu |
|---|---|---|
| 03/11 (T31) | **Fetch + Pull** (đủ `results/du_doan/` của 3 kiến trúc + `du_doan_test.json` của Phúc) → VS Code: `python src/phan_tich_loi.py --seed 42` → PR có thư mục `results/phan_tich_loi/` | VS Code |
| 02/11 (T33) | Đọc lỗi XLM-R (1 đoạn + 3 ví dụ) | |
| 08/11 (T38) | Viết mục **5.4** (đã có phương pháp + số CRF/zero-shot): bảng 5 nhóm lỗi × 5 mô hình (`bang_nhom_loi.md`); nhầm loại hay gặp (`ma_tran_nham_loai.csv`); **trả lời câu hỏi của đề "3 kiến trúc có mắc cùng loại lỗi không?"** bằng `loi_chung_rieng.md`; phần thực thể đặc thù (`loi_thuc_the_dac_thu.csv`); ≥ 3 ví dụ thật mỗi nhóm (`vi_du_*.csv`, thực thể được đánh dấu 【…】); ghép đoạn nhận xét của Duyên, Trinh, Phúc | Word |

Phát hiện đã có (đưa vào 5.4): zero-shot nhầm **840** thực thể LOCATION thành ORGANIZATION — phần lớn là bệnh viện / nơi cách ly, vì hướng dẫn gán nhãn
PhoNER_COVID19 coi nơi bệnh nhân có mặt là LOCATION. Kiểm tra xem 3 mô hình fine-tune còn nhầm cặp này không.

---

## 4. YẾN TRINH — mBERT-cased + tóm tắt bài báo/lý thuyết + demo Streamlit + ráp BC1

### Đến BC1 (22/10)
| Ngày | Việc | Ở đâu | Xong khi |
|---|---|---|---|
| 17/10 tối | Nếu chưa xong T06: `notebooks/00_setup_trinh.ipynb` (Colab) · Mục 1.1: PR `3_Trinh` | Colab · GitHub Desktop | |
| 18/10 | Viết (T09, T13): mục **1.1–1.3, 2.1, 2.2.2, 2.2.3, 2.5** — đã có bản nháp; đọc bài báo gốc (https://aclanthology.org/2021.naacl-main.173/) và `docs/SO_TAY_KY_THUAT.md` §1–§4 rồi **viết lại bằng lời của mình** (cô cấm chép nguyên văn) | Word | |
| 18–19/10 | Notebook **05** (mBERT): các bước giống mục 2 | Colab T4 | 3 file `results/mbert_seed*.json` |
| 19/10 | PR `trinh/T17-mbert` · `Closes #T17` | GitHub Desktop | |
| 20/10 | Viết (T22): 4.4.4 + dòng của mình ở 4.6 | Word | |
| 21/10 sáng | **Ráp BC1 (T23)** từ `reports/BC_TienDo1_De26_NHAP.docx` (đã có đủ 5 mục; mục 2, 3 có số thật) — điền bảng 6 (tiến độ 3 người) và bảng 7 (% hoàn thành lấy từ sheet Tổng quan của file phân công) | Word | |
| 21/10 tối | Họp rà soát (T25) · 22/10 **nộp** (T26) + chụp màn hình xác nhận gửi nhóm | | |

**Kết quả hợp lý:** mBERT thường thấp hơn XLM-R một chút (tham khảo: 0,90–0,92). Không có số trong bài báo cho mBERT — đây là đóng góp riêng của nhóm.

### Đến BC2 (12/11) — demo Streamlit (yêu cầu của cô)
| Hạn | Việc | Ở đâu |
|---|---|---|
| ngay sau 19/10 | **Chạy thử app với mô hình mBERT của mình** (không cần chờ mô hình tốt nhất): tải `mo_hinh_mbert.zip` từ Drive → giải nén vào `app/mo_hinh/mbert/` (mở ra thấy ngay `config.json`) → VS Code Terminal (đã `activate`): `pip install -r app/requirements.txt` → `streamlit run app/app.py` → trình duyệt mở `http://localhost:8501` | VS Code |
| 31/10 (T30) | Thêm mô hình tốt nhất (Duyên chia sẻ, T28) vào `app/mo_hinh/<tên>/` → app tự đưa mô hình F1 cao nhất lên đầu. Kiểm tra 3 câu **tự đặt**; với PhoBERT xem mục "Các bước xử lý" ghi đang tách từ bằng gì (VnCoreNLP cần Java: cài https://adoptium.net, Temurin 17; không có Java app tự dùng underthesea) | VS Code |
| 05/11 (T37) | Chụp 2 ảnh (kết quả tô màu + mục Các bước xử lý) và quay video 30–60 giây (Windows: **Win + Alt + R** bằng Xbox Game Bar). Tùy chọn: triển khai Streamlit Community Cloud (https://share.streamlit.io → New app → chọn repo, file `app/app.py`; mô hình phải ở Hugging Face Hub, đặt `NER_MODEL` và `HF_TOKEN` trong *Secrets*) | Trình duyệt |
| 02/11 (T34) | Đọc lỗi mBERT (1 đoạn + 3 ví dụ gửi Tâm) | |
| 07/11 (T40) | Viết mục **4.7** (đã có bản nháp + sơ đồ luồng `reports/hinh/so_do_demo.png`): thêm ảnh chụp, link/video | Word |

**Thiết kế app (để trình bày):** tô màu thực thể trong câu theo kiểu **displaCy** (spaCy) và widget NER của Hugging Face; câu mẫu bấm 1 lần;
thanh bên chọn mô hình + ngưỡng độ tin cậy + chú thích 10 loại; tab nhập file `.txt` nhiều câu → tải CSV; mục "Các bước xử lý bên trong"
(NFC → tách từ → subword → nhãn BIO) để giải thích pipeline. Chi tiết: `app/README.md`, `docs/SO_TAY_KY_THUAT.md` §9.

---

## 5. Đưa kết quả lên GitHub (dùng mỗi lần có file mới)

1. GitHub Desktop → **Fetch origin** → nếu hiện **Pull origin** thì bấm (lấy phần mới của bạn khác).
2. **Current branch → New branch** → đặt tên `ten/Txx-mo-ta` (vd `tam/T16-xlmr`) → Create branch.
3. Chép file vào thư mục repo (giải nén `ket_qua_*.zip` → *Replace*). Không chép `data/`, file mô hình, file `.zip`.
4. Quay lại GitHub Desktop: cột trái hiện danh sách file thay đổi → kiểm tra **không có** file dữ liệu `train_*.json`, `*.safetensors`, `*.zip`.
5. Ô **Summary** (góc dưới trái) ghi `T16: XLM-R 3 seed + tìm siêu tham số` → **Commit to tam/T16-xlmr** → **Publish branch** (hoặc **Push origin**).
6. Bấm **Create Pull Request** (mở github.com) → phần mô tả ghi `Closes #<số Issue>` (số Issue xem ở tab **Issues**: mở Issue có tiêu đề bắt đầu bằng `T16 ·`, số nằm sau dấu `#` cạnh tiêu đề) → **Create pull request**.
7. Nhờ 1 bạn review → bấm **Merge pull request → Confirm merge**. Issue tự đóng, Project board tự chuyển sang *Done*.

## 6. Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `CUDA out of memory` | Runtime → Restart session → chạy lại từ ô 1 (kết quả cũ tự khôi phục từ Drive). Còn lỗi ở cấu hình batch 32: ghi lại, báo nhóm — **không tự đổi không gian tìm kiếm** (3 kiến trúc phải giống nhau) |
| Colab ngắt giữa chừng / hết GPU trong ngày | Mở lại notebook, chạy lại từ ô 1: ô 5 khôi phục kết quả từ Drive, ô 7–8 tự **bỏ qua** cấu hình/seed đã xong. Hết hạn mức GPU → chạy tiếp hôm sau hoặc dùng Kaggle (Notebook → Settings → Accelerator GPU T4) |
| `ModuleNotFoundError: seqeval` | Đã xử lý tự động (`src/nap_seqeval.py`); nếu vẫn lỗi: chạy lại ô ghi code (bước 3) |
| Ô tải dữ liệu báo lỗi mạng | Tải zip ở mục 0 → kéo `word`, `syllable` vào `/content/de26/data/` |
| F1 = 0 hoặc rất thấp sau 3 seed | Kiểm tra đúng bản dữ liệu (PhoBERT = word); báo nhóm kèm file `results/<khoa>_seed42.json` |
| App: "Chưa có mô hình" | Thư mục phải là `app/mo_hinh/<tên>/config.json` (không lồng thêm 1 cấp thư mục khi giải nén) |
| App chậm lần đầu | Bình thường (tải mô hình + VnCoreNLP); các lần sau nhanh nhờ `st.cache_resource` |
| GitHub Desktop: *conflict* | Bấm **Fetch/Pull** trước khi tạo nhánh; nếu vẫn conflict: chụp màn hình gửi Duyên |
