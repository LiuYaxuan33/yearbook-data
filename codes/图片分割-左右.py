import cv2
import os
import glob

input_dir = "pics/University of Florida/1914-"
output_dir = "pics/University of Florida/1914"
os.makedirs(output_dir, exist_ok=True)
image_files = glob.glob(os.path.join(input_dir, '*.*'))  # 支持所有图片格式

click_x = None

def mouse_callback(event, x, y, flags, param):
    global click_x
    if event == cv2.EVENT_LBUTTONDOWN:
        click_x = x
        print(f"分割位置：x={x}")

for img_path in image_files:
    base = os.path.basename(img_path)
    name, ext = os.path.splitext(base)
    output_path = os.path.join(output_dir, f'{name}_left{ext}')

    # --- 断点续跑：如果输出文件已存在，则跳过 -
    if os.path.exists(output_path):
        print(f"跳过已处理文件: {output_path}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        continue
    h, w = img.shape[:2]
    
    cv2.namedWindow('选择裁剪区域', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('选择裁剪区域', 620, 980)
    cv2.setMouseCallback('选择裁剪区域', mouse_callback)
    
    click_x = None
    while True:
        cv2.imshow('选择裁剪区域', img)
        key = cv2.waitKey(1)
        if click_x is not None or key == 27:
            break
    if key == 27:  # 按ESC退出
        break
    
    if click_x is not None and 0 < click_x < w:
        left = img[:, :click_x]
        right = img[:, click_x:]
        base = os.path.basename(img_path)
        name, ext = os.path.splitext(base)
        cv2.imwrite(f'{output_dir}/{name}_left{ext}', left)
        cv2.imwrite(f'{output_dir}/{name}_right{ext}', right)
    
    cv2.destroyAllWindows()

print("处理完成！")