"""metrics.py - Hàm chấm điểm F1 dùng chung cho cả nhóm.

Quy ước của nhóm: chấm theo THỰC THỂ bằng seqeval, mode="strict", scheme=IOB2.
Một thực thể chỉ đúng khi đúng cả loại lẫn ranh giới (từ đầu đến từ cuối).
Cách chạy tự kiểm tra: python src/metrics.py
"""

import json
import os

from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2

# Danh sách 10 loại thực thể của PhoNER_COVID19
CAC_LOAI_THUC_THE = ["PATIENT_ID", "NAME", "AGE", "GENDER", "JOB", "LOCATION",
                     "ORGANIZATION", "SYMPTOM_AND_DISEASE", "TRANSPORTATION", "DATE"]

CHE_DO_CHAM = "strict_IOB2"


def tinh_metrics(ten_mo_hinh, y_that, y_du_doan):
    """Chấm F1 mức thực thể (strict, IOB2).
    Đầu vào : tên mô hình, nhãn đúng và nhãn dự đoán (list các câu, mỗi câu là list nhãn BIO).
    Đầu ra  : dict gồm P/R/F1 micro, F1 macro, số thực thể và F1 của đủ 10 loại."""
    # Bước 1: lấy báo cáo từng loại; zero_division=0 để loại không có dự đoán thì điểm = 0
    bao_cao = classification_report(y_that, y_du_doan, output_dict=True,
                                    zero_division=0, mode="strict", scheme=IOB2)

    # Bước 2: tạo sẵn đủ 10 loại với F1 = 0.0, loại nào seqeval có báo cáo thì ghi đè
    f1_tung_loai = {}
    for loai in CAC_LOAI_THUC_THE:
        f1_tung_loai[loai] = 0.0

    so_thuc_the = 0
    for loai in CAC_LOAI_THUC_THE:
        if loai in bao_cao:
            f1_tung_loai[loai] = round(float(bao_cao[loai]["f1-score"]), 4)
            so_thuc_the = so_thuc_the + int(bao_cao[loai]["support"])

    # Bước 3: các chỉ số tổng (micro, macro) tính riêng bằng các hàm của seqeval
    precision = precision_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)
    recall = recall_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)
    f1_micro = f1_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)
    f1_macro = f1_score(y_that, y_du_doan, average="macro", zero_division=0,
                        mode="strict", scheme=IOB2)

    ket_qua = {
        "ten_mo_hinh": ten_mo_hinh,
        "che_do_cham": CHE_DO_CHAM,
        "so_thuc_the": so_thuc_the,
        "precision_micro": round(float(precision), 4),
        "recall_micro": round(float(recall), 4),
        "f1_micro": round(float(f1_micro), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_tung_loai": f1_tung_loai,
    }
    return ket_qua


def luu_json(du_lieu, duong_dan):
    """Ghi dict ra file JSON (indent=2, giữ tiếng Việt).
    Đầu vào : du_lieu (dict) và duong_dan file; tự tạo thư mục chứa file nếu chưa có.
    Đầu ra  : không có, chỉ ghi file."""
    thu_muc = os.path.dirname(duong_dan)
    if thu_muc != "":
        os.makedirs(thu_muc, exist_ok=True)
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)


def in_dung_sai(ten_so, so_that, so_mong_doi):
    """So 1 số thực tế với số mong đợi, in ĐÚNG hoặc SAI.
    Đầu vào : tên số, số thực tế, số mong đợi.
    Đầu ra  : True nếu đúng (lệch dưới 0.0001), ngược lại False."""
    chenh_lech = abs(so_that - so_mong_doi)
    if chenh_lech < 0.0001:
        print(f"  {ten_so:18s} thực tế = {so_that:.4f} | mong đợi = {so_mong_doi:.4f} -> ĐÚNG")
        return True
    print(f"  {ten_so:18s} thực tế = {so_that:.4f} | mong đợi = {so_mong_doi:.4f} -> SAI")
    return False


def chay_thu_3_cau():
    """Tự kiểm tra tinh_metrics bằng 3 câu tự tạo đã tính tay.
    Đầu vào : không có.
    Đầu ra  : True nếu mọi số đều ĐÚNG, ngược lại False."""
    # Câu 1 đúng hoàn toàn, câu 2 sai biên (NAME thiếu I-NAME), câu 3 sai loại (AGE đoán thành DATE)
    gold = [["B-LOCATION", "I-LOCATION"], ["B-NAME", "I-NAME", "O"], ["B-AGE"]]
    pred = [["B-LOCATION", "I-LOCATION"], ["B-NAME", "O", "O"], ["B-DATE"]]

    kq = tinh_metrics("thu_3_cau", gold, pred)
    print("Kết quả tinh_metrics:", kq)

    # Tính tay: 3 thực thể gold, 3 thực thể đoán, chỉ 1 cái trùng -> P = R = F1 = 1/3
    # Macro tính trên 4 loại xuất hiện (LOCATION, NAME, AGE, DATE): (1 + 0 + 0 + 0) / 4 = 0.25
    tat_ca_dung = True
    if not in_dung_sai("precision_micro", kq["precision_micro"], 0.3333):
        tat_ca_dung = False
    if not in_dung_sai("recall_micro", kq["recall_micro"], 0.3333):
        tat_ca_dung = False
    if not in_dung_sai("f1_micro", kq["f1_micro"], 0.3333):
        tat_ca_dung = False
    if not in_dung_sai("f1_macro", kq["f1_macro"], 0.25):
        tat_ca_dung = False
    if not in_dung_sai("F1 LOCATION", kq["f1_tung_loai"]["LOCATION"], 1.0):
        tat_ca_dung = False
    if not in_dung_sai("F1 NAME", kq["f1_tung_loai"]["NAME"], 0.0):
        tat_ca_dung = False
    if not in_dung_sai("F1 AGE", kq["f1_tung_loai"]["AGE"], 0.0):
        tat_ca_dung = False
    if not in_dung_sai("F1 DATE", kq["f1_tung_loai"]["DATE"], 0.0):
        tat_ca_dung = False

    if len(kq["f1_tung_loai"]) == 10:
        print("  f1_tung_loai có đủ 10 loại -> ĐÚNG")
    else:
        print("  f1_tung_loai không đủ 10 loại -> SAI")
        tat_ca_dung = False
    return tat_ca_dung


if __name__ == "__main__":
    print("=== Tự kiểm tra metrics.py bằng 3 câu tự tạo ===")
    ket_qua_kiem_tra = chay_thu_3_cau()
    if ket_qua_kiem_tra:
        print("TẤT CẢ ĐÚNG")
    else:
        print("CÓ SỐ SAI -> dừng lại, không sửa số mong đợi cho khớp")


# GHI CHÚ VẤN ĐÁP
# 1. Vì sao chấm mức thực thể mà không chấm từng từ?
#    Khoảng 74-79% nhãn là O nên chấm từng từ luôn rất cao dù bỏ sót nhiều thực thể. Chấm mức thực thể
#    chỉ tính đúng khi khớp cả loại lẫn ranh giới (từ đầu đến từ cuối), phản ánh đúng chất lượng NER.
# 2. strict + IOB2 khác chế độ mặc định của seqeval ở đâu?
#    Mặc định thì nhãn I-X đứng sau O (không có B-X) vẫn được coi là bắt đầu 1 thực thể; strict + IOB2
#    thì không tính nhãn lỗi đó là thực thể. Cả nhóm dùng chung quy ước này nên số so sánh được với nhau.
# 3. Vì sao phải ép float()/int() trước khi lưu JSON?
#    Kết quả của seqeval có thể là kiểu số của numpy, thư viện json không lưu được kiểu đó,
#    nên đổi về float/int thường của Python.
