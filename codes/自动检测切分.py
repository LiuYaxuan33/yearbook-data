import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def split_columns_auto(image_path, save_debug=False):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化（文字变黑）
    _, bw = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # 去噪
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel)

    h, w = bw.shape

    # 计算竖向投影（每一列黑色像素数量）
    vertical_sum = np.sum(bw > 0, axis=0)

    # 只在中间 40%~60% 搜索“中缝”
    start = int(w * 0.35)
    end   = int(w * 0.65)

    mid_region = vertical_sum[start:end]

    # 找最小值位置（最空的竖线）
    split_x = start + np.argmin(mid_region)

    left = img[:, :split_x]
    right = img[:, split_x:]

    if save_debug:
        debug = img.copy()
        cv2.line(debug, (split_x, 0), (split_x, h), (0,0,255), 3)
        cv2.imwrite("debug_split_line.png", debug)
        cv2.imwrite("left_column.png", left)
        cv2.imwrite("right_column.png", right)

    return left, right


if __name__ == "__main__":
    img_path = r"pics\Virginia Polytenic University_1925\1 (1).png"
    left, right = split_columns_auto(img_path, save_debug=True)

    # 显示看看效果
    plt.figure(figsize=(6,10))
    plt.imshow(cv2.cvtColor(left, cv2.COLOR_BGR2RGB))
    plt.title("LEFT COLUMN")
    plt.axis("off")
    plt.show()

    plt.figure(figsize=(6,10))
    plt.imshow(cv2.cvtColor(right, cv2.COLOR_BGR2RGB))
    plt.title("RIGHT COLUMN")
    plt.axis("off")
    plt.show()