import os
from PIL import Image

def convert_jp2_folder_to_png(folder_path):
    """
    将指定文件夹中的所有 .jp2 文件转换为 .png，并删除原 .jp2 文件
    """
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return

    jp2_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jp2')]
    if not jp2_files:
        print("没有找到 .jp2 文件")
        return

    for idx, filename in enumerate(jp2_files, 1):
        jp2_path = os.path.join(folder_path, filename)
        png_path = os.path.join(folder_path, filename.rsplit('.', 1)[0] + '.png')

        try:
            print(f"[{idx}/{len(jp2_files)}] 转换 {filename} -> {os.path.basename(png_path)}")
            img = Image.open(jp2_path)
            img.save(png_path, 'PNG')
            os.remove(jp2_path)  # 删除原 .jp2 文件
        except Exception as e:
            print(f"转换失败: {filename}, 错误: {str(e)}")

    print("转换完成！")

if __name__ == "__main__":
    print(1)
    import sys
    if len(sys.argv) != 2:
        print("用法: python convert_jp2_to_png.py <文件夹路径>")
        sys.exit(1)

    folder = sys.argv[1]
    convert_jp2_folder_to_png(folder)
 