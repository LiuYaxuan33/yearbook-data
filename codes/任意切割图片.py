import cv2
import os
import glob
import numpy as np

# === 参数设置 ===
input_dir = r"pics\New Mexico State University\New Mexico State University_1909"
output_dir = r"pics\New Mexico State University\New Mexico State University_1909_split"
os.makedirs(output_dir, exist_ok=True)

image_files = glob.glob(os.path.join(input_dir, '*.*'))

# === 全局变量 ===
split_lines = []   # 存储分割线
split_mode = 'v'   # v=vertical, h=horizontal
redraw = False     # 控制窗口刷新


# === 鼠标回调函数 ===
def mouse_callback(event, x, y, flags, param):
    global split_lines, redraw, split_mode
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"👆 左键点击 ({x}, {y})")
        if split_mode == 'v':
            split_lines.append(('v', int(x / param["scale"])))  # 转回原图坐标
            print(f"添加纵向分割线 x={int(x / param['scale'])}")
        else:
            split_lines.append(('h', int(y / param["scale"])))
            print(f"添加横向分割线 y={int(y / param['scale'])}")
        redraw = True

    elif event == cv2.EVENT_RBUTTONDOWN:
        print(f"👆 右键点击 ({x}, {y})")
        if split_lines:
            removed = split_lines.pop()
            print(f"删除分割线 {removed}")
        else:
            print("当前没有可删除的分割线。")
        redraw = True


# === 主循环 ===
for img_path in image_files:
    # 断点续跑：如果已有分割结果，则跳过
    name, ext = os.path.splitext(os.path.basename(img_path))
    existing = [f for f in os.listdir(output_dir) if f.startswith(name + "_part")]
    if existing:
        print(f"已存在分割结果，跳过：{name}{ext}")
        continue

    # 读取图像（支持中文路径）
    with open(img_path, "rb") as f:
        img_data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    if img is None:
        print(f"无法读取: {img_path}")
        continue

    h, w = img.shape[:2]
    split_lines = []
    split_mode = 'v'
    redraw = True  # 初次显示需要绘制

    # 自动按比例缩放到合理尺寸
    max_height = 900
    scale = min(1.0, max_height / h)
    disp = cv2.resize(img, (int(w * scale), int(h * scale)))

    cv2.namedWindow('Split_Presee', cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback('Split_Presee', mouse_callback, {"scale": scale})

    print(f"\n处理 {name}{ext}：")
    print("操作说明：")
    print("  - 鼠标左键：添加分割线")
    print("  - 鼠标右键：撤销最后一条线")
    print("  - 按 v：切换纵向模式")
    print("  - 按 h：切换横向模式")
    print("  - 按 Enter：确认分割")
    print("  - 按 ESC：跳过")

    while True:
        if redraw:
            display = disp.copy()
            # 绘制分割线（按比例缩放）
            for mode, pos in split_lines:
                if mode == 'v':
                    cv2.line(display, (int(pos * scale), 0), (int(pos * scale), display.shape[0]), (0, 255, 0), 2)
                else:
                    cv2.line(display, (0, int(pos * scale)), (display.shape[1], int(pos * scale)), (255, 0, 0), 2)

            mode_text = f"Mode: {'Vertical' if split_mode == 'v' else 'Horizontal'}"
            cv2.putText(display, mode_text, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            cv2.imshow('Split_Presee', display)
            redraw = False

        key = cv2.waitKey(20) & 0xFF

        if key == 27:  # ESC
            print("跳过该图片。")
            break
        elif key == 13:  # Enter
            print("确认分割并保存结果...")
            all_v = sorted([p for m, p in split_lines if m == 'v'])
            all_h = sorted([p for m, p in split_lines if m == 'h'])
            x_points = [0] + all_v + [w]
            y_points = [0] + all_h + [h]
            count = 1

            for i in range(len(y_points) - 1):
                for j in range(len(x_points) - 1):
                    piece = img[y_points[i]:y_points[i + 1], x_points[j]:x_points[j + 1]]
                    out_path = os.path.join(output_dir, f"{name}_part{count}{ext}")
                    success, encoded_img = cv2.imencode(ext, piece)
                    if success:
                        encoded_img.tofile(out_path)
                    else:
                        print(f"第 {count} 张保存失败：{out_path}")
                    count += 1

            print(f"共保存 {count - 1} 个分割结果。")
            break
        elif key == ord('v'):
            split_mode = 'v'
            print("切换为纵向分割模式。")
        elif key == ord('h'):
            split_mode = 'h'
            print("切换为横向分割模式。")
        elif key == ord('r'):
            split_lines.clear()
            print("重置所有分割线。")
            redraw = True

    cv2.destroyAllWindows()

print("🎉 所有图片处理完成！")
