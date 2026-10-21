# Tóm tắt phân tích lỗi (test, seed 42; 11735 thực thể thật)

## Số lỗi theo nhóm
| Nhóm lỗi | CRF | Zero-shot | PhoBERT | XLM-R | mBERT |
|---|---|---|---|---|---|
| Sai loại | 125 | 875 | 81 | 96 | 90 |
| Sai biên | 291 | 194 | 273 | 309 | 325 |
| Sai cả hai | 79 | 171 | 20 | 18 | 29 |
| Bỏ sót | 639 | 6253 | 137 | 209 | 211 |
| Dự đoán thừa | 218 | 450 | 263 | 195 | 233 |
| Tổng lỗi | 1352 | 7943 | 774 | 827 | 888 |

## Nhầm loại hay gặp nhất
| Mô hình | Thật → Dự đoán | Số lần |
|---|---|---|
| CRF | ORGANIZATION → LOCATION | 53 |
| CRF | LOCATION → ORGANIZATION | 32 |
| CRF | NAME → LOCATION | 6 |
| CRF | LOCATION → PATIENT_ID | 5 |
| CRF | PATIENT_ID → DATE | 5 |
| CRF | DATE → PATIENT_ID | 4 |
| CRF | PATIENT_ID → TRANSPORTATION | 4 |
| CRF | TRANSPORTATION → LOCATION | 3 |
| Zero-shot | LOCATION → ORGANIZATION | 840 |
| Zero-shot | PATIENT_ID → NAME | 20 |
| Zero-shot | LOCATION → NAME | 5 |
| Zero-shot | ORGANIZATION → LOCATION | 3 |
| Zero-shot | DATE → LOCATION | 3 |
| Zero-shot | ORGANIZATION → NAME | 1 |
| Zero-shot | NAME → ORGANIZATION | 1 |
| Zero-shot | AGE → NAME | 1 |
| PhoBERT | ORGANIZATION → LOCATION | 33 |
| PhoBERT | LOCATION → ORGANIZATION | 31 |
| PhoBERT | PATIENT_ID → DATE | 3 |
| PhoBERT | DATE → LOCATION | 3 |
| PhoBERT | LOCATION → DATE | 2 |
| PhoBERT | LOCATION → PATIENT_ID | 1 |
| PhoBERT | LOCATION → SYMPTOM_AND_DISEASE | 1 |
| PhoBERT | JOB → TRANSPORTATION | 1 |
| XLM-R | ORGANIZATION → LOCATION | 46 |
| XLM-R | LOCATION → ORGANIZATION | 29 |
| XLM-R | PATIENT_ID → DATE | 4 |
| XLM-R | DATE → LOCATION | 3 |
| XLM-R | NAME → LOCATION | 2 |
| XLM-R | LOCATION → DATE | 2 |
| XLM-R | LOCATION → PATIENT_ID | 1 |
| XLM-R | LOCATION → JOB | 1 |
| mBERT | ORGANIZATION → LOCATION | 41 |
| mBERT | LOCATION → ORGANIZATION | 28 |
| mBERT | PATIENT_ID → DATE | 4 |
| mBERT | NAME → LOCATION | 3 |
| mBERT | DATE → LOCATION | 3 |
| mBERT | LOCATION → DATE | 2 |
| mBERT | LOCATION → PATIENT_ID | 1 |
| mBERT | ORGANIZATION → NAME | 1 |

## Lỗi chung và lỗi riêng
- Thực thể thật bị **mọi** mô hình (PhoBERT, XLM-R, mBERT) làm sai: **349**
- Chỉ riêng PhoBERT sai: 64 (tổng PhoBERT sai 511)
- Chỉ riêng XLM-R sai: 102 (tổng XLM-R sai 632)
- Chỉ riêng mBERT sai: 149 (tổng mBERT sai 655)
- Loại thực thể hay bị cả 3 mô hình cùng sai: LOCATION (120), SYMPTOM_AND_DISEASE (96), ORGANIZATION (53), PATIENT_ID (27), JOB (17)

## Thực thể đặc thù
| Loại | Số thực thể thật | CRF | Zero-shot | PhoBERT | XLM-R | mBERT |
|---|---|---|---|---|---|---|
| PATIENT_ID | 2005 | 50 | 2005 | 30 | 28 | 41 |
| ORGANIZATION | 771 | 148 | 104 | 76 | 108 | 104 |
| JOB | 173 | 98 | 173 | 28 | 56 | 49 |
| SYMPTOM_AND_DISEASE | 1136 | 302 | 1136 | 140 | 186 | 188 |