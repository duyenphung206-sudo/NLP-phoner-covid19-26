"""ner_core.py - Phần xử lý của demo (không phụ thuộc Streamlit, dùng lại được trong notebook).

Luồng (giống hệt lúc huấn luyện để kết quả nhất quán):
  văn bản -> chuẩn hóa Unicode NFC -> tách token (âm tiết + dấu câu) -> [tách từ nếu mô hình mức từ, vd PhoBERT]
          -> mã hóa từng token thành subword -> mô hình -> nhãn BIO ở subword đầu của mỗi token
          -> gộp B-/I- thành thực thể + độ tin cậy (xác suất softmax trung bình)
"""

import json
import os
import re
import unicodedata

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

LOAI = {
    "PATIENT_ID": ("Mã bệnh nhân", "#fde2e4"), "NAME": ("Tên người", "#e2ece9"), "AGE": ("Tuổi", "#fff1c1"),
    "GENDER": ("Giới tính", "#e4dcf5"), "JOB": ("Nghề nghiệp", "#d6eaf8"), "LOCATION": ("Địa điểm", "#d5f5e3"),
    "ORGANIZATION": ("Tổ chức", "#fadbd8"), "SYMPTOM_AND_DISEASE": ("Triệu chứng / bệnh", "#fcf3cf"),
    "TRANSPORTATION": ("Phương tiện", "#d1f2eb"), "DATE": ("Ngày tháng", "#ebdef0"),
}
MAU_CHU = {"PATIENT_ID": "#9b2335", "NAME": "#1e6b52", "AGE": "#8a6d00", "GENDER": "#5b3a9b", "JOB": "#1b4f72",
           "LOCATION": "#196f3d", "ORGANIZATION": "#943126", "SYMPTOM_AND_DISEASE": "#7d6608",
           "TRANSPORTATION": "#0e6655", "DATE": "#6c3483"}
MAU_TACH_TOKEN = re.compile(r"\d+(?:[/\-]\d+)+|\w+(?:\.\w+)+|\w+|[^\w\s]", re.UNICODE)


# ------------------------------------------------------------------ tiền xử lý
def chuan_hoa(van_ban):
    return unicodedata.normalize("NFC", van_ban).strip()


def tach_am_tiet(van_ban):
    """Tách âm tiết và dấu câu (giữ ngày dạng 15/3/2020, mã dạng VN0054, viết tắt TP.HCM thành 1 token)."""
    return MAU_TACH_TOKEN.findall(van_ban)


class BoTachTu:
    """Tách từ tiếng Việt cho mô hình mức từ (PhoBERT). Ưu tiên VnCoreNLP RDRSegmenter (giống dữ liệu huấn luyện),
    không có Java thì dùng underthesea, không có nữa thì để mức âm tiết (độ chính xác sẽ giảm)."""

    def __init__(self, thu_muc_vncorenlp=None):
        self.ten, self.rdr = None, None
        try:
            import py_vncorenlp
            thu_muc = os.path.abspath(thu_muc_vncorenlp or os.path.join(os.path.dirname(__file__), "vncorenlp"))
            os.makedirs(thu_muc, exist_ok=True)
            if not os.path.exists(os.path.join(thu_muc, "VnCoreNLP-1.2.jar")):
                py_vncorenlp.download_model(save_dir=thu_muc)
            cwd = os.getcwd()                                 # py_vncorenlp tự đổi thư mục làm việc -> trả lại
            try:
                self.rdr = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=thu_muc)
            finally:
                os.chdir(cwd)
            self.ten = "VnCoreNLP RDRSegmenter"
        except Exception:
            try:
                from underthesea import word_tokenize  # noqa: F401
                self.ten = "underthesea"
            except Exception:
                self.ten = "không tách từ (thiếu VnCoreNLP và underthesea)"

    def tach(self, van_ban):
        if self.rdr is not None:
            return " ".join(self.rdr.word_segment(van_ban)).split()
        if self.ten == "underthesea":
            from underthesea import word_tokenize
            return word_tokenize(van_ban, format="text").split()
        return tach_am_tiet(van_ban)


# ------------------------------------------------------------------ mô hình
class MoHinhNER:
    def __init__(self, duong_dan, thiet_bi=None):
        self.duong_dan = duong_dan
        self.tok = AutoTokenizer.from_pretrained(duong_dan)
        self.model = AutoModelForTokenClassification.from_pretrained(duong_dan)
        self.thiet_bi = thiet_bi or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.thiet_bi).eval()
        self.id2label = {int(k): v for k, v in self.model.config.id2label.items()}
        self.thong_tin = self._doc_thong_tin(duong_dan)
        if "muc_du_lieu" in self.thong_tin:
            self.muc_tu = self.thong_tin["muc_du_lieu"] == "muc_tu"
        else:                                               # không có file thông tin: PhoBERT luôn cần đầu vào mức từ
            self.muc_tu = "phobert" in type(self.tok).__name__.lower()
        self.max_length = 256
        self._cache = {}

    @staticmethod
    def _doc_thong_tin(duong_dan):
        """thong_tin_de26.json (do train_ner.py ghi): mức dữ liệu, seed, F1 test. Đọc ở thư mục máy hoặc repo Hub."""
        try:
            if os.path.isdir(duong_dan):
                p = os.path.join(duong_dan, "thong_tin_de26.json")
            else:
                from huggingface_hub import hf_hub_download
                p = hf_hub_download(duong_dan, "thong_tin_de26.json")
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}

    def _manh(self, tu):
        if tu not in self._cache:
            ids = self.tok.encode(tu, add_special_tokens=False)
            self._cache[tu] = ids or [self.tok.unk_token_id]
        return self._cache[tu]

    @torch.no_grad()
    def gan_nhan(self, cac_token):
        """Gán nhãn cho 1 đoạn token. Đầu ra: (nhan, xac_suat, manh_subword) cùng độ dài với cac_token."""
        nhan, xs, manh_ds = [], [], []
        dau = 0
        while dau < len(cac_token):                         # chia cửa sổ nếu dài hơn max_length subword
            ids, vi_tri, k = [self.tok.cls_token_id], [], dau
            while k < len(cac_token) and len(ids) + len(self._manh(cac_token[k])) < self.max_length - 1:
                vi_tri.append(len(ids))
                ids += self._manh(cac_token[k])
                k += 1
            if k == dau:                                     # 1 token quá dài (hiếm) -> bỏ qua
                vi_tri, k = [], dau + 1
            ids.append(self.tok.sep_token_id)
            dau_vao = torch.tensor([ids], device=self.thiet_bi)
            p = torch.softmax(self.model(input_ids=dau_vao, attention_mask=torch.ones_like(dau_vao)).logits[0], -1)
            for j, v in enumerate(vi_tri):
                nhan.append(self.id2label[int(p[v].argmax())])
                xs.append(float(p[v].max()))
                manh_ds.append(self.tok.convert_ids_to_tokens(self._manh(cac_token[dau + j])))
            if not vi_tri:
                nhan.append("O"); xs.append(0.0); manh_ds.append([])
            dau = k
        return nhan, xs, manh_ds


def sua_bio(nhan):
    ra, truoc = [], "O"
    for n in nhan:
        if n.startswith("I-") and truoc[2:] != n[2:]:
            n = "B-" + n[2:]
        ra.append(n)
        truoc = n
    return ra


def gop_thuc_the(cac_token, nhan, xac_suat):
    """Gộp nhãn BIO thành thực thể: list dict {van_ban, loai, dau, cuoi, do_tin_cay}."""
    ds, i = [], 0
    while i < len(nhan):
        if nhan[i].startswith("B-"):
            loai, j = nhan[i][2:], i + 1
            while j < len(nhan) and nhan[j] == "I-" + loai:
                j += 1
            ds.append({"van_ban": " ".join(t.replace("_", " ") for t in cac_token[i:j]), "loai": loai,
                       "dau": i, "cuoi": j - 1, "do_tin_cay": sum(xac_suat[i:j]) / (j - i)})
            i = j
        else:
            i += 1
    return ds


def nhan_dang(van_ban, mo_hinh, bo_tach_tu=None):
    """Toàn bộ pipeline cho 1 đoạn văn bản. Đầu ra dict có token, nhãn, thực thể và các bước trung gian."""
    goc = chuan_hoa(van_ban)
    if mo_hinh.muc_tu and bo_tach_tu is not None:
        cac_token = bo_tach_tu.tach(goc)
        cach_tach = bo_tach_tu.ten
    else:
        cac_token = tach_am_tiet(goc)
        cach_tach = "âm tiết (không cần tách từ)"
    nhan, xs, manh = mo_hinh.gan_nhan(cac_token) if cac_token else ([], [], [])
    nhan = sua_bio(nhan)
    return {"van_ban_chuan_hoa": goc, "cach_tach": cach_tach, "token": cac_token, "nhan": nhan,
            "xac_suat": xs, "subword": manh, "thuc_the": gop_thuc_the(cac_token, nhan, xs)}


def html_to_mau(ket_qua, nguong=0.0):
    """HTML tô màu thực thể (bỏ thực thể có độ tin cậy dưới ngưỡng)."""
    tt_theo_dau = {t["dau"]: t for t in ket_qua["thuc_the"] if t["do_tin_cay"] >= nguong}
    phan, i, tok = [], 0, ket_qua["token"]
    while i < len(tok):
        if i in tt_theo_dau:
            t = tt_theo_dau[i]
            nen, chu = LOAI[t["loai"]][1], MAU_CHU[t["loai"]]
            phan.append(f'<span class="tt" style="background:{nen};border-color:{chu}">'
                        f'{t["van_ban"]}<span class="nhan" style="background:{chu}">{LOAI[t["loai"]][0]}</span></span>')
            i = t["cuoi"] + 1
        else:
            phan.append(tok[i].replace("_", " "))
            i += 1
    html = " ".join(phan)
    html = re.sub(r" ([,.;:!?)\]])", r"\1", html)
    return re.sub(r"([(\[]) ", r"\1", html)
