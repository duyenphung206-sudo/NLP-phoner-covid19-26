## Pull Request này làm gì?

<!-- 1–3 câu. Ví dụ: Thêm data.py đọc 2 bản dữ liệu (mức từ, âm tiết) và configs/common.json. -->

Closes #<!-- số Issue, ví dụ: Closes #7 -->

## Kết quả / bằng chứng đã đạt "Xong khi"

<!-- Dán số liệu, ảnh chụp, hoặc output khi chạy. Ví dụ:
train 5027 / dev 2000 / test 3000 câu (cả 2 bản) — 0 câu lệch số từ/số nhãn
results/xlmr_seed42.json: f1_micro = 0.9xxx
-->

## Tự kiểm tra trước khi nhờ review

- [ ] Làm trên nhánh riêng `ten/Txx-...`, không phải `main`
- [ ] Đã đạt đủ các ý **Xong khi** trong Issue (đã tick trong Issue)
- [ ] KHÔNG có file dữ liệu, checkpoint (`.bin`, `.safetensors`, `.pt`, `.pkl`), file nén
- [ ] File kết quả đặt đúng tên `results/{khoa_mo_hinh}_seed{seed}.json`, đủ trường như `results/_MAU_ket_qua_finetune.json`
- [ ] Notebook đã **Restart & Run all** chạy hết không lỗi (hoặc ghi rõ cell nào chỉ chạy trên Colab)
- [ ] Dùng đúng giá trị trong `configs/common.json` (seed, siêu tham số, cách chấm)
- [ ] Đã viết/cập nhật phần tương ứng trong file báo cáo chung (nếu Issue yêu cầu)

## Nhờ review

<!-- Bấm "Reviewers" ở cột phải để chọn 1 bạn. Ghi chỗ cần bạn ấy xem kỹ. -->
