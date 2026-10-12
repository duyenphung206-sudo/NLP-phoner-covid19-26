"""train_ner.py - Fine-tune 1 kiến trúc cho NER, DÙNG CHUNG cho PhoBERT / XLM-R / mBERT.

Người phụ trách: Hoàng Duyên · Issue T10 · hạn 15/10 · Phúc review
Trạng thái: KHUNG MẪU — giữ nguyên tham số dòng lệnh và định dạng JSON đầu ra để aggregate.py đọc được.

Cách chạy (1 dòng lệnh, ở thư mục gốc repo):
    python src/train_ner.py --mo_hinh phobert --seed 42
    python src/train_ner.py --mo_hinh xlmr --seed 123
    python src/train_ner.py --mo_hinh phobert_khong_tach_tu --seed 42      # phần nâng cao (Phúc)
Thêm --thu_nhanh 500 để chạy thử trên 500 câu, 1 epoch.

Xong khi (Issue T10):
  (a) PhoBERT chạy 1 epoch trên 500 câu không lỗi, số id = số nhãn ở mọi câu, F1 dev > 0
  (b) XLM-R và mBERT chạy >= 50 bước không lỗi
  (c) 2 seed khác nhau cho loss khác nhau
  (d) tự lưu JSON đúng mẫu results/_MAU_ket_qua_finetune.json + checkpoint tốt nhất (ngoài repo)
"""

import argparse
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data import doc_cau_hinh, tai_du_lieu, tao_label2id   # noqa: E402  (Tâm, T07)
from metrics import tinh_metrics, luu_json                 # noqa: E402  (Phúc, đã có)


def doc_tham_so():
    cau_hinh = doc_cau_hinh()
    sts = cau_hinh["sieu_tham_so"]
    p = argparse.ArgumentParser(description="Fine-tune NER PhoNER_COVID19")
    p.add_argument("--mo_hinh", required=True, choices=list(cau_hinh["mo_hinh"].keys()))
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--lr", type=float, default=sts["learning_rate"])
    p.add_argument("--batch_size", type=int, default=sts["batch_size"])
    p.add_argument("--so_epoch", type=int, default=sts["so_epoch_toi_da"])
    p.add_argument("--max_length", type=int, default=sts["max_length"])
    p.add_argument("--thu_muc_checkpoint", default="/content/drive/MyDrive/NLP_De26/checkpoints")
    p.add_argument("--thu_nhanh", type=int, default=0, help="Chỉ dùng N câu train, 1 epoch (để thử code)")
    return p.parse_args(), cau_hinh


def can_nhan_tokenizer_nhanh(tokenizer, cac_tu, cac_nhan, label2id, max_length):
    """Căn nhãn cho tokenizer nhanh (XLM-R, mBERT) bằng word_ids():
    nhãn thật cho mảnh đầu của mỗi từ, -100 cho các mảnh còn lại và token đặc biệt."""
    # TODO (Duyên)
    raise NotImplementedError


def can_nhan_phobert(tokenizer, cac_tu, cac_nhan, label2id, max_length):
    """PhoBERT dùng tokenizer chậm (không có word_ids) -> tự encode từng từ rồi ghép.
    Kiểm tra len(input_ids) == len(labels) ở mọi câu."""
    # TODO (Duyên) - xem mẫu ở sheet "Hướng dẫn kỹ thuật" trong PhanCong_Phuc.xlsx, mục 3.6
    raise NotImplementedError


def du_doan_ve_muc_tu(logits, labels, id2label):
    """Lấy argmax tại mảnh đầu của mỗi từ (bỏ vị trí -100) -> list nhãn chuỗi theo từ cho seqeval."""
    # TODO (Duyên)
    raise NotImplementedError


def main():
    args, cau_hinh = doc_tham_so()
    thong_tin = cau_hinh["mo_hinh"][args.mo_hinh]
    muc = "word" if thong_tin["muc_du_lieu"] == "muc_tu" else "syllable"
    label2id, id2label = tao_label2id(cau_hinh)
    du_lieu = tai_du_lieu(muc)
    bat_dau = time.time()

    # TODO (Duyên): set_seed(args.seed) TRƯỚC khi tạo model
    # TODO: AutoTokenizer + AutoModelForTokenClassification(thong_tin["ten"], num_labels=21, id2label, label2id)
    # TODO: huấn luyện, chấm dev mỗi epoch bằng tinh_metrics, dừng sớm sau cau_hinh["sieu_tham_so"]["dung_som_sau"] epoch
    # TODO: nạp checkpoint tốt nhất theo f1_micro dev, chấm test
    ket_qua_test = None        # = tinh_metrics(f"{args.mo_hinh} seed {args.seed}", y_that_test, y_du_doan_test)

    # Ghép thêm thông tin lượt chạy rồi lưu (định dạng: results/_MAU_ket_qua_finetune.json)
    ket_qua = dict(ket_qua_test or {})
    ket_qua.update({
        "khoa_mo_hinh": args.mo_hinh,
        "model": thong_tin["ten"],
        "muc_du_lieu": thong_tin["muc_du_lieu"],
        "seed": args.seed,
        "best_epoch": None,
        "f1_micro_dev": None,
        "sieu_tham_so": {"lr": args.lr, "batch_size": args.batch_size, "so_epoch_toi_da": args.so_epoch,
                         "max_length": args.max_length},
        "thoi_gian_train_giay": round(time.time() - bat_dau),
        "thu_vien": {},          # TODO: {"transformers": transformers.__version__, "torch": torch.__version__}
        "nguoi_chay": thong_tin["nguoi"],
    })
    luu_json(ket_qua, os.path.join("results", f"{args.mo_hinh}_seed{args.seed}.json"))


if __name__ == "__main__":
    main()
