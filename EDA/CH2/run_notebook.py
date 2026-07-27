# -*- coding: utf-8 -*-
"""노트북을 실제로 실행하고 실행 결과가 반영된 .ipynb로 덮어쓴다."""
import nbformat
from nbclient import NotebookClient

NB_PATH = "eda_지자체대응역량.ipynb"

nb = nbformat.read(NB_PATH, as_version=4)
client = NotebookClient(nb, timeout=600, kernel_name="python3")
try:
    client.execute()
    status = "SUCCESS"
except Exception as e:
    status = f"FAILED: {type(e).__name__}: {e}"

with open(NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("실행 상태:", status)

# 에러가 발생한 셀 확인
for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") == "code":
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                print(f"\n=== 셀 {i} 에러 ===")
                print(out.get("ename"), out.get("evalue"))
                print("\n".join(out.get("traceback", []))[:3000])
