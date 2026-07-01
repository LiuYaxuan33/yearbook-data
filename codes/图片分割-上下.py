import cv2
import os
import glob

input_dir = 'C:/Users/32783/Desktop/Yearbook_OCR_to_json/pics/Clemson/Clemson University_1904'  # 输入图片目录
output_dir = 'C:/Users/32783/Desktop/Yearbook_OCR_to_json/pics/Clemson/Clemson University_1904_cleaned'  # 输出目录

os.makedirs(output_dir, exist_ok=True)
image_files = glob.glob(os.path.join(input_dir, '*.*'))  # 支持所有图片格式

click_y = None

def mouse_callback(event, x, y, flags, param):
    global click_y
    if event == cv2.EVENT_LBUTTONDOWN:
        click_y = y
        print(f"分割位置：y={y}")

for img_path in image_files:
    img = cv2.imread(img_path)
    if img is None:
        continue
    h, w = img.shape[:2]
    
    cv2.namedWindow('选择分割位置', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('选择分割位置', 420, 980)
    cv2.setMouseCallback('选择分割位置', mouse_callback)
    
    click_y = None
    while True:
        cv2.imshow('选择分割位置', img)
        key = cv2.waitKey(1)
        if click_y is not None or key == 27:
            break
    if key == 27:  # 按ESC退出
        break
    
    if click_y is not None and 0 < click_y < h:
        up = img[:click_y, :]
        down = img[click_y:, :]
        base = os.path.basename(img_path)
        name, ext = os.path.splitext(base)
        cv2.imwrite(f'{output_dir}/{name}_left{ext}', up)
        cv2.imwrite(f'{output_dir}/{name}_right{ext}', down)
    
    cv2.destroyAllWindows()

print("处理完成！")