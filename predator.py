import cv2
import numpy as np
import time
import subprocess
from pathlib import Path

INPUT = "input.mp4"
SOUND_EFFECT = "vision_effect.mp3"

TEMP_VIDEO = "thermal_predator_no_audio.mp4"
OUTPUT = "thermal_predator.mp4"

BAR_WIDTH = 90
FPS_FALLBACK = 30
PROGRESS_EVERY_FRAMES = 100

cap = cv2.VideoCapture(INPUT)

if not cap.isOpened():
    raise RuntimeError(f"No se pudo abrir el video: {INPUT}")

fps = cap.get(cv2.CAP_PROP_FPS) or FPS_FALLBACK
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

out_w = w + BAR_WIDTH

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(TEMP_VIDEO, fourcc, fps, (out_w, h))

if not writer.isOpened():
    raise RuntimeError("No se pudo crear el video temporal")

clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
vignette_cache = None


def thermal_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(gray, (0, 0), 7)
    hot = cv2.addWeighted(gray, 1.8, blur, -0.5, 0)

    hot = cv2.normalize(hot, None, 0, 255, cv2.NORM_MINMAX)
    hot = hot.astype(np.uint8)

    colored = cv2.applyColorMap(hot, cv2.COLORMAP_JET)

    mask_cold = hot < 80
    colored[mask_cold] = (colored[mask_cold] * 0.35).astype(np.uint8)

    return colored


def fake_scanner_bar(frame_idx):
    bar = np.zeros((h, BAR_WIDTH, 3), dtype=np.uint8)
    x = BAR_WIDTH // 2

    cv2.line(bar, (x, 0), (x, h), (0, 180, 255), 2)

    for i in range(40):
        y = int((i / 40) * h)
        wave = np.sin(frame_idx * 0.12 + i * 0.7)
        length = int(10 + abs(wave) * 32)
        color = (0, int(100 + abs(wave) * 155), 255)

        cv2.line(
            bar,
            (x - length, y),
            (x + length, y),
            color,
            1
        )

    sweep_y = int((frame_idx * 6) % h)
    cv2.line(bar, (0, sweep_y), (BAR_WIDTH, sweep_y), (0, 255, 255), 2)

    bar[::5, :] = (0, 35, 60)

    return bar


print("Procesando video...")

frame_idx = 0
start_time = time.time()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    thermal = thermal_frame(frame)
    bar = fake_scanner_bar(frame_idx)

    combined = np.hstack([bar, thermal])

    combined[::4, :, :] = (combined[::4, :, :] * 0.75).astype(np.uint8)

    if vignette_cache is None:
        vignette_cache = np.linspace(0.75, 1.0, combined.shape[1])
        vignette_cache = vignette_cache[np.newaxis, :, np.newaxis]

    combined = (combined * vignette_cache).astype(np.uint8)

    writer.write(combined)
    frame_idx += 1

    if frame_idx % PROGRESS_EVERY_FRAMES == 0 or frame_idx == total_frames:
        elapsed = time.time() - start_time
        current_fps = frame_idx / elapsed if elapsed > 0 else 0
        percent = (frame_idx / total_frames) * 100 if total_frames > 0 else 0

        print(
            f"{frame_idx}/{total_frames} frames | "
            f"{percent:.1f}% | "
            f"{current_fps:.2f} fps",
            flush=True
        )

cap.release()
writer.release()

if not Path(SOUND_EFFECT).exists():
    Path(TEMP_VIDEO).replace(OUTPUT)
    print(f"No existe {SOUND_EFFECT}. Video generado sin audio: {OUTPUT}")
else:
    print("Añadiendo efecto de sonido...")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", TEMP_VIDEO,
        "-stream_loop", "-1",
        "-i", SOUND_EFFECT,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT
    ]

    subprocess.run(cmd, check=True)

    Path(TEMP_VIDEO).unlink(missing_ok=True)

    print("Listo:", OUTPUT)