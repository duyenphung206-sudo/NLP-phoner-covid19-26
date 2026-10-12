# Hướng dẫn 2 — Cách mỗi thành viên làm việc trên repo

**Ai đọc:** cả 4 người · **Thời gian đọc:** 15 phút · Làm phần A một lần, sau đó mỗi việc lặp lại phần B.

> Hình dung: **Issue** là "phiếu giao việc", **nhánh (branch)** là "bản nháp riêng" của bạn, **Pull Request (PR)** là "nộp bài để bạn khác chấm". `main` là "bản chính thức" — không ai viết thẳng vào đó.

---

## A. Làm 1 lần đầu (15 phút)

1. **Nhận lời mời:** mở email từ GitHub → **View invitation** → **Accept invitation** (hoặc vào link `https://github.com/duyenphung206-sudo/nlp-de26-phoner-covid19/invitations`).
2. **Cài GitHub Desktop:** https://desktop.github.com → mở → **Sign in to GitHub.com** → đăng nhập.
3. **Clone repo về máy:** GitHub Desktop → **File → Clone repository…** → tab **GitHub.com** → chọn `duyenphung206-sudo/nlp-de26-phoner-covid19` → **Local path**: ví dụ `D:\NLP\GitHub` → **Clone**.
4. **Tải dữ liệu** (không commit) theo [`data/README.md`](../data/README.md).
5. **Xem việc của mình:** trên web vào tab **Issues** → ô lọc gõ `is:open assignee:@me` (hoặc bấm link "Việc của tôi" trong README).

---

## B. Vòng lặp cho MỖI việc (Issue)

### B1. Nhận việc
- Mở Issue của mình, đọc 3 phần **Cần có trước – Kết quả bàn giao – Xong khi**.
- Comment: `Bắt đầu làm, dự kiến xong <ngày>`.
- Trên bảng **Project**, kéo thẻ Issue sang cột **Đang làm**.

### B2. Tạo nhánh riêng (GitHub Desktop)
1. Thanh trên: **Current branch** → chọn `main` → bấm **Fetch origin** → nếu hiện **Pull origin** thì bấm (lấy bản mới nhất).
2. **Current branch → New branch** → đặt tên `ten/Txx-mo-ta`, ví dụ `tam/T07-data-py` → **Create branch** (dựa trên `main`).

### B3. Làm việc
- Đặt file đúng chỗ: code vào `src/`, notebook vào `notebooks/NN_noi-dung_ten.ipynb`, kết quả JSON vào `results/` (xem [`CONTRIBUTING.md`](../CONTRIBUTING.md) mục Đặt tên).
- Dùng giá trị trong `configs/common.json`, không tự đổi seed/siêu tham số.

### B4. Commit (lưu một bước)
1. GitHub Desktop cột trái liệt kê file đã đổi. **Bỏ tick** file nào không nên đưa lên (dữ liệu, checkpoint, file tạm).
2. Ô **Summary**: `Txx: <làm gì>` — ví dụ `T07: đọc được 2 bản dữ liệu`.
3. Bấm **Commit to ten/Txx-…**. Nên commit nhiều lần nhỏ, mỗi khi xong 1 phần.

### B5. Đẩy lên GitHub
Bấm **Publish branch** (lần đầu) hoặc **Push origin** (các lần sau).

### B6. Mở Pull Request
1. GitHub Desktop hiện nút **Create Pull Request** (hoặc trên web có dải vàng **Compare & pull request**) → bấm.
2. Trình duyệt mở trang PR, nội dung đã có sẵn mẫu → điền:
   - Tiêu đề: `T07: data.py + configs`
   - Dòng **`Closes #7`** (số của Issue — xem trên tiêu đề Issue, ví dụ "T07 · … #7").
   - Phần *Kết quả / bằng chứng*: dán số liệu hoặc ảnh chụp.
   - Tick các ô tự kiểm tra.
3. Cột phải: **Reviewers** → chọn 1 bạn (gợi ý: train_ner.py → Phúc review; data.py → Duyên review; bài viết → người ráp báo cáo review).
4. Bấm **Create pull request**. Kéo thẻ trên Project sang **Chờ review**.

### B7. Review và merge
- **Người review:** tab **Files changed** → đọc → **Review changes** → chọn **Approve** (đạt) hoặc **Request changes** (ghi rõ thiếu gì) → **Submit review**. Trong vòng 12 giờ.
- **Người mở PR:** sửa theo góp ý (commit + push tiếp trên cùng nhánh, PR tự cập nhật). Khi đã Approve → **Squash and merge** → **Confirm**.
- Issue tự đóng, thẻ tự sang **Xong**, thanh % Milestone BC1 tự tăng. Trong GitHub Desktop: chuyển về `main` → **Fetch origin → Pull origin**.

---

## C. Báo tiến độ mỗi tối (trước 22h, 1 phút)

Comment vào Issue đang làm:

```
✅ Đã xong: chạy xong seed 42 (f1_micro dev 0.93)
⏭️ Mai làm: seed 123 và 2024
⚠️ Đang vướng: không / Colab ngắt sau 3 tiếng
```

Bị chặn quá nửa ngày → **New issue → 🚧 Báo vướng mắc** + nhắn nhóm.

---

## D. Cách nhanh cho notebook Colab (không cần Desktop)

1. Trên web repo: nút chọn nhánh (chữ `main` phía trên danh sách file) → gõ `ten/Txx-...` → **Create branch … from main**.
2. Trong Colab: **File → Save a copy in GitHub** → cho phép truy cập (lần đầu tick **Include private repos**) → chọn repo `nlp-de26-phoner-covid19`, **Branch** là nhánh vừa tạo, **File path** `notebooks/NN_noi-dung_ten.ipynb`, ghi commit message → **OK**.
3. Quay lại web repo → dải vàng **Compare & pull request** → làm như B6.

File kết quả JSON từ Colab: tải về máy rồi chép vào `results/` trong thư mục repo và commit bằng Desktop (B4–B6), hoặc trên web vào thư mục `results/` (đang ở nhánh của mình) → **Add file → Upload files**.

---

## E. Dùng code của repo trong Colab (repo private)

1. Tạo token: GitHub → ảnh đại diện → **Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token (classic)** → Note `colab-nlp`, Expiration **30 days**, tick **repo** → **Generate token** → copy (chỉ hiện 1 lần).
   *(Repo thuộc tài khoản cá nhân của Duyên nên token dạng fine-grained của bạn khác không truy cập được — dùng loại classic.)*
2. Colab → biểu tượng **🔑 Secrets** (thanh trái) → **Add new secret**: Name `GITHUB_TOKEN`, Value dán token, bật **Notebook access**.
3. Cell đầu notebook:
   ```python
   from google.colab import userdata, drive
   drive.mount('/content/drive')                       # để lưu checkpoint
   token = userdata.get('GITHUB_TOKEN')
   !git clone -q https://{token}@github.com/duyenphung206-sudo/nlp-de26-phoner-covid19.git
   %cd nlp-de26-phoner-covid19
   !pip install -q -r requirements.txt
   ```
   **Không bao giờ** dán token thẳng vào notebook hay commit nó.

---

## F. Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Lỡ làm trên `main` chưa commit | **Current branch → New branch** → chọn **Bring my changes to …** |
| Lỡ commit trên `main` (chưa push) | **History** → chuột phải commit → **Undo commit** → tạo nhánh mới rồi commit lại |
| Push bị từ chối (*rejected*) | **Fetch origin → Pull origin** rồi push lại |
| PR báo **conflicts** | Nhờ Duyên/người viết file đó gộp cùng; đừng xóa phần của người khác |
| File > 100 MB không push được | Đó là file không được commit (checkpoint, dữ liệu) → bỏ tick, thêm vào `.gitignore` |
| Không thấy Issue của mình | Kiểm tra đã nhận lời mời vào repo chưa; báo Duyên gán lại |

---

## G. Quy tắc vàng

1. Không commit thẳng vào `main`. 2. Một việc – một nhánh – một PR có `Closes #`. 3. Không đưa dữ liệu/checkpoint/token lên. 4. Comment tiến độ mỗi tối. 5. Review cho bạn trong 12 giờ.
