import subprocess

years = [str(y) for y in range(1904, 1920)]

for name in ["University of North Dakota"]:
    for y in years:
        subprocess.run(["python", "codes_liuyaxuan/use_ocr.py", name, y])