# data/ — KHÔNG commit dữ liệu vào đây

Giấy phép PhoNER_COVID19 chỉ cho dùng nghiên cứu/học tập và **không cho phát tán lại**, nên `.gitignore` đã chặn toàn bộ thư mục này (trừ file README này).

## Cách tải (máy cá nhân hoặc Colab)

```bash
git clone https://github.com/VinAIResearch/PhoNER_COVID19.git
# chép 2 thư mục vào data/ của repo nhóm
cp -r PhoNER_COVID19/data/word PhoNER_COVID19/data/syllable data/
```

Sau khi chép, cấu trúc phải là:

```
data/
├── word/       train_word.json  dev_word.json  test_word.json        (đã tách từ — PhoBERT, CRF)
└── syllable/   train_syllable.json  dev_syllable.json  test_syllable.json   (âm tiết — XLM-R, mBERT, zero-shot)
```

Mỗi dòng là 1 câu: `{"words": [...], "tags": [...]}`. Số câu mong đợi: train 5.027 · dev 2.000 · test 3.000.
Tên nhãn thật trong file: `PATIENT_ID, NAME, AGE, GENDER, JOB, LOCATION, ORGANIZATION, SYMPTOM_AND_DISEASE, TRANSPORTATION, DATE`.

Trích dẫn bắt buộc: T. H. Truong, M. H. Dao, D. Q. Nguyen, "COVID-19 Named Entity Recognition for Vietnamese," NAACL 2021.
