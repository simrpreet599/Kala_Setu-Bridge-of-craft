"""AI Image Enhancer (classical computer-vision pipeline, runs fully offline).

Steps: EXIF fix -> GrabCut background removal (border-seeded) -> LAB CLAHE lighting
correction + moderated white balance -> crop to subject -> square e-commerce canvas.

Honest scope: GrabCut works best on a single object against a reasonably plain
background. Every result carries quality metrics and warnings so the artisan can retake
the photo. A deep-learning segmenter (e.g. U2-Net/rembg) can be swapped into
`remove_background` later without changing the rest of the app.
"""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image, ImageOps

CANVAS = 1600
BG_COLORS = {"white": (255, 255, 255), "ivory": (250, 246, 238)}


def load_image(path: str, max_side: int = 2000) -> np.ndarray:
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def sharpness(bgr: np.ndarray) -> float:
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (640, max(1, int(640 * g.shape[0] / g.shape[1]))))
    return float(cv2.Laplacian(g, cv2.CV_64F).var())


def brightness(bgr: np.ndarray, mask: np.ndarray | None = None) -> float:
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if mask is not None and (mask > 127).sum() > 0:
        return float(g[mask > 127].mean())
    return float(g.mean())


def remove_background(bgr: np.ndarray) -> tuple[np.ndarray, float]:
    """Return (soft alpha mask uint8 0..255, foreground_ratio)."""
    h, w = bgr.shape[:2]
    scale = 640 / max(h, w)
    small = cv2.resize(bgr, (int(w * scale), int(h * scale))) if scale < 1 else bgr.copy()
    sh, sw = small.shape[:2]

    mask = np.full((sh, sw), cv2.GC_PR_BGD, np.uint8)
    b = max(2, int(0.05 * min(sh, sw)))
    mask[:b, :] = cv2.GC_BGD
    mask[-b:, :] = cv2.GC_BGD
    mask[:, :b] = cv2.GC_BGD
    mask[:, -b:] = cv2.GC_BGD
    border = np.concatenate([small[:b].reshape(-1, 3), small[-b:].reshape(-1, 3),
                             small[:, :b].reshape(-1, 3), small[:, -b:].reshape(-1, 3)])
    bg_mean = np.median(border, axis=0)
    dist = np.linalg.norm(small.astype(np.float32) - bg_mean.astype(np.float32), axis=2)
    thr = max(30.0, float(np.percentile(dist[:b * 2], 95)) + 10)
    mask[(dist > thr) & (mask != cv2.GC_BGD)] = cv2.GC_PR_FGD
    centre = mask[int(sh * .3):int(sh * .7), int(sw * .3):int(sw * .7)]
    centre[centre == cv2.GC_PR_BGD] = cv2.GC_PR_FGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(small, mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return np.full((h, w), 255, np.uint8), 1.0
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == keep, 255, 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(fg)
    cv2.drawContours(filled, cnts, -1, 255, cv2.FILLED)
    ratio = float(filled.mean() / 255)
    alpha = cv2.GaussianBlur(filled, (0, 0), 1.6)
    alpha = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_LINEAR)
    return alpha, ratio


def correct_lighting(bgr: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    out = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR).astype(np.float32)
    sel = (mask > 127) if mask is not None and (mask > 127).sum() > 100 else np.ones(out.shape[:2], bool)
    means = out[sel].mean(axis=0)
    gains = np.clip(means.mean() / np.maximum(means, 1), 0.92, 1.08)  # moderated: keeps real dye colours
    out = np.clip(out * gains, 0, 255)
    cur = float(cv2.cvtColor(out.astype(np.uint8), cv2.COLOR_BGR2GRAY)[sel].mean())
    gamma = float(np.clip(np.log(135 / 255) / np.log(max(cur, 1) / 255), 0.6, 1.6))
    out = np.clip(255 * np.power(out / 255, gamma), 0, 255).astype(np.uint8)
    blur = cv2.GaussianBlur(out, (0, 0), 1.2)
    return cv2.addWeighted(out, 1.35, blur, -0.35, 0)


def to_square_canvas(bgr: np.ndarray, alpha: np.ndarray, bg: str, remove_bg: bool) -> np.ndarray:
    color = np.array(BG_COLORS.get(bg, BG_COLORS["white"])[::-1], np.float32)
    if remove_bg:
        ys, xs = np.where(alpha > 127)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        pad = int(0.08 * max(y1 - y0, x1 - x0))
        y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
        y1, x1 = min(bgr.shape[0], y1 + pad), min(bgr.shape[1], x1 + pad)
        crop, a = bgr[y0:y1, x0:x1], alpha[y0:y1, x0:x1, None].astype(np.float32) / 255
        comp = crop.astype(np.float32) * a + color * (1 - a)
    else:
        comp = bgr.astype(np.float32)
    comp = np.clip(comp, 0, 255).astype(np.uint8)
    h, w = comp.shape[:2]
    s = CANVAS / max(h, w)
    comp = cv2.resize(comp, (max(1, int(w * s)), max(1, int(h * s))),
                      interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    canvas = np.empty((CANVAS, CANVAS, 3), np.uint8)
    canvas[:] = color.astype(np.uint8)
    h, w = comp.shape[:2]
    oy, ox = (CANVAS - h) // 2, (CANVAS - w) // 2
    canvas[oy:oy + h, ox:ox + w] = comp
    return canvas


def enhance(src_path: str, dst_path: str, bg: str = "white") -> dict:
    bgr = load_image(src_path)
    before = {"brightness": round(brightness(bgr), 1), "sharpness": round(sharpness(bgr), 1)}
    alpha, ratio = remove_background(bgr)
    warnings: list[str] = []
    do_remove = 0.03 <= ratio <= 0.93
    if not do_remove:
        warnings.append("Background could not be separated reliably; kept the original background. "
                        "Try a plain cloth or wall behind the product.")
    fixed = correct_lighting(bgr, alpha if do_remove else None)
    out = to_square_canvas(fixed, alpha, bg, do_remove)
    cv2.imwrite(dst_path, out, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if before["sharpness"] < 60:
        warnings.append("Photo looks blurry. Hold the phone steady and retake for better buyer trust.")
    if before["brightness"] < 70:
        warnings.append("Photo was very dark; lighting was boosted but retaking near a window is better.")
    after = {"brightness": round(brightness(out), 1), "sharpness": round(sharpness(out), 1)}
    return {"before": before, "after": after, "foreground_ratio": round(ratio, 3),
            "background_removed": do_remove, "warnings": warnings, "size": [CANVAS, CANVAS]}
