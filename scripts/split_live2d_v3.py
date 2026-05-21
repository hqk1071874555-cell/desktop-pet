"""
Live2D 自动拆分脚本 v3 (精细版)
新增：Haar级联检测眼睛/嘴巴 + 轮廓分割头发/四肢 + Live2D标准图层结构
"""
import os
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from psd_tools import PSDImage

# ========== 配置 ==========
INPUT_PATH = "E:/桌面/galgame/desktop-pet/assets/character_original.jpg"
OUTPUT_DIR = Path("E:/桌面/galgame/desktop-pet/assets/live2d_layers_v3")
PSD_OUTPUT = OUTPUT_DIR / "character_live2d.psd"
PNG_DIR = OUTPUT_DIR / "png_layers"

# HSV 颜色范围（与 v2 一致）
SKIN_LOWER = np.array([0, 15, 60])
SKIN_UPPER = np.array([25, 200, 255])

RED_LOWER1 = np.array([0, 60, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([160, 60, 50])
RED_UPPER2 = np.array([180, 255, 255])

WHITE_LOWER = np.array([0, 0, 190])
WHITE_UPPER = np.array([180, 25, 255])

DARK_LOWER = np.array([0, 0, 0])
DARK_UPPER = np.array([180, 255, 80])

PINK_LOWER = np.array([140, 30, 100])
PINK_UPPER = np.array([175, 255, 255])


def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)


def load_image(path):
    """用 PIL 读图，转 OpenCV BGR"""
    pil = Image.open(path).convert("RGB")
    bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return pil, bgr


def grabcut_remove_bg(bgr):
    """GrabCut 去背景 → 返回 RGBA + mask"""
    print("🎨 去除背景...")
    h, w = bgr.shape[:2]
    margin = int(min(w, h) * 0.03)
    rect = (margin, margin, w - 2 * margin, h - 2 * margin)

    mask = np.zeros((h, w), np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)

    fg = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgba = Image.fromarray(np.dstack([rgb, fg]), 'RGBA')
    rgba.save(PNG_DIR / "00_transparent.png")
    print(f"  ✓ 前景像素: {fg.sum()}")
    return rgba, fg


def detect_face_regions(bgr):
    """
    Haar级联检测：人脸、眼睛、嘴巴
    返回坐标字典
    """
    print("\n👁️ 检测面部特征...")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    results = {}

    # 人脸检测
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
    )
    faces = face_cascade.detectMultiScale(gray, 1.05, 3)

    if len(faces) == 0:
        print("  ⚠️ 未检测到标准人脸（可能是二次元角色）")
        print("  使用边缘检测 + 轮廓分析替代方案...")
        return detect_anime_face(bgr)
    
    x, y, w, h = faces[0]
    results['face'] = (x, y, w, h)
    face_roi = gray[y:y+h, x:x+w]
    face_color = bgr[y:y+h, x:x+w]
    print(f"  ✓ 人脸: x={x} y={y} w={w} h={h}")

    # 眼睛检测
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml'
    )
    eyes = eye_cascade.detectMultiScale(face_roi, 1.1, 4)
    eye_regions = []
    for (ex, ey, ew, eh) in eyes[:2]:
        abs_x, abs_y = x + ex, y + ey
        eye_regions.append((abs_x, abs_y, ew, eh))
    if eye_regions:
        results['eyes'] = eye_regions
        print(f"  ✓ 检测到 {len(eye_regions)} 只眼睛")

    # 嘴巴检测
    mouth_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_smile.xml'
    )
    mouths = mouth_cascade.detectMultiScale(face_roi, 1.3, 15)
    if len(mouths) > 0:
        mx, my, mw, mh = mouths[0]
        results['mouth'] = (x + mx, y + my, mw, mh)
        print(f"  ✓ 嘴巴: {mw}x{mh}")

    return results


def detect_anime_face(bgr):
    """
    二次元角色面部检测：基于皮肤色 + 边缘密度的启发式方法
    """
    print("  🎭 使用二次元面部启发式检测...")
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    results = {}

    # 皮肤色 mask
    skin = cv2.inRange(hsv, SKIN_LOWER, SKIN_UPPER)
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    # 找最大的皮肤色连通域（应该是脸）
    contours, _ = cv2.findContours(skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # 只取上半部分（脸），下半可能是身体
        face_h = int(h * 0.55)
        results['face'] = (x, y, w, face_h)
        print(f"  ✓ 面部区域估计: x={x} y={y} w={w} h={face_h}")

        # 在面部区域找眼睛（高对比度小区域）
        face_roi = gray[y:y+face_h, x:x+w]
        # 用Laplacian找边缘密集的区域
        lap = cv2.Laplacian(face_roi, cv2.CV_64F)
        lap_abs = np.abs(lap)
        _, lap_thresh = cv2.threshold(lap_abs.astype(np.uint8), 0, 255,
                                       cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学处理，找独立小块
        kernel = np.ones((3, 3), np.uint8)
        lap_thresh = cv2.erode(lap_thresh, kernel, iterations=1)
        
        eye_contours, _ = cv2.findContours(lap_thresh, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选可能是眼睛的轮廓（圆形度 + 位置在上半脸）
        eye_regions = []
        face_center_x = w // 2
        for cnt in eye_contours:
            ex, ey, ew, eh = cv2.boundingRect(cnt)
            area = ew * eh
            # 眼睛大小适中，位置在脸上半部偏两侧
            if 30 < area < w * face_h * 0.07 and ey < face_h * 0.7:
                abs_x, abs_y = x + ex, y + ey
                # 区分左右眼
                eye_regions.append((abs_x, abs_y, ew, eh))

        # 取最大的两个作为左右眼
        eye_regions.sort(key=lambda r: -r[2] * r[3])
        if len(eye_regions) >= 2:
            eye_regions = sorted(eye_regions[:2], key=lambda r: r[0])
            results['eyes'] = eye_regions
            for i, (ex, ey, ew, eh) in enumerate(eye_regions):
                side = "左" if i == 0 else "右"
                print(f"  ✓ {side}眼: x={ex} y={ey} w={ew} h={eh}")

        # 嘴巴位置（脸部下半区域）
        mouth_y = y + int(face_h * 0.65)
        mouth_h = int(face_h * 0.2)
        mouth_w = int(w * 0.3)
        mouth_x = x + int(w * 0.35)
        results['mouth'] = (mouth_x, mouth_y, mouth_w, mouth_h)
        print(f"  ✓ 嘴巴区域估计: {mouth_w}x{mouth_h}")

    return results


def extract_layers_from_features(bgr, fg_mask, face_info):
    """
    基于面部特征定位 + 颜色分割，生成 Live2D 标准图层
    """
    print("\n🔬 精细分割图层...")
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    valid = fg_mask > 0

    layers = {}
    used = np.zeros(bgr.shape[:2], dtype=np.uint8)

    # ====== 面部区域 ======
    if 'face' in face_info:
        fx, fy, fw, fh = face_info['face']
        face_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
        face_mask[fy:fy+fh, fx:fx+fw] = 255
        face_mask = face_mask & valid
        layers['01_face_base'] = face_mask.copy()
        used |= face_mask
        print(f"  ✓ 面部基础层")

    # ====== 眼睛 ======
    if 'eyes' in face_info:
        left_eye_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
        right_eye_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)

        for i, (ex, ey, ew, eh) in enumerate(face_info['eyes']):
            # 扩展眼睛 ROI 以捕获完整的眼部区域
            pad = int(ew * 0.5)
            roi = bgr[max(0,ey-pad):ey+eh+pad, max(0,ex-pad):ex+ew+pad]
            if roi.size == 0:
                continue
            roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # 在 ROI 内用边缘检测提取眼部细节
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_edges = cv2.Canny(roi_gray, 40, 120)

            # 膨胀边缘
            roi_edges = cv2.dilate(roi_edges, np.ones((3, 3), np.uint8))

            # 填充轮廓
            contours, _ = cv2.findContours(roi_edges, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            eye_detail = np.zeros(roi.shape[:2], dtype=np.uint8)
            for cnt in contours:
                if cv2.contourArea(cnt) > 10:
                    cv2.drawContours(eye_detail, [cnt], -1, 255, -1)

            if i == 0:  # 左眼
                left_eye_mask[ey-pad:ey+eh+pad, ex-pad:ex+ew+pad] = eye_detail
            else:  # 右眼
                right_eye_mask[ey-pad:ey+eh+pad, ex-pad:ex+ew+pad] = eye_detail

        left_eye_mask = left_eye_mask & valid
        right_eye_mask = right_eye_mask & valid

        if left_eye_mask.sum() > 10:
            layers['02_eye_left'] = left_eye_mask.copy()
            used |= left_eye_mask
            print(f"  ✓ 左眼: {left_eye_mask.sum()} px")
        if right_eye_mask.sum() > 10:
            layers['03_eye_right'] = right_eye_mask.copy()
            used |= right_eye_mask
            print(f"  ✓ 右眼: {right_eye_mask.sum()} px")

    # ====== 嘴巴 ======
    if 'mouth' in face_info:
        mx, my, mw, mh = face_info['mouth']
        mouth_mask = np.zeros(bgr.shape[:2], dtype=np.uint8)
        # 暗色区域在嘴巴位置的检测
        mouth_roi = bgr[my:my+mh, mx:mx+mw]
        if mouth_roi.size > 0:
            mouth_hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
            mouth_dark = cv2.inRange(mouth_hsv, DARK_LOWER, DARK_UPPER)
            mouth_mask[my:my+mh, mx:mx+mw] = mouth_dark

        mouth_mask = mouth_mask & valid & ~used
        if mouth_mask.sum() > 10:
            layers['04_mouth'] = mouth_mask.copy()
            used |= mouth_mask
            print(f"  ✓ 嘴巴: {mouth_mask.sum()} px")

    # ====== 红发层（精细拆分） ======
    red_mask = (cv2.inRange(hsv, RED_LOWER1, RED_UPPER1) |
                cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)) & valid & ~used
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    if red_mask.sum() > 300:
        # 用连通域分析拆分红发为多个组件（刘海/侧发/发包等）
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            red_mask, connectivity=8
        )

        hair_parts = []
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 100:  # 过滤小噪点
                component = (labels == i).astype(np.uint8) * 255
                cx, cy = centroids[i]
                hair_parts.append((area, cx, cy, component))

        # 按面积排序，分前中后发
        hair_parts.sort(key=lambda x: -x[0])

        # 前发（刘海，通常在上方）
        top_parts = [p for p in hair_parts if p[1] < bgr.shape[1] * 0.5 and p[2] < bgr.shape[0] * 0.5]
        # 侧发（左右两侧）
        side_parts = [p for p in hair_parts if p[2] > bgr.shape[0] * 0.3]

        if top_parts:
            front_hair = np.zeros(bgr.shape[:2], dtype=np.uint8)
            for _, _, _, comp in top_parts[:2]:
                front_hair |= comp
            front_hair = front_hair & valid & ~used
            layers['05_hair_front'] = front_hair.copy()
            used |= front_hair
            print(f"  ✓ 前发(刘海): {front_hair.sum()} px")

        if side_parts:
            side_hair = np.zeros(bgr.shape[:2], dtype=np.uint8)
            for _, _, _, comp in side_parts[:2]:
                side_hair |= comp
            side_hair = side_hair & valid & ~used
            if side_hair.sum() > 100:
                layers['06_hair_side'] = side_hair.copy()
                used |= side_hair
                print(f"  ✓ 侧发: {side_hair.sum()} px")

        # 剩余红发
        remaining_hair = red_mask & ~used
        if remaining_hair.sum() > 100:
            layers['07_hair_back'] = remaining_hair.copy()
            used |= remaining_hair
            print(f"  ✓ 后发/其他红发: {remaining_hair.sum()} px")

    # ====== 白色区域（衣服） ======
    white_mask = cv2.inRange(hsv, WHITE_LOWER, WHITE_UPPER) & valid & ~used
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    if white_mask.sum() > 300:
        layers['08_clothes_white'] = white_mask.copy()
        used |= white_mask
        print(f"  ✓ 白色衣服: {white_mask.sum()} px")

    # ====== 粉色区域 ======
    pink_mask = cv2.inRange(hsv, PINK_LOWER, PINK_UPPER) & valid & ~used
    pink_mask = cv2.morphologyEx(pink_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if pink_mask.sum() > 200:
        layers['09_pink_parts'] = pink_mask.copy()
        used |= pink_mask
        print(f"  ✓ 粉色装饰: {pink_mask.sum()} px")

    # ====== 皮肤 ======
    skin1 = cv2.inRange(hsv, SKIN_LOWER, SKIN_UPPER)
    skin_mask = skin1 & valid & ~used
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    if skin_mask.sum() > 300:
        layers['10_skin'] = skin_mask.copy()
        used |= skin_mask
        print(f"  ✓ 皮肤: {skin_mask.sum()} px")

    # ====== 深色线条 ======
    dark_mask = cv2.inRange(hsv, DARK_LOWER, DARK_UPPER) & valid & ~used
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    if dark_mask.sum() > 100:
        layers['11_dark_lines'] = dark_mask.copy()
        used |= dark_mask
        print(f"  ✓ 深色线条: {dark_mask.sum()} px")

    # ====== 身体剩余 ======
    remaining = valid.astype(np.uint8) * 255
    remaining[used > 0] = 0
    remaining = cv2.morphologyEx(remaining, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if remaining.sum() > 200:
        layers['12_body_rest'] = remaining.copy()
        print(f"  ✓ 身体剩余: {remaining.sum()} px")

    return layers


def export_and_psd(base_rgba, layers):
    """导出 PNG + 合成 PSD"""
    print("\n📦 导出图层...")
    exported = {}
    base_rgba.save(PNG_DIR / "99_full.png")
    exported['99_full'] = str(PNG_DIR / "99_full.png")

    for name in sorted(layers.keys()):
        mask = layers[name]
        arr = np.array(base_rgba).copy()
        arr[:, :, 3] = np.where(mask > 0, arr[:, :, 3], 0)
        img = Image.fromarray(arr, 'RGBA')
        path = PNG_DIR / f"{name}.png"
        img.save(path)
        exported[name] = str(path)
        print(f"  ✓ {name}.png")

    print("\n🎭 合成 PSD...")
    psd = PSDImage.new("RGBA", base_rgba.size, color=0)
    for name in sorted(exported.keys(), reverse=True):
        if name == '99_full':
            continue
        img = Image.open(exported[name]).convert("RGBA")
        psd.create_pixel_layer(img, name=name)
    
    psd.save(PSD_OUTPUT)
    print(f"  ✅ PSD: {PSD_OUTPUT}")
    print(f"  📏 {len(layers)} 个图层")

    # 预览图
    print("\n🖼️ 生成预览...")
    cols, w, h = 3, base_rgba.size[0] // 3, base_rgba.size[1] // 3
    layer_list = sorted(layers.keys())
    rows = (len(layer_list) + cols - 1) // cols + 1  # +1 for full
    preview = Image.new('RGBA', (w * cols, h * rows))
    preview.paste(base_rgba.resize((w, h)), (w, 0))

    for i, name in enumerate(layer_list):
        col = i % cols
        row = (i // cols) + 1
        img = Image.open(exported[name]).convert("RGBA")
        img.thumbnail((w, h))
        # 画在棋盘格背景上以便看到透明区域
        checker = Image.new('RGBA', (w, h), (240, 240, 240, 255))
        for px in range(0, w, 10):
            for py in range(0, h, 10):
                if (px // 10 + py // 10) % 2 == 0:
                    for dx in range(10):
                        for dy in range(10):
                            if px+dx < w and py+dy < h:
                                checker.putpixel((px+dx, py+dy), (200, 200, 200, 255))
        checker.paste(img, (0, 0), img)
        preview.paste(checker, (col * w, row * h))

    preview_path = OUTPUT_DIR / "preview.png"
    preview.save(preview_path)
    print(f"  ✅ 预览: {preview_path}")


def main():
    print("=" * 60)
    print("🎀 Live2D 精细拆分 v3")
    print("=" * 60)

    ensure_dirs()
    
    # 1. 读取 + 去背景
    pil_img, bgr = load_image(INPUT_PATH)
    print(f"📂 尺寸: {bgr.shape[1]}x{bgr.shape[0]}")
    base_rgba, fg_mask = grabcut_remove_bg(bgr)

    # 2. 面部检测
    face_info = detect_face_regions(bgr)

    # 3. 精细图层分割
    layers = extract_layers_from_features(bgr, fg_mask, face_info)

    # 4. 导出 PSD + 预览
    export_and_psd(base_rgba, layers)

    print(f"\n{'=' * 60}")
    print(f"✨ 拆分完成！共 {len(layers)} 个图层")
    print(f"\n📂 输出:")
    print(f"  PSD: {PSD_OUTPUT}")
    print(f"  PNG: {PNG_DIR}/")
    print(f"  预览: {OUTPUT_DIR / 'preview.png'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
