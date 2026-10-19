"""nap_seqeval.py - Bảo đảm dùng được thư viện seqeval trên mọi máy (Colab, Kaggle, Windows, macOS).

Vì sao cần file này?
    seqeval 1.2.2 (bản mới nhất, 2020) chỉ phát hành dạng mã nguồn đóng gói kiểu cũ (setup.py), nên
    "pip install seqeval" bị lỗi "metadata-generation-failed" trên Python mới (Colab dùng Python 3.12+).
    seqeval viết bằng Python thuần, nên chỉ cần TẢI MÃ NGUỒN về rồi thêm vào sys.path là dùng được.

Cách dùng (đặt TRƯỚC mọi lệnh "from seqeval ..."):
    from nap_seqeval import dam_bao_seqeval
    dam_bao_seqeval()
"""

import os
import sys
import tarfile
import tempfile
import urllib.request

PHIEN_BAN = "1.2.2"
URL_PYPI = f"https://files.pythonhosted.org/packages/source/s/seqeval/seqeval-{PHIEN_BAN}.tar.gz"


def dam_bao_seqeval(thu_muc_cache=None):
    """Nạp seqeval. Nếu máy chưa có thì tải mã nguồn từ PyPI (không cần pip, không cần git).
    Đầu ra: đường dẫn tới thư mục chứa seqeval đang dùng."""
    try:
        import seqeval  # noqa: F401  (đã cài sẵn thì dùng luôn)
        return os.path.dirname(os.path.dirname(seqeval.__file__))
    except ModuleNotFoundError:
        pass

    thu_muc_cache = thu_muc_cache or os.path.join(tempfile.gettempdir(), "seqeval_src")
    thu_muc_ma_nguon = os.path.join(thu_muc_cache, f"seqeval-{PHIEN_BAN}")
    if not os.path.exists(os.path.join(thu_muc_ma_nguon, "seqeval", "__init__.py")):
        os.makedirs(thu_muc_cache, exist_ok=True)
        file_nen = os.path.join(thu_muc_cache, f"seqeval-{PHIEN_BAN}.tar.gz")
        urllib.request.urlretrieve(URL_PYPI, file_nen)
        with tarfile.open(file_nen, "r:gz") as tar:
            try:
                tar.extractall(thu_muc_cache, filter="data")   # Python mới: chỉ giải nén file thường, an toàn
            except TypeError:
                tar.extractall(thu_muc_cache)

    if thu_muc_ma_nguon not in sys.path:
        sys.path.insert(0, thu_muc_ma_nguon)
    import seqeval  # noqa: F401,E402
    return thu_muc_ma_nguon


if __name__ == "__main__":
    print("seqeval nạp từ:", dam_bao_seqeval())
    from seqeval.metrics import f1_score
    from seqeval.scheme import IOB2
    print("Thử chấm 1 câu:", f1_score([["B-AGE", "O"]], [["B-AGE", "O"]], mode="strict", scheme=IOB2))
