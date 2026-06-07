import cv2
import numpy as np

INPUT = "input.mp4"
OUTPUT = "thermal_predator.mp4"

BAR_WIDTH = 90
FPS_FALLBACK = 30

cap = cv2.VideoCapture(INPUT)

fps = cap.get(cv2.CAP_PROP_FPS) or FPS_FALLBACK
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out_w = w + BAR_WIDTH

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(OUTPUT, fourcc, fps, (out_w, h))

clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))

def thermal_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(gray, (0, 0), 7)
    hot = cv2.addWeighted(gray, 1.8, blur, -0.5, 0)

    hot = cv2.normalize(hot, None, 0, 255, cv2.NORM_MINMAX)
    hot = hot.astype(np.uint8)

    colored = cv2.applyColorMap(hot, cv2.COLORMAP_JET)

    # Oscurecer zonas frías
    mask_cold = hot < 80
    colored[mask_cold] = (colored[mask_cold] * 0.35).astype(np.uint8)

    return colored

def fake_scanner_bar(frame_idx):
    bar = np.zeros((h, BAR_WIDTH, 3), dtype=np.uint8)

    x = BAR_WIDTH // 2

    # Línea vertical principal
    cv2.line(bar, (x, 0), (x, h), (0, 180, 255), 2)

    # Pulsos falsos animados
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

    # Barrido vertical
    sweep_y = int((frame_idx * 6) % h)
    cv2.line(bar, (0, sweep_y), (BAR_WIDTH, sweep_y), (0, 255, 255), 2)

    # Scanlines
    bar[::5, :] = (0, 35, 60)

    return bar

frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    thermal = thermal_frame(frame)
    bar = fake_scanner_bar(frame_idx)

    combined = np.hstack([bar, thermal])

    # Scanlines globales
    combined[::4, :, :] = (combined[::4, :, :] * 0.75).astype(np.uint8)

    # Viñeta leve
    vignette = np.linspace(0.75, 1.0, combined.shape[1])
    combined = (combined * vignette[np.newaxis, :, np.newaxis]).astype(np.uint8)

    writer.write(combined)
    frame_idx += 1

cap.release()
writer.release()

print("Listo:", OUTPUT)