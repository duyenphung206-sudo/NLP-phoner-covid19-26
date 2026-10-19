"""train_ner.py - Fine-tune 1 kiến trúc cho NER. DÙNG CHUNG cho PhoBERT / XLM-R / mBERT (chỉ đổi --mo_hinh).

Người phụ trách: Hoàng Duyên · Issue T10 (Phúc review)

Ý tưởng (giải thích ngắn cho báo cáo mục 4.4):
  1. Mỗi câu là danh sách token (từ hoặc âm tiết) kèm nhãn BIO.
  2. Tokenizer của mô hình cắt mỗi token thành 1..n mảnh subword. Nhãn thật đặt ở mảnh ĐẦU của mỗi token,
     các mảnh còn lại nhận -100 (bị bỏ qua khi tính loss) -> "căn nhãn với subword".
  3. AutoModelForTokenClassification = encoder pretrained + 1 lớp tuyến tính 768 -> 21 nhãn, softmax từng vị trí,
     loss cross-entropy trên các vị trí có nhãn (bài giảng Session 6: L = -Σ log p(y_t | x)).
  4. Huấn luyện bằng AdamW + warmup tuyến tính, chấm dev sau mỗi epoch bằng F1 mức thực thể (seqeval strict IOB2),
     giữ checkpoint dev tốt nhất, dừng sớm khi dev không tăng N epoch, rồi mới chấm test ĐÚNG 1 LẦN.

Cách chạy:
  python src/train_ner.py --mo_hinh phobert --seed 42                 # 1 lượt
  python src/train_ner.py --mo_hinh xlmr --tim_kiem random --so_lan 6  # tìm siêu tham số (mục 4.3)
  python src/train_ner.py --mo_hinh mbert --seed 42 --thu_nhanh 300    # chạy thử nhanh 300 câu, 1 epoch
"""

import argparse
import inspect
import json
import os
import sys
import time

THU_MUC_SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC_SRC)

from nap_seqeval import dam_bao_seqeval  # noqa: E402

dam_bao_seqeval()

import numpy as np  # noqa: E402
import torch  # noqa: E402
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score  # noqa: E402
from seqeval.scheme import IOB2  # noqa: E402
from transformers import (AutoModelForTokenClassification, AutoTokenizer, DataCollatorForTokenClassification,  # noqa: E402
                          EarlyStoppingCallback, Trainer, TrainingArguments, set_seed)

from data import THU_MUC_GOC, doc_cau_hinh, tai_du_lieu, tao_label2id  # noqa: E402

try:                                    # dùng hàm chấm điểm của Phúc nếu đã có trong repo (src/metrics.py)
    from metrics import tinh_metrics, luu_json  # noqa: E402
except ImportError:
    tinh_metrics = luu_json = None

CAC_LOAI = ["PATIENT_ID", "NAME", "AGE", "GENDER", "JOB", "LOCATION", "ORGANIZATION",
            "SYMPTOM_AND_DISEASE", "TRANSPORTATION", "DATE"]


# ----------------------------------------------------------------------------------------------------
# 1. Chấm điểm (giống hệt quy ước nhóm: seqeval, mode="strict", scheme=IOB2)
# ----------------------------------------------------------------------------------------------------
def cham_diem(ten, y_that, y_du_doan):
    """Trả về dict cùng định dạng với metrics.tinh_metrics() của Phúc."""
    if tinh_metrics is not None:
        return tinh_metrics(ten, y_that, y_du_doan)
    bao_cao = classification_report(y_that, y_du_doan, output_dict=True, zero_division=0, mode="strict", scheme=IOB2)
    return {
        "ten_mo_hinh": ten, "che_do_cham": "strict_IOB2",
        "so_thuc_the": int(sum(bao_cao[l]["support"] for l in CAC_LOAI if l in bao_cao)),
        "precision_micro": round(float(precision_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)), 4),
        "recall_micro": round(float(recall_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)), 4),
        "f1_micro": round(float(f1_score(y_that, y_du_doan, zero_division=0, mode="strict", scheme=IOB2)), 4),
        "f1_macro": round(float(f1_score(y_that, y_du_doan, average="macro", zero_division=0, mode="strict", scheme=IOB2)), 4),
        "f1_tung_loai": {l: round(float(bao_cao[l]["f1-score"]), 4) if l in bao_cao else 0.0 for l in CAC_LOAI},
    }


def ghi_json(du_lieu, duong_dan):
    os.makedirs(os.path.dirname(duong_dan) or ".", exist_ok=True)
    with open(duong_dan, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------------------------------------
# 2. Mã hóa câu + căn nhãn với subword (cùng 1 cách cho cả 3 kiến trúc -> so sánh công bằng)
# ----------------------------------------------------------------------------------------------------
class BoMaHoa:
    """Bọc tokenizer: mã hóa TỪNG token rồi ghép, có bộ nhớ đệm (nhanh hơn nhiều với tokenizer chậm của PhoBERT).
    Cách này chạy được cho mọi tokenizer, kể cả PhoBERT (không có word_ids())."""

    def __init__(self, tokenizer, max_length):
        self.tok = tokenizer
        self.max_length = max_length
        self.cache = {}

    def manh(self, tu):
        if tu not in self.cache:
            ids = self.tok.encode(tu, add_special_tokens=False)
            self.cache[tu] = ids if ids else [self.tok.unk_token_id]     # ký tự lạ -> <unk>
        return self.cache[tu]

    def ma_hoa(self, cac_tu, cac_nhan=None, label2id=None):
        """Đầu ra: dict input_ids, attention_mask, labels (nếu có nhãn), vi_tri_dau (vị trí mảnh đầu của từng token,
        -1 nếu token bị cắt vì vượt max_length)."""
        ids, nhan, vi_tri_dau = [self.tok.cls_token_id], [-100], []
        gioi_han = self.max_length - 1                                    # chừa chỗ cho </s> / [SEP]
        for k, tu in enumerate(cac_tu):
            manh = self.manh(tu)
            if len(ids) + len(manh) > gioi_han:                           # hết chỗ: các token còn lại bị cắt
                vi_tri_dau.extend([-1] * (len(cac_tu) - k))
                break
            vi_tri_dau.append(len(ids))
            ids.extend(manh)
            if cac_nhan is not None:
                nhan.extend([label2id[cac_nhan[k]]] + [-100] * (len(manh) - 1))
        ids.append(self.tok.sep_token_id)
        mau = {"input_ids": ids, "attention_mask": [1] * len(ids), "vi_tri_dau": vi_tri_dau}
        if cac_nhan is not None:
            nhan.append(-100)
            mau["labels"] = nhan
        return mau


class TapDuLieu(torch.utils.data.Dataset):
    def __init__(self, cac_mau):
        self.cac_mau = cac_mau

    def __len__(self):
        return len(self.cac_mau)

    def __getitem__(self, i):
        m = self.cac_mau[i]
        return {k: m[k] for k in ("input_ids", "attention_mask", "labels")}


def ma_hoa_tap(bo_ma_hoa, cac_cau, cac_nhan, label2id):
    cac_mau = [bo_ma_hoa.ma_hoa(c, n, label2id) for c, n in zip(cac_cau, cac_nhan)]
    so_cau_bi_cat = sum(1 for m in cac_mau if -1 in m["vi_tri_dau"])
    return cac_mau, so_cau_bi_cat


# ----------------------------------------------------------------------------------------------------
# 3. Dự đoán về lại mức token (để chấm trên ĐỦ nhãn thật, kể cả token bị cắt -> tính là "O")
# ----------------------------------------------------------------------------------------------------
@torch.no_grad()
def du_doan(model, cac_mau, id2label, collator, batch_size=64, tra_xac_suat=False):
    model.eval()
    thiet_bi = next(model.parameters()).device
    ket_qua, xac_suat = [], []
    for i in range(0, len(cac_mau), batch_size):
        lo = cac_mau[i:i + batch_size]
        batch = collator([{"input_ids": m["input_ids"], "attention_mask": m["attention_mask"]} for m in lo])
        batch = {k: v.to(thiet_bi) for k, v in batch.items()}
        with torch.autocast(device_type=thiet_bi.type, dtype=torch.float16, enabled=thiet_bi.type == "cuda"):
            logits = model(**batch).logits
        p = torch.softmax(logits.float(), dim=-1)
        nhan_id = p.argmax(-1).cpu().numpy()
        p_max = p.max(-1).values.cpu().numpy()
        for j, m in enumerate(lo):
            ket_qua.append([id2label[int(nhan_id[j, v])] if v >= 0 else "O" for v in m["vi_tri_dau"]])
            if tra_xac_suat:
                xac_suat.append([float(p_max[j, v]) if v >= 0 else 0.0 for v in m["vi_tri_dau"]])
    return (ket_qua, xac_suat) if tra_xac_suat else ket_qua


def sua_chuoi_bio(cac_nhan):
    """Hậu xử lý nhẹ: I-X đứng sau O hoặc sau loại khác -> đổi thành B-X (để thực thể không bị mất khi chấm strict).
    Đây là cách chuẩn thường dùng khi không có lớp CRF; ghi rõ trong báo cáo."""
    ra, truoc = [], "O"
    for n in cac_nhan:
        if n.startswith("I-") and truoc[2:] != n[2:]:
            n = "B-" + n[2:]
        ra.append(n)
        truoc = n
    return ra


# ----------------------------------------------------------------------------------------------------
# 4. Tham số huấn luyện (tương thích nhiều phiên bản transformers)
# ----------------------------------------------------------------------------------------------------
def tao_training_args(thu_muc_ra, sts, seed, so_epoch, co_danh_gia=True):
    tham_so = dict(
        output_dir=thu_muc_ra, learning_rate=sts["learning_rate"],
        per_device_train_batch_size=sts["batch_size"], per_device_eval_batch_size=64,
        gradient_accumulation_steps=sts.get("gradient_accumulation_steps", 1),
        num_train_epochs=so_epoch, weight_decay=sts.get("weight_decay", 0.0),
        warmup_ratio=sts.get("warmup_ratio", 0.0), lr_scheduler_type="linear",
        save_strategy="epoch" if co_danh_gia else "no", logging_steps=50,
        load_best_model_at_end=co_danh_gia, metric_for_best_model="f1_micro", greater_is_better=True,
        save_total_limit=1, fp16=torch.cuda.is_available() and sts.get("fp16", True),
        seed=seed, data_seed=seed, report_to="none", disable_tqdm=False,
    )
    chu_ky = inspect.signature(TrainingArguments.__init__).parameters
    tham_so["eval_strategy" if "eval_strategy" in chu_ky else "evaluation_strategy"] = "epoch"
    if "warmup_ratio" not in chu_ky:               # transformers >= 5: warmup_ratio bị bỏ, warmup_steps nhận số thực = tỉ lệ
        tham_so["warmup_steps"] = float(tham_so.pop("warmup_ratio"))
    if "save_only_model" in chu_ky:
        tham_so["save_only_model"] = True          # không lưu optimizer -> đỡ tốn ổ đĩa Colab
    return TrainingArguments(**{k: v for k, v in tham_so.items() if k in chu_ky or k in ("eval_strategy", "evaluation_strategy")})


def ham_cham_dev(id2label):
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        pred = np.argmax(logits, axis=-1)
        y_that, y_doan = [], []
        for p_cau, l_cau in zip(pred, labels):
            mask = l_cau != -100
            y_that.append([id2label[int(x)] for x in l_cau[mask]])
            y_doan.append(sua_chuoi_bio([id2label[int(x)] for x in p_cau[mask]]))
        return {"f1_micro": f1_score(y_that, y_doan, mode="strict", scheme=IOB2, zero_division=0),
                "f1_macro": f1_score(y_that, y_doan, average="macro", mode="strict", scheme=IOB2, zero_division=0)}
    return compute_metrics


# ----------------------------------------------------------------------------------------------------
# 5. Một lượt huấn luyện đầy đủ (1 kiến trúc × 1 seed)
# ----------------------------------------------------------------------------------------------------
def huan_luyen(khoa_mo_hinh, seed, sieu_tham_so=None, so_epoch=None, dung_som=None, thu_nhanh=0,
               thu_muc_checkpoint=None, luu_mo_hinh=None, ghi_ket_qua=True, cham_test=True, nguoi_chay=None):
    """Huấn luyện 1 lượt và (mặc định) chấm test, ghi results/{khoa}_seed{seed}.json + results/du_doan/....
    sieu_tham_so: dict ghi đè configs/common.json (dùng khi đã tìm được bộ tốt hơn ở mục 4.3).
    Trả về dict kết quả."""
    cau_hinh = doc_cau_hinh()
    thong_tin = cau_hinh["mo_hinh"][khoa_mo_hinh]
    sts = dict(cau_hinh["sieu_tham_so"])
    sts.update(sieu_tham_so or {})
    so_epoch = so_epoch or sts["so_epoch_toi_da"]
    dung_som = sts["dung_som_sau"] if dung_som is None else dung_som
    muc = "word" if thong_tin["muc_du_lieu"] == "muc_tu" else "syllable"
    label2id, id2label = tao_label2id(cau_hinh)

    set_seed(seed)                                                    # 1) cố định seed TRƯỚC khi tạo model
    du_lieu = tai_du_lieu(muc)
    tok = AutoTokenizer.from_pretrained(thong_tin["ten"])
    bo_ma_hoa = BoMaHoa(tok, sts["max_length"])
    cau_train, nhan_train = du_lieu["train"]
    if thu_nhanh:
        cau_train, nhan_train, so_epoch = cau_train[:thu_nhanh], nhan_train[:thu_nhanh], 1
    mau_train, cat_train = ma_hoa_tap(bo_ma_hoa, cau_train, nhan_train, label2id)
    if thu_nhanh:                                                     # chạy thử: cắt cả dev cho nhanh
        du_lieu["dev"] = (du_lieu["dev"][0][:thu_nhanh], du_lieu["dev"][1][:thu_nhanh])
        du_lieu["test"] = (du_lieu["test"][0][:thu_nhanh], du_lieu["test"][1][:thu_nhanh])
    mau_dev, cat_dev = ma_hoa_tap(bo_ma_hoa, *du_lieu["dev"], label2id)
    print(f"[{khoa_mo_hinh} | seed {seed}] train {len(mau_train)} câu, dev {len(mau_dev)} câu; "
          f"câu bị cắt ở {sts['max_length']} subword: train {cat_train}, dev {cat_dev}")

    model = AutoModelForTokenClassification.from_pretrained(
        thong_tin["ten"], num_labels=len(label2id), id2label=id2label, label2id=label2id, ignore_mismatched_sizes=True)
    collator = DataCollatorForTokenClassification(tok, pad_to_multiple_of=8 if torch.cuda.is_available() else None)
    thu_muc_ra = thu_muc_checkpoint or os.path.join("/tmp", "ckpt_ner", f"{khoa_mo_hinh}_seed{seed}")
    trainer = Trainer(
        model=model, args=tao_training_args(thu_muc_ra, sts, seed, so_epoch),
        train_dataset=TapDuLieu(mau_train), eval_dataset=TapDuLieu(mau_dev),
        data_collator=collator, compute_metrics=ham_cham_dev(id2label),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=dung_som)] if dung_som else [],
    )
    bat_dau = time.time()
    trainer.train()
    thoi_gian = round(time.time() - bat_dau)

    # Epoch tốt nhất và F1 dev tốt nhất (đọc từ lịch sử huấn luyện)
    lich_su = [x for x in trainer.state.log_history if "eval_f1_micro" in x]
    tot_nhat = max(lich_su, key=lambda x: x["eval_f1_micro"]) if lich_su else {}

    # Chấm dev + test trên ĐỦ token (token bị cắt tính là "O")
    ket_qua_dev = cham_diem("dev", du_lieu["dev"][1], [sua_chuoi_bio(x) for x in du_doan(trainer.model, mau_dev, id2label, collator)])
    ket_qua = {"f1_micro_dev": ket_qua_dev["f1_micro"]}
    if cham_test:
        mau_test, cat_test = ma_hoa_tap(bo_ma_hoa, *du_lieu["test"], label2id)
        du_doan_test = [sua_chuoi_bio(x) for x in du_doan(trainer.model, mau_test, id2label, collator)]
        ket_qua = cham_diem(f"{khoa_mo_hinh} seed {seed}", du_lieu["test"][1], du_doan_test)
        ket_qua["so_cau_test_bi_cat"] = cat_test
    ket_qua.update({
        "khoa_mo_hinh": khoa_mo_hinh, "model": thong_tin["ten"], "muc_du_lieu": thong_tin["muc_du_lieu"],
        "seed": seed, "best_epoch": tot_nhat.get("epoch"), "so_epoch_da_chay": round(trainer.state.epoch or 0, 2),
        "f1_micro_dev": ket_qua_dev["f1_micro"], "f1_macro_dev": ket_qua_dev["f1_macro"],
        "lich_su_dev": [{"epoch": x["epoch"], "f1_micro": round(x["eval_f1_micro"], 4), "loss": round(x.get("eval_loss", 0), 4)}
                        for x in lich_su],
        "sieu_tham_so": {k: sts[k] for k in ("learning_rate", "batch_size", "gradient_accumulation_steps", "weight_decay",
                                             "warmup_ratio", "max_length", "fp16") if k in sts}
                        | {"so_epoch_toi_da": so_epoch, "dung_som_sau": dung_som},
        "so_cau_bi_cat": {"train": cat_train, "dev": cat_dev},
        "thoi_gian_train_giay": thoi_gian,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "thu_vien": {"torch": torch.__version__, "transformers": __import__("transformers").__version__},
        "nguoi_chay": nguoi_chay or thong_tin.get("nguoi"),
        "thu_nhanh": bool(thu_nhanh),
    })

    if ghi_ket_qua and cham_test and not thu_nhanh:
        ghi_json(ket_qua, os.path.join(THU_MUC_GOC, "results", f"{khoa_mo_hinh}_seed{seed}.json"))
        ghi_json({"khoa_mo_hinh": khoa_mo_hinh, "seed": seed, "muc_du_lieu": muc, "tap": "test",
                  "du_doan": du_doan_test},
                 os.path.join(THU_MUC_GOC, "results", "du_doan", f"{khoa_mo_hinh}_seed{seed}.json"))
    if luu_mo_hinh:
        trainer.save_model(luu_mo_hinh)
        tok.save_pretrained(luu_mo_hinh)
        ghi_json({k: ket_qua.get(k) for k in ("khoa_mo_hinh", "model", "muc_du_lieu", "seed", "f1_micro", "f1_macro",
                                              "f1_micro_dev")}, os.path.join(luu_mo_hinh, "thong_tin_de26.json"))
    del trainer, model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return ket_qua


# ----------------------------------------------------------------------------------------------------
# 6. Tìm siêu tham số: Grid Search / Random Search trên tập dev (báo cáo mục 4.3)
# ----------------------------------------------------------------------------------------------------
KHONG_GIAN_TIM_KIEM = {                          # cùng 1 không gian + cùng ngân sách cho cả 3 kiến trúc
    "learning_rate": [2e-5, 3e-5, 5e-5],
    "batch_size": [16, 32],
    "warmup_ratio": [0.0, 0.1],
    "weight_decay": [0.0, 0.01],
}
LUOI_NHO = {"learning_rate": [2e-5, 3e-5, 5e-5], "batch_size": [16, 32]}   # Grid Search: 3 × 2 = 6 cấu hình


def tim_sieu_tham_so(khoa_mo_hinh, kieu="random", so_lan=6, so_epoch=3, seed=42, thu_nhanh=0, nguoi_chay=None):
    """Grid Search (ParameterGrid) hoặc Random Search (ParameterSampler) của scikit-learn.
    Mỗi cấu hình: train `so_epoch` epoch trên train, chọn theo F1 micro trên DEV (không đụng test).
    Vì sao không dùng thẳng GridSearchCV? GridSearchCV cần estimator kiểu scikit-learn + k-fold cross-validation;
    với mô hình Transformer, k-fold tốn gấp k lần GPU và bộ dữ liệu đã có sẵn tập dev chuẩn, nên dùng đúng
    cơ chế duyệt lưới/lấy mẫu ngẫu nhiên của scikit-learn trên tập dev (hold-out validation)."""
    from sklearn.model_selection import ParameterGrid, ParameterSampler
    if kieu == "grid":
        cac_cau_hinh = list(ParameterGrid(LUOI_NHO))
    else:
        cac_cau_hinh = list(ParameterSampler(KHONG_GIAN_TIM_KIEM, n_iter=so_lan, random_state=seed))
    bang = []
    for i, ch in enumerate(cac_cau_hinh, 1):
        ch = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in ch.items()}
        print(f"\n===== {kieu} search {i}/{len(cac_cau_hinh)}: {ch} =====")
        ch_day_du = dict(ch, gradient_accumulation_steps=1)
        kq = huan_luyen(khoa_mo_hinh, seed, sieu_tham_so=ch_day_du, so_epoch=so_epoch, dung_som=0,
                        thu_nhanh=thu_nhanh, ghi_ket_qua=False, cham_test=False, nguoi_chay=nguoi_chay)
        bang.append({**ch, "f1_micro_dev": kq["f1_micro_dev"], "f1_macro_dev": kq["f1_macro_dev"],
                     "thoi_gian_giay": kq["thoi_gian_train_giay"]})
        print(f"   -> F1 micro dev = {kq['f1_micro_dev']:.4f}")
    tot = max(bang, key=lambda x: x["f1_micro_dev"])
    ket_qua = {"khoa_mo_hinh": khoa_mo_hinh, "kieu": kieu, "so_cau_hinh": len(bang), "so_epoch_moi_cau_hinh": so_epoch,
               "seed": seed, "khong_gian": LUOI_NHO if kieu == "grid" else KHONG_GIAN_TIM_KIEM,
               "bang": sorted(bang, key=lambda x: -x["f1_micro_dev"]), "tot_nhat": tot, "thu_nhanh": bool(thu_nhanh)}
    if not thu_nhanh:
        ghi_json(ket_qua, os.path.join(THU_MUC_GOC, "results", "tim_kiem", f"{khoa_mo_hinh}_{kieu}.json"))
    return ket_qua


def doc_cau_hinh_tot_nhat(khoa_mo_hinh, in_ra=True):
    """Bộ siêu tham số có F1 dev cao nhất qua CẢ Grid Search và Random Search đã chạy (results/tim_kiem/).
    Chưa chạy tìm kiếm thì trả {} (dùng giá trị mặc định trong configs/common.json)."""
    ung_vien = []
    for kieu in ("grid", "random"):
        p = os.path.join(THU_MUC_GOC, "results", "tim_kiem", f"{khoa_mo_hinh}_{kieu}.json")
        if os.path.exists(p):
            ung_vien.append((json.load(open(p, encoding="utf-8"))["tot_nhat"], kieu))
    if not ung_vien:
        return {}
    tot, kieu = max(ung_vien, key=lambda x: x[0]["f1_micro_dev"])
    if in_ra:
        print(f"Dùng cấu hình tốt nhất từ {kieu} search (F1 dev {tot['f1_micro_dev']:.4f}):",
              {k: tot[k] for k in KHONG_GIAN_TIM_KIEM if k in tot})
    return {k: tot[k] for k in KHONG_GIAN_TIM_KIEM if k in tot} | {"gradient_accumulation_steps": 1}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fine-tune NER PhoNER_COVID19 (đề 26)")
    ap.add_argument("--mo_hinh", required=True, choices=["phobert", "xlmr", "mbert", "phobert_khong_tach_tu"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tim_kiem", choices=["grid", "random"], help="chạy tìm siêu tham số thay vì huấn luyện")
    ap.add_argument("--so_lan", type=int, default=6, help="số cấu hình cho random search")
    ap.add_argument("--dung_cau_hinh_tot_nhat", action="store_true", help="dùng bộ tìm được ở results/tim_kiem/")
    ap.add_argument("--thu_nhanh", type=int, default=0)
    ap.add_argument("--luu_mo_hinh", default=None, help="thư mục lưu mô hình (cho demo)")
    a = ap.parse_args()
    if a.tim_kiem:
        print(json.dumps(tim_sieu_tham_so(a.mo_hinh, a.tim_kiem, a.so_lan, thu_nhanh=a.thu_nhanh)["tot_nhat"], indent=2))
    else:
        sts = doc_cau_hinh_tot_nhat(a.mo_hinh) if a.dung_cau_hinh_tot_nhat else None
        kq = huan_luyen(a.mo_hinh, a.seed, sieu_tham_so=sts, thu_nhanh=a.thu_nhanh, luu_mo_hinh=a.luu_mo_hinh)
        print(json.dumps({k: kq.get(k) for k in ("f1_micro", "f1_macro", "f1_micro_dev", "best_epoch")}, indent=2))
