import os, csv, subprocess, sys
from dataclasses import dataclass
from typing import List, Tuple

import cv2
import face_recognition
from tqdm import tqdm
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

# ====== 路径 ======
VIDEO_PATH = r"D:\heky\SWproject\vCut\video.mp4" 
REF_IMG_PATH = r"D:\heky\SWproject\vCut\he.png" 
OUT_DIR = r"D:\heky\SWproject\vCut\he_out"

# ====== 可调参数 ======
SCENE_THRESHOLD = 27.0
FACE_TOLERANCE = 0.50
FRAME_POS_IN_SCENE = 0.50
DOWNSCALE = 0.60
PAD_SEC = 1.0


@dataclass
class Hit:
    idx: int
    s: float
    e: float
    dist: float
    frame: str


def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "frames"), exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "clips"), exist_ok=True)


def detect_scenes(video_path: str, threshold: float) -> List[Tuple[float, float]]:
    video = open_video(video_path)
    sm = SceneManager()
    sm.add_detector(ContentDetector(threshold=threshold))
    sm.detect_scenes(video)
    out = []
    for s_tc, e_tc in sm.get_scene_list():
        out.append((s_tc.get_seconds(), e_tc.get_seconds()))
    return out


def load_ref_encoding(ref_path: str):
    img = face_recognition.load_image_file(ref_path)
    encs = face_recognition.face_encodings(img)
    if not encs:
        raise RuntimeError("参考照片检测不到人脸，请换清晰正脸照片。")
    return encs[0]


def extract_frame(video_path: str, t: float, out_path: str) -> bool:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return False
    if DOWNSCALE != 1.0:
        frame = cv2.resize(frame, None, fx=DOWNSCALE, fy=DOWNSCALE, interpolation=cv2.INTER_AREA)
    return cv2.imwrite(out_path, frame)


def match_frame(frame_path: str, ref_enc):
    img = face_recognition.load_image_file(frame_path)
    encs = face_recognition.face_encodings(img)
    if not encs:
        return False, 999.0
    dists = face_recognition.face_distance(encs, ref_enc)
    best = float(dists.min())
    return best <= FACE_TOLERANCE, best


def ffmpeg_cut(video_path: str, s: float, e: float, out_path: str):
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "warning",
        "-i", video_path,
        "-ss", f"{s:.3f}",
        "-to", f"{e:.3f}",
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        out_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ensure_dirs()

    print("\n[1/5] 加载参考人脸...")
    ref_enc = load_ref_encoding(REF_IMG_PATH)
    print("✔ 参考脸加载完成\n")

    print("[2/5] 进行镜头切分...")
    scenes = detect_scenes(VIDEO_PATH, SCENE_THRESHOLD)
    total = len(scenes)
    print(f"✔ 共检测到 {total} 个镜头\n")

    hits: List[Hit] = []
    frames_dir = os.path.join(OUT_DIR, "frames")

    print("[3/5] 人脸扫描中...")
    for i, (s, e) in enumerate(tqdm(scenes, desc="扫描镜头", ncols=90), start=1):
        if e <= s:
            continue

        t = s + (e - s) * FRAME_POS_IN_SCENE
        frame_path = os.path.join(frames_dir, f"scene_{i:05d}.jpg")

        if not extract_frame(VIDEO_PATH, t, frame_path):
            continue

        ok, dist = match_frame(frame_path, ref_enc)

        if ok:
            hits.append(Hit(i, s, e, dist, frame_path))
            tqdm.write(f"🎯 HIT scene={i:05d}  {s:.1f}-{e:.1f}s  dist={dist:.4f}")

    print(f"\n✔ 命中镜头数：{len(hits)}\n")

    csv_path = os.path.join(OUT_DIR, "hits.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scene","start","end","distance"])
        for h in hits:
            w.writerow([h.idx, f"{h.s:.3f}", f"{h.e:.3f}", f"{h.dist:.6f}"])

    print("[4/5] 正在裁剪片段...")
    clips_dir = os.path.join(OUT_DIR, "clips")

    for h in tqdm(hits, desc="裁剪中", ncols=90):
        ps = max(0.0, h.s - PAD_SEC)
        pe = h.e + PAD_SEC
        out_clip = os.path.join(clips_dir, f"he_scene_{h.idx:05d}.mp4")
        ffmpeg_cut(VIDEO_PATH, ps, pe, out_clip)

    print("\n[5/5] 完成 🎉")
    print(f"输出目录: {clips_dir}")


if __name__ == "__main__":
    main()