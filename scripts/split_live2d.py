"""
Live2D 自动拆分脚本 v2 (离线版)
使用 OpenCV GrabCut 去背景 + HSV 色彩分割 + PSD 导出
无需下载 AI 模型，纯离线运行
"""
import os
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from psd_tools import PSDImage

# ========== 配置 ==========
INPUT_PATH = "E:/桌面/galgame/desktop-pet/assets/character_original.jpg"
OUTPUT_DIR = Path("E:/桌面/galgame/desktop-pet/assets/live2d_layers")
PSD_OUTPUT = OUTPUT_DIR / "character_split.psd"
PNG_OUTPUT_DIR = OUTPUT_DIR / "png_layers"

# ========== HSV 颜色范围 ==========
# 皮肤色（亚洲人）
SKIN_LOWER = np.array([0, 15, 60])
SKIN_UPPER = np.array([25, 200, 255])
SKIN_LOWER2 = np.array([0, 20, 40])
SKIN_UPPER2 = np.array([30, 255, 255])

# 红色系（头发、装饰）
RED_LOWER1 = np.array([0, 60, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([160, 60, 50])
RED_UPPER2 = np.array([180, 255, 255])

# 粉色系（皮肤/粉色衣服）
PINK_LOWER = np.array([140, 30, 100])
PINK_UPPER = np.array([175, 255, 255])

# 白色系（衣服、眼白）
WHITE_LOWER = np.array([0, 0, 190])
WHITE_UPPER = np.array([180, 25, 255])

# 深色系（眼睛、眉毛、线条）
DARK_LOWER = np.array([0, 0, 0])
DARK_UPPER = np.array([180, 255, 80])

# 蓝色/青色
BLUE_LOWER = np.array([90, 40, 40])
BLUE_UPPER = np.array([140, 255, 255])

# 黄色系
YELLOW_LOWER = np.array([20, 50, 50])
YELLOW_UPPER = np.array([40, 255, 255])

# 绿色系
GREEN_LOWER = np.array([40, 50, 50])
GREEN_UPPER = np.array([80, 255, 255])


def create_output_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)
    print(f"✅ 输出目录: {OUTPUT_DIR}")


def remove_background_grabcut(img_bgr):
    """
    使用 OpenCV GrabCut 去除背景
    返回 RGBA 图像（透明背景）
    """
    print("\n🎨 正在去除背景 (GrabCut)...")

    h, w = img_bgr.shape[:2]

    # 创建矩形 ROI（缩进 5%，假设主体在画面内）
    margin_x = int(w * 0.05)
    margin_y = int(h * 0.05)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    # 初始化 mask
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # GrabCut 分割（迭代 6 次）
    cv2.grabCut(img_bgr, mask, rect, bgd_model, fgd_model, 6, cv2.GC_INIT_WITH_RECT)

    # 生成二值 mask（0=背景, 1=前景, 2=可能背景, 3=可能前景）
    fg_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)

    # 形态学处理：去除噪点 + 填充空洞
    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    # 转换为 RGBA
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    rgba = np.dstack([img_rgb, fg_mask])

    result = Image.fromarray(rgba, 'RGBA')
    result.save(PNG_OUTPUT_DIR / "00_transparent.png")
    print(f"  ✓ 背景已去除 (前景像素: {fg_mask.sum()})")

    return result, fg_mask


def refine_mask_with_edge_detect(img_bgr, fg_mask):
    """
    用边缘检测细化 mask
    在 GrabCut 结果基础上，使用 Canny 边缘检测填补可能遗漏的线条
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 100)
    # 膨胀边缘，让线条区域被包含
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
    # 合并到前景 mask
    refined = fg_mask.copy()
    refined[edges > 0] = 255
    return refined


def split_layers(img_bgr, fg_mask):
    """
    基于 HSV 颜色空间的分割
    将人物拆分为：皮肤、红色头发、白色衣服、深色线条等
    """
    print("\n🔬 正在进行颜色分割...")

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    valid = fg_mask > 0

    layers = {}
    used_mask = np.zeros(img_bgr.shape[:2], dtype=np.uint8)

    # --- 1. 皮肤区域 ---
    skin1 = cv2.inRange(hsv, SKIN_LOWER, SKIN_UPPER)
    skin2 = cv2.inRange(hsv, SKIN_LOWER2, SKIN_UPPER2)
    skin_mask = (skin1 | skin2) & valid
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    if skin_mask.sum() > 300:
        layers['03_skin'] = skin_mask
        used_mask |= skin_mask
        print(f"  ✓ 皮肤区域: {skin_mask.sum()} px")

    # --- 2. 红色头发/装饰 ---
    red1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
    red2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    red_mask = (red1 | red2) & valid & ~used_mask
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if red_mask.sum() > 300:
        layers['01_hair_red'] = red_mask
        used_mask |= red_mask
        print(f"  ✓ 红色头发区域: {red_mask.sum()} px")

    # --- 3. 粉色区域 ---
    pink_mask = cv2.inRange(hsv, PINK_LOWER, PINK_UPPER) & valid & ~used_mask
    pink_mask = cv2.morphologyEx(pink_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if pink_mask.sum() > 300:
        layers['04_pink_parts'] = pink_mask
        used_mask |= pink_mask
        print(f"  ✓ 粉色区域: {pink_mask.sum()} px")

    # --- 4. 白色/浅色区域 ---
    white_mask = cv2.inRange(hsv, WHITE_LOWER, WHITE_UPPER) & valid & ~used_mask
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if white_mask.sum() > 300:
        layers['02_white_parts'] = white_mask
        used_mask |= white_mask
        print(f"  ✓ 白色/浅色区域: {white_mask.sum()} px")

    # --- 5. 深色区域（眼睛、眉毛、线条） ---
    dark_mask = cv2.inRange(hsv, DARK_LOWER, DARK_UPPER) & valid & ~used_mask
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    if dark_mask.sum() > 200:
        layers['05_dark_parts'] = dark_mask
        used_mask |= dark_mask
        print(f"  ✓ 深色/线条区域: {dark_mask.sum()} px")

    # --- 6. 蓝色区域 ---
    blue_mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER) & valid & ~used_mask
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if blue_mask.sum() > 200:
        layers['06_blue_parts'] = blue_mask
        used_mask |= blue_mask
        print(f"  ✓ 蓝色区域: {blue_mask.sum()} px")

    # --- 7. 黄色区域 ---
    yellow_mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER) & valid & ~used_mask
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if yellow_mask.sum() > 200:
        layers['07_yellow_parts'] = yellow_mask
        used_mask |= yellow_mask
        print(f"  ✓ 黄色区域: {yellow_mask.sum()} px")

    # --- 8. 剩余未分类区域 ---
    remaining = valid.astype(np.uint8) * 255
    remaining[used_mask > 0] = 0
    remaining = cv2.morphologyEx(remaining, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    if remaining.sum() > 200:
        layers['00_body_rest'] = remaining
        print(f"  ✓ 身体剩余区域: {remaining.sum()} px")

    return layers


def export_layers(base_img_rgba, layers):
    """导出各图层为独立 PNG"""
    print("\n📦 正在导出各图层...")

    # 保存完整透明图
    base_img_rgba.save(PNG_OUTPUT_DIR / "99_full.png")
    exported = {'99_full': str(PNG_OUTPUT_DIR / "99_full.png")}

    for name, mask in sorted(layers.items()):
        layer_np = np.array(base_img_rgba).copy()
        layer_np[:, :, 3] = np.where(mask > 0, layer_np[:, :, 3], 0)
        result = Image.fromarray(layer_np, 'RGBA')

        filepath = PNG_OUTPUT_DIR / f"{name}.png"
        result.save(filepath)
        exported[name] = str(filepath)
        print(f"  ✓ {name}.png")

    return exported


def create_psd(base_img_rgba, exported_layers):
    """合成 PSD 文件"""
    print("\n🎭 正在合成 PSD 文件...")

    psd = PSDImage.new("RGBA", base_img_rgba.size, color=0)

    # 按名称倒序添加（PSD 栈顺序：底层先加）
    for name in sorted(exported_layers.keys(), reverse=True):
        if name == '99_full':
            continue
        path = exported_layers[name]
        layer_img = Image.open(path).convert("RGBA")
        psd.create_pixel_layer(layer_img, name=name)

    psd.save(PSD_OUTPUT)
    print(f"  ✅ PSD 已保存: {PSD_OUTPUT}")
    print(f"  📏 图层数: {len(exported_layers) - 1}")
    print(f"  📐 画布尺寸: {base_img_rgba.size}")


def generate_preview(base_img_rgba, exported_layers):
    """生成预览对比图"""
    w, h = base_img_rgba.size
    cols = 3
    rows = (len(exported_layers) + cols - 1) // cols
    thumb_w = w // cols
    thumb_h = h // cols

    preview = Image.new('RGBA', (thumb_w * cols, thumb_h * rows))

    for idx, (name, path) in enumerate(sorted(exported_layers.items())):
        if name == '99_full':
            continue
        col = idx % cols
        row = idx // cols
        layer_img = Image.open(path).convert("RGBA")
        layer_img.thumbnail((thumb_w, thumb_h))
        preview.paste(layer_img, (col * thumb_w, row * thumb_h))

    preview_path = OUTPUT_DIR / "preview.png"
    preview.save(preview_path)
    print(f"  ✅ 预览图: {preview_path}")


def main():
    print("=" * 60)
    print("🎀 Live2D 自动拆分工具 v2 (离线版)")
    print("=" * 60)

    create_output_dirs()

    # 读取图片（用 PIL 绕过 OpenCV 中文路径问题）
    print(f"\n📂 输入: {INPUT_PATH}")
    pil_img = Image.open(INPUT_PATH).convert("RGB")
    img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    if img_bgr is None:
        print(f"❌ 无法读取图片: {INPUT_PATH}")
        return
    print(f"  📐 尺寸: {img_bgr.shape[1]}x{img_bgr.shape[0]}")

    # Step 1: GrabCut 去背景
    base_img_rgba, fg_mask = remove_background_grabcut(img_bgr)

    # Step 2: 细化边缘
    fg_mask = refine_mask_with_edge_detect(img_bgr, fg_mask)

    # Step 3: 颜色分割
    layers = split_layers(img_bgr, fg_mask)

    if not layers:
        print("\n⚠️ 未能识别出明显颜色区域，导出完整透明图")
        base_img_rgba.save(PSD_OUTPUT.with_suffix('.png'))
        return

    # Step 4: 导出 PNG
    exported = export_layers(base_img_rgba, layers)

    # Step 5: 合成 PSD
    create_psd(base_img_rgba, exported)

    # Step 6: 生成预览
    generate_preview(base_img_rgba, exported)

    print(f"\n{'=' * 60}")
    print("✨ 拆分完成！")
    print(f"\n📂 输出文件:")
    print(f"  · PSD: {PSD_OUTPUT}")
    print(f"  · PNG 图层: {PNG_OUTPUT_DIR}/")
    print(f"  · 预览图: {OUTPUT_DIR / 'preview.png'}")
    print(f"\n💡 下一步:")
    print(f"  1. 在 Photoshop 中打开 PSD，微调各图层")
    print(f"  2. 手动拆分眼睛、嘴巴、头发（需要更精细的操作）")
    print(f"  3. 导入 Live2D Cubism Editor 进行 rigging")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
