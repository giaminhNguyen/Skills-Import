r"""Quét thư mục .txt, tạo audio cho file CHƯA có, sau mỗi file quét lại từ đầu.

Dừng khi một lượt quét đầy đủ không còn file nào thiếu audio.
Model chỉ nạp một lần cho cả phiên.

    .venv\Scripts\python.exe queue_runner.py <thu_muc> --voice "Thái Sơn"
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf


def split_jobs(text: str, max_chars: int) -> list:
    """Cắt text thành các đoạn <= max_chars, ưu tiên ranh giới đoạn văn rồi câu."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    jobs, cur = [], ""
    for para in paras:
        pieces = [para] if len(para) <= max_chars else [
            s for s in re.split(r"(?<=[.!?…])\s+", para) if s
        ]
        for piece in pieces:
            if cur and len(cur) + len(piece) + 2 > max_chars:
                jobs.append(cur)
                cur = piece
            else:
                cur = f"{cur}\n\n{piece}".strip() if cur else piece
    if cur:
        jobs.append(cur)
    return jobs


def read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-16", "cp1258"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def all_texts(src_dir: Path, recursive: bool) -> list:
    pattern = "**/*.txt" if recursive else "*.txt"
    return sorted(src_dir.glob(pattern), key=lambda p: str(p).lower())


def wav_for(txt: Path, src_dir: Path, out_dir: Path) -> Path:
    """.wav trùng tên; khi có --out thì giữ nguyên cấu trúc thư mục con."""
    if out_dir == src_dir:
        return txt.with_suffix(".wav")
    return out_dir / txt.relative_to(src_dir).with_suffix(".wav")


def find_missing(src_dir: Path, out_dir: Path, recursive: bool):
    """File .txt ĐẦU TIÊN (theo thứ tự tên) chưa có .wav trùng tên. None nếu đủ cả."""
    for txt in all_texts(src_dir, recursive):
        if not wav_for(txt, src_dir, out_dir).exists():
            return txt
    return None


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Hàng chờ TTS: quét lại từ đầu sau mỗi file")
    ap.add_argument("src", help="thư mục chứa các file .txt")
    ap.add_argument("-o", "--out", default=None, help="thư mục lưu .wav (mặc định: cùng thư mục .txt)")
    ap.add_argument("-v", "--voice", required=True, help="tên giọng preset")
    ap.add_argument("--precision", default="fp32", choices=["fp32", "int8"])
    ap.add_argument("--threads", type=int, default=6)
    ap.add_argument("--max-chars", type=int, default=700)
    ap.add_argument("--gap", type=float, default=0.35)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("-r", "--recursive", action="store_true", help="quét cả thư mục con")
    ap.add_argument("--once", action="store_true",
                    help="tạo đúng MỘT file rồi thoát (thoát mã 10 nếu không còn gì thiếu); "
                         "dùng trong vòng lặp ngoài để mỗi file chạy trong tiến trình mới")
    args = ap.parse_args()

    src_dir = Path(args.src)
    if not src_dir.is_dir():
        sys.exit(f"Không phải thư mục: {src_dir}")
    out_dir = Path(args.out) if args.out else src_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    total_txt = len(all_texts(src_dir, args.recursive))
    if not total_txt:
        sys.exit(f"Không có file .txt nào trong {src_dir}")

    if find_missing(src_dir, out_dir, args.recursive) is None:
        print(f"Tất cả {total_txt} file .txt đều đã có audio — không có gì để làm.")
        sys.exit(10 if args.once else 0)

    print(f"Nạp model (v3turbo / {args.precision} / {args.threads} luồng)…", flush=True)
    from vieneu import Vieneu

    tts = Vieneu(mode="v3turbo", precision=args.precision, threads=args.threads)
    sr = tts.sample_rate
    print(f"Model sẵn sàng. Giọng: {args.voice}\n", flush=True)

    made, t_all = 0, time.time()
    while True:
        txt = find_missing(src_dir, out_dir, args.recursive)
        if txt is None:
            break

        dest = wav_for(txt, src_dir, out_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        jobs = split_jobs(read_text(txt), args.max_chars)
        if not jobs:
            print(f"⚠️  {txt.name} rỗng — bỏ qua, nhưng sẽ bị quét lại. Dừng để tránh lặp vô hạn.")
            break

        print(f"▶️  {txt.name} — {len(jobs)} đoạn", flush=True)
        t0, frames = time.time(), 0
        silence = np.zeros(int(sr * args.gap), dtype=np.float32) if args.gap > 0 else None
        # Ghi thẳng từng đoạn ra đĩa thay vì gom cả file trong RAM: audio 25 phút
        # tốn ~550 MB nếu gom, còn cách này thì RAM phẳng bất kể file dài bao nhiêu.
        # Ghi vào .part rồi mới đổi tên -> dừng giữa chừng không để lại .wav cụt
        # bị lượt quét sau tưởng nhầm là đã xong.
        tmp = dest.with_suffix(".wav.part")
        # format phải khai báo tường minh: đuôi .part khiến soundfile không tự đoán được.
        with sf.SoundFile(str(tmp), "w", samplerate=sr, channels=1,
                          format="WAV", subtype="PCM_16") as fh:
            for j, chunk in enumerate(jobs, 1):
                wav = np.asarray(tts.infer(chunk, voice=args.voice,
                                           temperature=args.temperature), dtype=np.float32)
                fh.write(wav)
                frames += len(wav)
                if j < len(jobs) and silence is not None:
                    fh.write(silence)
                    frames += len(silence)
                print(f"    đoạn {j}/{len(jobs)} — {time.time() - t0:.0f}s", flush=True)
        tmp.replace(dest)

        made += 1
        print(f"✅  {dest.name} — audio {frames / sr / 60:.1f} phút, "
              f"tạo mất {(time.time() - t0) / 60:.1f} phút\n", flush=True)

        if args.once:
            break

    print(f"🎉 Xong. Tạo mới {made} file, tổng {(time.time() - t_all) / 60:.1f} phút. "
          f"Cả {total_txt} file .txt trong {src_dir} đều đã có audio.")


if __name__ == "__main__":
    main()
