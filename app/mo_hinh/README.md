# app/mo_hinh/ — đặt mô hình đã fine-tune vào đây (KHÔNG commit, .gitignore đã chặn)

Mỗi thư mục con = 1 mô hình, tạo bởi ô 11 của notebook huấn luyện (`mo_hinh_<khoa>.zip` trên Google Drive `NLP_De26/`):

```
app/mo_hinh/
├── phobert/   config.json  model.safetensors  tokenizer files  thong_tin_de26.json
├── xlmr/      ...
└── mbert/     ...
```

Giải nén zip vào đúng thư mục con (mở thư mục ra phải thấy ngay `config.json`). App tự liệt kê, mô hình có Micro-F1 test cao nhất đứng đầu.
Không có mô hình ở máy? Đặt biến môi trường `NER_MODEL=<tài-khoản>/<repo>` (Hugging Face Hub) trước khi chạy.
