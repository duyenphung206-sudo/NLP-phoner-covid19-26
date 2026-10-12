# app/ — Demo Gradio (D)

Người phụ trách: **Yến Trinh** · bắt đầu sau BC1 (Issue T30, T37 trong kế hoạch Giai đoạn 2).

Yêu cầu của cô: giao diện Gradio/Streamlit nhập văn bản → hiển thị thực thể do **mô hình tốt nhất trong 3 kiến trúc** dự đoán; chỉ cần chạy được.
Luồng: câu nhập → (tách từ bằng `py_vncorenlp` nếu là PhoBERT) → model → gộp nhãn BIO thành thực thể → tô màu (`gr.HighlightedText`).
