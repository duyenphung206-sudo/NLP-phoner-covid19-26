# Quy tắc làm việc chung

Ngắn gọn để cả nhóm làm giống nhau. Hướng dẫn bấm nút từng bước: [docs/HUONG_DAN_2_THANH_VIEN.md](docs/HUONG_DAN_2_THANH_VIEN.md).

## 1. Một việc = một Issue = một nhánh = một Pull Request

| Bước | Làm gì | Ví dụ |
|---|---|---|
| 1 | Mở Issue của mình, đọc *Đầu vào – Đầu ra – Xong khi* | Issue `T07 · Viết data.py…` |
| 2 | Cập nhật `main` mới nhất, tạo nhánh mới từ `main` | `tam/T07-data-py` |
| 3 | Làm việc, commit nhỏ và thường xuyên | `T07: đọc được 2 bản dữ liệu` |
| 4 | Push nhánh, mở Pull Request vào `main` | tiêu đề `T07: data.py + configs`, nội dung có `Closes #7` |
| 5 | 1 bạn khác review | Approve hoặc Request changes |
| 6 | Merge (Squash and merge), xóa nhánh | Issue #7 tự đóng |

## 2. Đặt tên

- **Nhánh:** `ten/Txx-mo-ta-ngan` — `ten` là `phuc`, `duyen`, `tam`, `trinh`.
- **Commit:** `Txx: <làm gì>` — ví dụ `T15: chạy xong PhoBERT seed 42`.
- **Notebook:** `notebooks/NN_noi-dung_ten.ipynb` — ví dụ `03_train-phobert_duyen.ipynb`.
- **Kết quả:** `results/{khoa_mo_hinh}_seed{seed}.json` — khóa lấy trong `configs/common.json` (`phobert`, `xlmr`, `mbert`, `phobert_khong_tach_tu`), ví dụ `results/xlmr_seed42.json`.

## 3. Không bao giờ commit

- File dữ liệu PhoNER_COVID19 (giấy phép không cho phát tán).
- Checkpoint/model (`.bin`, `.safetensors`, `.pt`, `.pkl`) → lưu Google Drive chung hoặc Hugging Face Hub.
- File lớn hơn 50 MB, file nén `.zip/.rar`, mật khẩu/token.

`.gitignore` đã chặn sẵn phần lớn; vẫn nhìn kỹ danh sách file trước khi commit.

## 4. Review Pull Request

- Người review: chạy thử hoặc đọc kỹ, đối chiếu cột **Xong khi** của Issue. Thiếu ý nào thì *Request changes* và ghi rõ.
- Không tự merge PR của mình khi chưa có ai Approve (trừ PR chỉ sửa tài liệu nhỏ).
- Review trong vòng **12 giờ** kể từ khi được nhờ, để không ai bị chặn.

## 5. Báo tiến độ và vướng mắc

- Mỗi tối trước 22h: comment vào Issue đang làm → *Đã xong / Mai làm / Đang vướng*.
- Bị chặn quá nửa ngày: mở Issue mới bằng mẫu **"Báo vướng mắc"** và nhắn nhóm.
- Đổi hạn hoặc đổi người phụ trách: sửa trong Issue + ghi vào biên bản họp gần nhất.

## 6. Muốn đổi "hợp đồng chung"

Mọi giá trị trong `configs/common.json` (seed, siêu tham số, tên model, cách chấm) chỉ được đổi qua PR có lý do, và phải báo cả nhóm — nếu không, 3 kiến trúc sẽ không còn so sánh công bằng.
