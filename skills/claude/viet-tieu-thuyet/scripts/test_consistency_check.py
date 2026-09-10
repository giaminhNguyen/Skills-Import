#!/usr/bin/env python3
"""Self-check cho consistency_check.py — chạy: python scripts/test_consistency_check.py

Không cần framework. Dựng một dự án truyện giả trong thư mục tạm rồi khẳng định
script bắt đúng cái cần bắt và im lặng với cái không liên quan.
"""
import json
import os
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "consistency_check.py")

STATE = {
    "du_an": "Test",
    "chuong_hien_tai": 3,
    "fact_ledger": {"Số tiền nợ": "200 triệu đồng", "Tuổi nhân vật An": "17 tuổi"},
    "guard_rails": ["An không được biết bí mật của Bình trước chương 15"],
    "ve_so_dang_mo": [{"cai_o_chuong": 1, "noi_dung": "chiếc vòng tay",
                       "du_kien_tra_o_chuong": 9}],
}
CHUONG = {
    "chuong-01.md": "# Chương 1\nAn đánh rơi chiếc vòng tay. Cô nợ 200 triệu đồng, năm nay 17 tuổi.\n",
    "chuong-02.md": "# Chương 2\nKhoản nợ 500 triệu đồng khiến An mất ngủ.\n",
    "chuong-03.md": "# Chương 3\nAn mua ổ bánh mì 25 nghìn đồng rồi đi học.\n",
}


def run(d):
    r = subprocess.run([sys.executable, CHECKER, "--dir", d, "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)["chi_tiet"]


def main():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "project-state.json"), "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False)
        for name, text in CHUONG.items():
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
        issues = run(d)

    facts = [i for i in issues if i["loai"] == "FACT_LEDGER"]
    ch = {i["chuong"] for i in facts}
    assert "chuong-02.md" in ch, f"bỏ sót mâu thuẫn 200 vs 500 triệu: {facts}"
    assert "chuong-03.md" not in ch, f"báo nhầm ổ bánh mì 25 nghìn đồng: {facts}"
    assert not [i for i in facts if i["chuong"] == "chuong-01.md"], "báo nhầm chương khớp ledger"
    assert not [i for i in issues if i["loai"] == "VE_SO"], "vé số hạn chương 9 chưa tới hạn"
    print("✅ consistency_check: 4/4 khẳng định đạt")


if __name__ == "__main__":
    main()
