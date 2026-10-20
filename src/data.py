"""data.py - Đọc dữ liệu PhoNER_COVID19 và tạo bảng nhãn dùng chung cho cả nhóm.

Người phụ trách: Đức Tâm · Issue T07
Cách tự kiểm tra (ở thư mục gốc repo):  python src/data.py
Xong khi in ra: train 5027 / dev 2000 / test 3000 câu cho CẢ 2 bản, 21 nhãn, 0 câu lệch số từ - số nhãn.

Tiền xử lý duy nhất: chuẩn hóa Unicode NFC cho từng token (nhãn giữ nguyên vì 1 token -> 1 token).
Lý do: mỗi phiên bản dữ liệu gốc có 1.052 token chưa ở dạng NFC (dấu viết tách rời chữ cái) lẫn với dạng dựng sẵn;
cùng một chữ "Hà" có thể là 2 chuỗi byte khác nhau -> tokenizer cắt khác nhau. NFC là chuẩn an toàn mặc định
cho văn bản tiếng Việt (bài giảng Session 2 - Words, Tokens; Unicode Standard Annex #15).
"""

import json
import os
import unicodedata
from collections import Counter

THU_MUC_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUONG_DAN_CAU_HINH = os.path.join(THU_MUC_GOC, "configs", "common.json")
CAC_TAP = ["train", "dev", "test"]


def doc_cau_hinh(duong_dan=DUONG_DAN_CAU_HINH):
    """Đọc configs/common.json -> dict cấu hình chung của nhóm."""
    with open(duong_dan, encoding="utf-8") as f:
        return json.load(f)


def chuan_hoa_nfc(cac_tu):
    """Chuẩn hóa Unicode NFC cho danh sách token (không đổi số lượng token)."""
    return [unicodedata.normalize("NFC", tu) for tu in cac_tu]


def doc_file_json(duong_dan, nfc=True):
    """Đọc 1 file .json của PhoNER_COVID19 (mỗi dòng {"words": [...], "tags": [...]}).
    Đầu ra: (cac_cau, cac_nhan) - 2 list cùng độ dài; mỗi phần tử là list token / list nhãn của 1 câu."""
    cac_cau, cac_nhan = [], []
    with open(duong_dan, encoding="utf-8") as f:
        for dong in f:
            if not dong.strip():
                continue
            mau = json.loads(dong)
            cac_cau.append(chuan_hoa_nfc(mau["words"]) if nfc else mau["words"])
            cac_nhan.append(mau["tags"])
    return cac_cau, cac_nhan


def tai_du_lieu(muc="word", thu_muc_data=None, nfc=True):
    """Đọc đủ 3 tập của 1 phiên bản dữ liệu.
    muc = "word"     (đã tách từ bằng RDRSegmenter - dùng cho PhoBERT, CRF)
        = "syllable" (âm tiết - dùng cho XLM-R, mBERT, zero-shot, PhoBERT không tách từ)
    Đầu ra: {"train": (cac_cau, cac_nhan), "dev": (...), "test": (...)}"""
    if muc not in ("word", "syllable"):
        raise ValueError("muc phải là 'word' hoặc 'syllable'")
    thu_muc_data = thu_muc_data or os.path.join(THU_MUC_GOC, "data")
    du_lieu = {}
    for tap in CAC_TAP:
        duong_dan = os.path.join(thu_muc_data, muc, f"{tap}_{muc}.json")
        if not os.path.exists(duong_dan):
            raise FileNotFoundError(f"Không thấy {duong_dan}. Xem data/README.md để tải dữ liệu PhoNER_COVID19.")
        du_lieu[tap] = doc_file_json(duong_dan, nfc=nfc)
    return du_lieu


def tao_label2id(cau_hinh=None):
    """label2id, id2label CỐ ĐỊNH theo thứ tự khóa "nhan" trong configs/common.json (21 nhãn).
    Cả nhóm phải dùng đúng hàm này để id của nhãn giống nhau ở mọi mô hình."""
    cau_hinh = cau_hinh or doc_cau_hinh()
    label2id = {nhan: i for i, nhan in enumerate(cau_hinh["nhan"])}
    id2label = {i: nhan for nhan, i in label2id.items()}
    return label2id, id2label


def lay_thuc_the(nhan_cau):
    """Lấy danh sách thực thể (loai, vi_tri_dau, vi_tri_cuoi) từ dãy nhãn BIO (IOB2, vị trí tính cả 2 đầu).
    Viết tay (không cần seqeval) để file này chạy được ở mọi máy."""
    thuc_the, loai_hien_tai, dau = [], None, None
    for i, nhan in enumerate(list(nhan_cau) + ["O"]):
        bat_dau_moi = nhan.startswith("B-") or nhan == "O" or (nhan.startswith("I-") and nhan[2:] != loai_hien_tai)
        if bat_dau_moi and loai_hien_tai is not None:
            thuc_the.append((loai_hien_tai, dau, i - 1))
            loai_hien_tai = None
        if nhan.startswith("B-") or (nhan.startswith("I-") and loai_hien_tai is None):
            loai_hien_tai, dau = nhan[2:], i
    return thuc_the


def kiem_tra_du_lieu(du_lieu, label2id):
    """Kiểm tra từng tập: số token = số nhãn, nhãn nằm trong label2id, nhãn I-X đứng sai chỗ (vi phạm IOB2).
    Đầu ra: {tap: {"so_cau", "lech_do_dai", "nhan_la", "I_sai_cho", "so_thuc_the"}}"""
    ket_qua = {}
    for tap, (cac_cau, cac_nhan) in du_lieu.items():
        lech = sum(len(c) != len(n) for c, n in zip(cac_cau, cac_nhan))
        nhan_la = {x for n in cac_nhan for x in n if x not in label2id}
        i_sai = 0
        for n in cac_nhan:
            truoc = "O"
            for x in n:
                if x.startswith("I-") and truoc[2:] != x[2:]:
                    i_sai += 1
                truoc = x
        ket_qua[tap] = {"so_cau": len(cac_cau), "lech_do_dai": lech, "nhan_la": sorted(nhan_la),
                        "I_sai_cho": i_sai, "so_thuc_the": sum(len(lay_thuc_the(n)) for n in cac_nhan)}
    return ket_qua


def dem_thuc_the_theo_loai(cac_nhan):
    """Counter {loai: so_thuc_the} cho 1 tập."""
    return Counter(loai for n in cac_nhan for loai, _, _ in lay_thuc_the(n))


if __name__ == "__main__":
    cau_hinh = doc_cau_hinh()
    label2id, id2label = tao_label2id(cau_hinh)
    print("Số nhãn:", len(label2id), "(mong đợi 21)")
    for muc in ["word", "syllable"]:
        du_lieu = tai_du_lieu(muc)
        print(f"\n[{muc}] mong đợi {cau_hinh['du_lieu']['so_cau_mong_doi']}")
        for tap, kq in kiem_tra_du_lieu(du_lieu, label2id).items():
            print(f"  {tap:5s} {kq}")
