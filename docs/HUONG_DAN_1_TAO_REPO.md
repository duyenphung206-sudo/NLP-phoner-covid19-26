# Hướng dẫn 1 — Tạo repo và thiết lập theo dõi tiến độ (người làm: Hoàng Duyên, 1 lần duy nhất)

**Thời gian:** khoảng 45–60 phút · **Kết quả cuối cùng:** repo private có đủ khung, 3 bạn đã vào repo, có Milestone **BC1** với 26 Issue (T01–T26) và bảng Project tự cập nhật.

> Đọc lướt hết 1 lượt trước khi bấm. Chữ **in đậm** là tên nút/menu trên GitHub (giao diện tiếng Anh). Nếu giao diện hơi khác ảnh trong đầu bạn, tìm đúng **tên nút** là được.

---

## Bước 0 — Chuẩn bị (10 phút)

1. Đăng nhập https://github.com bằng tài khoản `duyenphung206-sudo`.
2. Xin username GitHub của 3 bạn (Phúc, Đức Tâm, Yến Trinh). Ai chưa có thì tạo tài khoản ở https://github.com/signup.
3. Cài **GitHub Desktop**: https://desktop.github.com → cài xong mở lên → **Sign in to GitHub.com** → đăng nhập → **Authorize desktop**.
4. *(Khuyến nghị, không bắt buộc hôm nay)* Đăng ký **GitHub Student Developer Pack** bằng email trường: https://education.github.com/pack. Được duyệt thì tài khoản có **GitHub Pro** → bật được "bảo vệ nhánh main" cho repo private (Bước 8). Xét duyệt có thể mất vài ngày — không cần chờ.

---

## Bước 1 — Tạo repository (3 phút)

1. Góc trên bên phải bấm dấu **+** → **New repository**.
2. Điền:
   | Ô | Giá trị |
   |---|---|
   | **Owner** | `duyenphung206-sudo` |
   | **Repository name** | `nlp-de26-phoner-covid19` |
   | **Description** | `Đồ án NLP Đề 26 — NER tiếng Việt về COVID-19 (PhoNER_COVID19): CRF, zero-shot, PhoBERT / XLM-R / mBERT` |
   | **Visibility** | **Private** (bắt buộc: giấy phép dữ liệu không cho công khai) |
   | **Add README** | **Tắt** (bộ khung đã có README) |
   | **.gitignore** | **No .gitignore** |
   | **License** | **No license** |
3. Bấm **Create repository**. Bạn sẽ thấy trang "Quick setup" của repo trống — để nguyên tab này.

> Phải để repo **trống hoàn toàn** thì bước 2 mới không bị xung đột.

---

## Bước 2 — Đưa bộ khung lên repo bằng GitHub Desktop (10 phút)

1. Trên trang "Quick setup" bấm **Set up in Desktop** (hoặc mở GitHub Desktop → **File → Clone repository…** → tab **GitHub.com** → chọn `duyenphung206-sudo/nlp-de26-phoner-covid19`).
2. Ô **Local path** chọn thư mục làm việc, ví dụ `D:\Năm 3\NLP\GitHub` → **Clone**. Desktop tạo thư mục `D:\Năm 3\NLP\GitHub\nlp-de26-phoner-covid19` (đang trống, chỉ có thư mục ẩn `.git`).
3. Giải nén file `nlp-de26-phoner-covid19_KHUNG.zip` (chuột phải → **Extract All…**) → mở thư mục `nlp-de26-phoner-covid19` bên trong → **Ctrl + A** → **Ctrl + C** → mở thư mục repo vừa clone (trong Desktop: **Repository → Show in Explorer**) → **Ctrl + V**.
   - Kiểm tra phải có đủ: `.github`, `.gitignore`, `.gitattributes`, `README.md`, `CONTRIBUTING.md`, `configs`, `data`, `docs`, `notebooks`, `plan`, `reports`, `results`, `src`, `app`, `requirements.txt`.
   - Nếu không thấy `.github` / `.gitignore`: trong File Explorer bấm **View → Show → Hidden items**.
4. Quay lại GitHub Desktop: cột trái hiện khoảng **30 changed files**.
   - Ô **Summary** (góc dưới trái) gõ: `Khởi tạo khung dự án Đề 26`
   - Bấm **Commit to main**.
5. Bấm **Publish branch** (hoặc **Push origin**) ở thanh trên cùng.
6. Mở lại trang repo trên trình duyệt, nhấn **F5**: thấy README hiển thị đẹp với bảng thành viên và bảng kết quả là thành công.

---

## Bước 3 — Cài đặt chung của repo (3 phút)

**Settings** (tab trên cùng của repo) → **General**:

1. Mục **Features**: đảm bảo đã tick **Issues** và **Projects**. Có thể bỏ tick **Wikis** (không dùng).
2. Kéo xuống mục **Pull Requests**:
   - Tick **Allow squash merging** (để mỗi PR thành 1 commit gọn), có thể bỏ tick 2 kiểu còn lại cho thống nhất.
   - Tick **Always suggest updating pull request branches**.
   - Tick **Automatically delete head branches** (merge xong tự xóa nhánh).

---

## Bước 4 — Mời 3 thành viên (3 phút)

1. **Settings** → cột trái mục **Access** → **Collaborators** (GitHub có thể hỏi lại mật khẩu).
2. Bấm **Add people** → gõ username của Phúc → chọn đúng người → **Add … to this repository**. Làm lại cho Đức Tâm, Yến Trinh.
3. Mỗi bạn sẽ nhận email mời. Nhắn nhóm: *"Vào email bấm **View invitation → Accept invitation**, hoặc mở https://github.com/duyenphung206-sudo/nlp-de26-phoner-covid19/invitations"*.
4. Chờ cả 3 nhận lời mời (trang Collaborators không còn chữ *Pending Invite*) rồi mới làm Bước 6 — nếu chưa nhận thì Issue không gán được cho bạn đó.

---

## Bước 5 — Điền username vào kế hoạch (3 phút)

Ngay trên web, không cần Desktop:

1. Mở file `plan/team.json` → bấm biểu tượng **bút chì (Edit this file)**.
2. Điền username (không có `@`), ví dụ:
   ```json
   "thanh_vien": {"Phúc": "phuc-xyz", "Hoàng Duyên": "duyenphung206-sudo", "Đức Tâm": "tam-abc", "Yến Trinh": "trinh-123"}
   ```
3. Bấm **Commit changes…** → ô message gõ `Điền username nhóm` → chọn **Commit directly to the main branch** → **Commit changes**.
4. Làm tương tự với `README.md` (cột **GitHub** trong bảng thành viên, thay `@…`).

---

## Bước 6 — Tạo bảng Project để xem tiến độ cả nhóm (8 phút)

> Làm bước này **trước** Bước 7, để Issue tạo ra được tự đưa vào bảng.

1. Trong repo, bấm tab **Projects** → **New project** (nếu chỉ thấy **Link a project** thì bấm vào đó → **New project**).
2. Chọn mẫu **Board** (Kanban) → **Project name**: `Tiến độ Đề 26 — BC1` → **Create project**.
3. Bật tự thêm Issue vào bảng: trong Project bấm **⋯** (góc trên phải) → **Workflows** →
   - **Auto-add to project** → **Edit** → chọn repository `nlp-de26-phoner-covid19`, filter giữ `is:issue,pr is:open` → **Save and turn on workflow**.
   - Kiểm tra **Item closed** và **Pull request merged** đang **On** (mặc định đã bật) → Issue đóng thì tự sang cột **Done**.
4. Đặt tên cột cho dễ hiểu (bấm **⋯** trên đầu cột → **Rename** hoặc đổi trong field **Status**): `Todo` → `Cần làm`, `In Progress` → `Đang làm`, `Done` → `Xong`. Có thể thêm cột `Chờ review`.
5. Thêm 1 khung nhìn theo người: bấm **+ New view** → **Table** → bấm tên view đổi thành `Theo người` → **⋯ → Group by → Assignees**. Bật thêm cột **Milestone** và **Labels** (bấm **+** ở cuối hàng tiêu đề).
6. Quay về repo → tab **Projects** → nếu chưa thấy project vừa tạo thì bấm **Link a project** → chọn nó.
7. Trong Project: **⋯ → Settings → Manage access → Invite collaborators** → thêm 3 bạn với quyền **Write**.

---

## Bước 7 — Tạo 26 Issue + Milestone BC1 bằng 1 nút bấm (5 phút)

1. Tab **Actions** của repo. Nếu GitHub hỏi, bấm **I understand my workflows, go ahead and enable them**.
2. Cột trái chọn **Tạo Issue từ kế hoạch** → bên phải bấm **Run workflow** →
   - Branch: `main` · File kế hoạch: `plan/tasks_bc1.json` · Chạy thử: `false`
   - Bấm nút xanh **Run workflow**.
3. Chờ khoảng 1 phút, F5: dòng chạy có dấu **✓ xanh** là xong. Bấm vào để xem bảng tóm tắt các Issue đã tạo.
4. Kiểm tra:
   - Tab **Issues** → có `T01` … `T26`; `T08`, `T12`, `T14` (phần Phúc đã xong) đã **Closed**.
   - **Issues → Milestones** → có **BC1 — Báo cáo tiến độ 1 (22/10/2026)** với thanh % hoàn thành.
   - Mỗi Issue đã gán đúng người (cột phải **Assignees**). Ai chưa được gán: sửa `plan/team.json` rồi gán tay trong Issue (bấm **Assignees** → chọn).
5. Nếu dấu **✗ đỏ**: bấm vào xem dòng bắt đầu bằng `!` — thường là chưa bật quyền. Vào **Settings → Actions → General → Workflow permissions** → chọn **Read and write permissions** → **Save** → chạy lại (chạy lại không tạo trùng).

---

## Bước 8 — Bảo vệ nhánh main (2 phút, cần GitHub Pro / Student Pack)

GitHub chỉ cho bật bảo vệ nhánh trên repo **private** khi tài khoản là **Pro** trở lên. Nếu đã có Student Pack:

1. **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
2. **Ruleset Name**: `bao-ve-main` · **Enforcement status**: **Active**.
3. **Target branches → Add target → Include default branch**.
4. Tick: **Restrict deletions**, **Require a pull request before merging** (ô **Required approvals** = `1`), **Block force pushes** → **Create**.

Chưa có Pro: bỏ qua bước này, cả nhóm giữ quy tắc *"không ai commit thẳng vào main, mọi thay đổi qua Pull Request"* (đã ghi trong `CONTRIBUTING.md`).

---

## Bước 9 — Nhắn cho nhóm (copy nguyên văn)

> Repo đồ án đã sẵn sàng: https://github.com/duyenphung206-sudo/nlp-de26-phoner-covid19
> 1) Nhận lời mời trong email (hoặc link .../invitations).
> 2) Đọc **docs/HUONG_DAN_2_THANH_VIEN.md** (15 phút) và cài GitHub Desktop.
> 3) Vào tab Issues → **Assignee: mình** để thấy việc của mình, có sẵn đầu vào – đầu ra – xong khi – hạn chót.
> 4) Việc đầu tiên hạn **13/10**: setup + mở 1 Pull Request thử (T03–T06). Phúc đưa phần baseline/zero-shot đã làm lên qua PR (T03).
> 5) Mỗi tối trước 22h comment 3 dòng vào Issue đang làm: Đã xong / Mai làm / Đang vướng.
> Tiến độ chung xem ở Issues → Milestones → BC1 và bảng Project.

---

## ✅ Tự kiểm tra cuối cùng

- [ ] Repo **private**, README hiển thị đúng
- [ ] 3 bạn đã là Collaborator (không còn *Pending*)
- [ ] `plan/team.json` và bảng README đã có username thật
- [ ] Project board có Issue, auto-add đang bật
- [ ] Milestone BC1 có 26 Issue, 3 Issue đã đóng
- [ ] (nếu có Pro) Ruleset `bao-ve-main` đang **Active**
- [ ] Đã gửi tin nhắn Bước 9 · Comment "Xong" vào Issue **T02** rồi đóng nó
