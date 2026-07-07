import subprocess
import sys

years = [str(y) for y in range(1904, 1920)]

for name in ["University of North Dakota"]:
    for y in years:
        subprocess.run([sys.executable, "codes/use_ocr.py", name, y], check=True)
