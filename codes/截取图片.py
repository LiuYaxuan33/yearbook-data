import cv2
import os
import glob
import numpy as np

# === 参数设置 ===
input_dir = r"pics\University of Florida\1915-"
output_dir = r"pics\University of Florida\1915"
os.makedirs(output_dir, exist_ok=True)

image_files = glob.glob(os.path.join(input_dir, '*.*'))

# === 全局变量 ===
rectangles = []    # 存储所有矩形 (x1, y1, x2, y2)
temp_start = None  # 临时记录第一次点（左上角）
need_redraw = False


# === 鼠标回调函数 ===
def mouse_callback(event, x, y, flags, param):
    """
    左键第一次点：记录左上角
    左键第二次点：记录右下角，保存矩形
    右键：撤销上一次矩形
    """
    global temp_start, rectangles, need_redraw

    scale = param["scale"]

    if event == cv2.EVENT_LBUTTONDOWN:
        if temp_start is None:
            temp_start = (int(x / scale), int(y / scale))
            print(f"📌 左键第一点（左上角）：{temp_start}")
        else:
            x1, y1 = temp_start
            x2, y2 = int(x / scale), int(y / scale)

            # 自动保证左上右下顺序
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            rectangles.append((x1, y1, x2, y2))
            print(f"🟩 添加矩形：{(x1, y1, x2, y2)}")

            temp_start = None
        need_redraw = True

    elif event == cv2.EVENT_RBUTTONDOWN:
        if rectangles:
            removed = rectangles.pop()
            print(f"❌ 撤销矩形：{removed}")
        else:
            print("没有可撤销的矩形。")
        temp_start = None
        need_redraw = True



# === 主循环 ===
for img_path in image_files:
    # 断点续跑
    name, ext = os.path.splitext(os.path.basename(img_path))
    existing = [f for f in os.listdir(output_dir) if f.startswith(name + "_rect")]
    if existing:
        print(f"已处理：跳过 {name}{ext}")
        continue

    # 读取图像
    with open(img_path, "rb") as f:
        img_data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    if img is None:
        print(f"无法读取: {img_path}")
        continue

    h, w = img.shape[:2]

    rectangles = []
    temp_start = None
    need_redraw = True

    # 缩放显示
    max_height = 900
    scale = min(1.0, max_height / h)
    disp = cv2.resize(img, (int(w * scale), int(h * scale)))

    cv2.namedWindow('Rect_Select', cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback('Rect_Select', mouse_callback, {"scale": scale})

    print(f"\n处理 {name}{ext}:")
    print("操作说明：")
    print("  - 左键第一次点：矩形左上角")
    print("  - 左键第二次点：矩形右下角 → 完成一个矩形")
    print("  - 右键：撤销上一个矩形")
    print("  - Enter：保存所有矩形")
    print("  - ESC：跳过")

    while True:
        if need_redraw:
            display = disp.copy()

            # 绘制已有矩形
            for (x1, y1, x2, y2) in rectangles:
                cv2.rectangle(
                    display,
                    (int(x1 * scale), int(y1 * scale)),
                    (int(x2 * scale), int(y2 * scale)),
                    (0, 255, 0), 2
                )

            # 如果正在框选（只点了一次）
            if temp_start is not None:
                sx, sy = temp_start
                cv2.rectangle(
                    display,
                    (int(sx * scale), int(sy * scale)),
                    (cv2.getWindowImageRect('Rect_Select')[2] // 2,
                     cv2.getWindowImageRect('Rect_Select')[3] // 2),
                    (0, 255, 255), 1
                )

            cv2.imshow("Rect_Select", display)
            need_redraw = False

        key = cv2.waitKey(20) & 0xFF

        if key == 27:  # ESC
            print("跳过该图片。")
            break

        elif key == 13:  # Enter
            print("开始保存矩形区域...")

            max_output_size = 2000  # 最大边长限制
            count = 1

            for (x1, y1, x2, y2) in rectangles:
                crop = img[y1:y2, x1:x2]

                # 限制输出图片大小
                ch, cw = crop.shape[:2]
                scale_o = min(1.0, max_output_size / max(ch, cw))
                if scale_o < 1:
                    crop = cv2.resize(crop, (int(cw * scale_o), int(ch * scale_o)))

                out_path = os.path.join(output_dir, f"{name}_rect{count}{ext}")
                ok, buf = cv2.imencode(ext, crop)
                if ok:
                    buf.tofile(out_path)
                else:
                    print(f"保存失败：{out_path}")
                count += 1

            print(f"🎉 已保存 {count - 1} 个区域。")
            break

    cv2.destroyAllWindows()

print("✨ 所有图片处理完成！")
