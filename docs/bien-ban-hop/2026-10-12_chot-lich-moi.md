# Biên bản họp — 12/10/2026: chốt lịch mới đến Báo cáo tiến độ 1

- **Hình thức:** online · **Thời gian:** tối 12/10, 30 phút · **Chủ trì:** Hoàng Duyên · **Thư ký:** …
- **Có mặt:** Phúc · Hoàng Duyên · Đức Tâm · Yến Trinh

## Chương trình (đã chuẩn bị sẵn)

1. **Tình hình:** Phúc đã xong baseline CRF (micro-F1 0,9199 / macro-F1 0,8771) và zero-shot (0,4760 / 0,1996) + `metrics.py` → mục (3) của BC1 đã có số.
2. **Lịch mới 12/10 → 22/10** (xem `docs/KE_HOACH_BC1.md`):
   - 13/10: `data.py` (Tâm), môi trường + PR thử (cả nhóm), Phúc đưa phần đã làm lên repo.
   - 15/10: `train_ner.py` (Duyên), EDA (Tâm), tóm tắt bài báo (Trinh), phần viết của Phúc.
   - 18/10: PhoBERT / XLM-R / mBERT × 3 seed xong.
   - 19/10: mọi người viết xong phần mình · bảng mean ± std sơ bộ.
   - 20/10: kiểm tra chéo số liệu + họp rà soát · 21/10 sửa · **22/10 nộp**.
3. **Chốt hợp đồng chung** (`docs/QUY_UOC_CHUNG.md`): seed 42/123/2024 · lr 5e-5 · batch 16 × 2 · 15 epoch / dừng sớm 3 · strict IOB2 · std mẫu.
4. **Cách làm trên GitHub:** 1 việc = 1 Issue = 1 nhánh = 1 PR có `Closes #` · comment tiến độ mỗi tối trước 22h · review trong 12 giờ.
5. Hỏi cô: ngày nộp BC2 / cuối kỳ; kênh nộp BC1; dùng bản dữ liệu đã tách từ sẵn có được không.

## Quyết định

1. Hợp đồng chung: ☐ đồng ý như đề xuất · ☐ sửa: …
2. Phân công giữ nguyên 4 vai trò: ☐ đồng ý · ☐ sửa: …
3. Người hỏi cô các mục ở (5): …

## Việc phát sinh

| Việc | Người | Hạn | Issue |
|---|---|---|---|
| | | | # |
