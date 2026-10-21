# app/ — Demo Streamlit (D): nhập văn bản → nhận dạng thực thể COVID-19

Người phụ trách: **Yến Trinh** · Issue T30 (làm demo), T37 (triển khai + ảnh/video), T40 (viết mục 4.7).
Yêu cầu của cô: ứng dụng **Streamlit**, nhập văn bản (input) → hiện thực thể (output), dùng **mô hình tốt nhất trong 3 kiến trúc**.

| File | Vai trò |
|---|---|
| `app.py` | Giao diện: thanh bên (chọn mô hình, F1, ngưỡng tin cậy, chú thích 10 loại), tab *Nhập 1 đoạn văn*, tab *Nhiều câu (file .txt)*, tab *Giới thiệu* |
| `ner_core.py` | Xử lý (không phụ thuộc Streamlit): NFC → tách token / tách từ → subword → mô hình → sửa BIO → gộp thực thể + độ tin cậy |
| `requirements.txt`, `packages.txt` | Thư viện Python và gói hệ thống (Java cho VnCoreNLP) khi triển khai Streamlit Community Cloud |
| `mo_hinh/` | Nơi đặt mô hình (xem README trong đó) |

## Chạy trên máy (VS Code)

```bash
# ở thư mục gốc repo, đã kích hoạt môi trường ảo (.venv)
pip install -r app/requirements.txt
streamlit run app/app.py          # trình duyệt tự mở http://localhost:8501
```

PhoBERT cần tách từ: app thử **VnCoreNLP** (cần Java 8+, giống công cụ tạo dữ liệu) → không có Java thì dùng **underthesea** →
không có nữa thì để mức âm tiết (độ chính xác giảm, app ghi rõ đang dùng cách nào ở mục "Các bước xử lý").

## Tham khảo thiết kế
Tô màu thực thể trong câu theo kiểu **displaCy** (spaCy) và widget NER trên trang mô hình của Hugging Face; câu mẫu bấm 1 lần;
bảng thực thể có cột độ tin cậy; mục "Các bước xử lý bên trong" để giải thích pipeline khi thuyết trình. Chi tiết: `docs/SO_TAY_KY_THUAT.md` §9.

## Kiểm tra tự động (không cần mở trình duyệt)
```python
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("app/app.py", default_timeout=120).run()
at.button[0].click().run()                                           # bấm câu mẫu 1
[b for b in at.button if "Nhận dạng" in b.label][0].click().run()
print(at.exception, [(m.label, m.value) for m in at.metric])
```
