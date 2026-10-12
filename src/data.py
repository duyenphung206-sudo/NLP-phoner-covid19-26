"""data.py - Đọc dữ liệu PhoNER_COVID19 và tạo bảng nhãn dùng chung.

Người phụ trách: Đức Tâm · Issue T07 · hạn 13/10
Trạng thái: KHUNG MẪU — điền phần TODO, giữ nguyên tên hàm và kiểu trả về vì train_ner.py, EDA, demo đều gọi các hàm này.

Cách tự kiểm tra (chạy ở thư mục gốc repo):  python src/data.py
Xong khi in ra: train 5027 / dev 2000 / test 3000 câu cho CẢ 2 bản, 21 nhãn, 0 câu lệch số từ - số nhãn.
"""

import json
import os

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUONG_DAN_CAU_HINH = os.path.join(THU_MUC_GOC, "configs", "common.json")


def doc_cau_hinh(duong_dan=DUONG_DAN_CAU_HINH):
    """Đọc configs/common.json.
    Đầu ra : dict cấu hình chung của nhóm."""
    with open(duong_dan, encoding="utf-8") as f:
        return json.load(f)


def doc_file_json(duong_dan):
    """Đọc 1 file .json của PhoNER_COVID19 (mỗi dòng {"words": [...], "tags": [...]}).
    Đầu vào : đường dẫn file.
    Đầu ra  : (cac_cau, cac_nhan) - 2 list cùng độ dài; mỗi phần tử là list từ / list nhãn của 1 câu.
    Gợi ý   : có thể lấy lại hàm doc_file_json trong notebook 01 của Phúc."""
    # TODO (Tâm): đọc từng dòng, json.loads, gom words và tags
    raise NotImplementedError("TODO - Tâm (T07)")


def tai_du_lieu(muc="word", thu_muc_data=None):
    """Đọc đủ 3 tập của 1 phiên bản dữ liệu.
    Đầu vào : muc = "word" (đã tách từ, dùng cho PhoBERT, CRF) hoặc "syllable" (âm tiết, dùng cho XLM-R, mBERT).
    Đầu ra  : dict {"train": (cac_cau, cac_nhan), "dev": (...), "test": (...)}
    Tên file: data/{muc}/{split}_{muc}.json  ví dụ data/word/train_word.json"""
    # TODO (Tâm)
    raise NotImplementedError("TODO - Tâm (T07)")


def tao_label2id(cau_hinh=None):
    """Tạo label2id và id2label CỐ ĐỊNH theo thứ tự trong configs/common.json (khóa "nhan", 21 nhãn).
    Đầu ra  : (label2id, id2label) - 2 dict.
    Lưu ý   : cả nhóm phải dùng đúng hàm này, không tự sắp xếp lại nhãn."""
    # TODO (Tâm)
    raise NotImplementedError("TODO - Tâm (T07)")


def kiem_tra_du_lieu(du_lieu, label2id):
    """Kiểm tra: số từ = số nhãn ở mọi câu; mọi nhãn nằm trong label2id; đếm nhãn I-X đứng sai chỗ.
    Đầu ra  : dict thống kê lỗi, ví dụ {"lech_do_dai": 0, "nhan_la": 0, "I_sai_cho": 0}"""
    # TODO (Tâm)
    raise NotImplementedError("TODO - Tâm (T07)")


if __name__ == "__main__":
    cau_hinh = doc_cau_hinh()
    label2id, id2label = tao_label2id(cau_hinh)
    print("Số nhãn:", len(label2id), "(mong đợi 21)")
    for muc in ["word", "syllable"]:
        du_lieu = tai_du_lieu(muc)
        so_cau = {split: len(du_lieu[split][0]) for split in ["train", "dev", "test"]}
        print(muc, so_cau, "(mong đợi", cau_hinh["du_lieu"]["so_cau_mong_doi"], ")")
        print("  Kiểm tra:", kiem_tra_du_lieu(du_lieu, label2id))
