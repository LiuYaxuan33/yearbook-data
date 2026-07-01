import cv2
import os
import numpy as np

# === 参数设置 ===
input_dir = r"pics/University of Idaho/University of Idaho_1906"  # 输入文件夹
output_dir = r"pics/University of Idaho/University of Idaho_1906_compressed"  # 输出文件夹
max_dim = 3000        # 图片最大边长（像素）
max_size_mb = 4       # 最大文件大小（MB）
min_quality = 40      # 最低JPEG质量
init_quality = 90     # 初始JPEG质量

# === 函数定义 ===
def compress_image(in_path, out_path, max_dim=3000, max_size_mb=4, init_quality=90, min_quality=40):
    """自动压缩图片到指定大小/分辨率"""
    try:
        # ✅ 用 imdecode 支持中文路径
        with open(in_path, "rb") as f:
            img_data = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

        if img is None:
            print(f"❌ 无法读取: {in_path}")
            return

        h, w = img.shape[:2]
        if h > max_dim or w > max_dim:
            scale = max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            print(f"🔧 缩放图片: {w}x{h} → {new_w}x{new_h}")

        quality = init_quality
        success, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not success:
            print(f"❌ 编码失败: {in_path}")
            return

        size_mb = len(buffer) / (1024 * 1024)
        while size_mb > max_size_mb and quality > min_quality:
            quality -= 10
            success, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            size_mb = len(buffer) / (1024 * 1024)

        # ✅ 支持中文路径保存
        buffer.tofile(out_path)
        print(f"✅ 压缩完成: {os.path.basename(in_path)} ({size_mb:.2f}MB, Q={quality})")

    except Exception as e:
        print(f"⚠️ 压缩失败 {in_path}: {e}")


# === 主程序 ===
for root, _, files in os.walk(input_dir):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            continue

        in_path = os.path.join(root, file)
        rel_path = os.path.relpath(in_path, input_dir)
        out_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        compress_image(in_path, out_path, max_dim, max_size_mb, init_quality, min_quality)

print("\n🎉 所有图片压缩完成！")
