#!/usr/bin/env python3
"""
P1 #17 — 절대경로 → 상대경로 일괄 변환
═══════════════════════════════════════════════════
실행: I-mPine 루트에서 python patches/P1_17_fix_paths.py

현재 문제:
  Modeling/4차/model1_v4_final.py
    → OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
  Modeling/6차/model1_final_재구현_TierA_TierB_검증.py
    → MOD = r"C:\\Users\\SAMSUNG\\OneDrive\\..."
  Modeling/7차/model2_final_재구현.py
    → PANEL = r"C:\\Users\\SAMSUNG\\OneDrive\\..."

저장소를 클론한 심사위원은 스크립트를 실행할 수 없습니다.
필요한 CSV는 저장소 안에 있으므로 상대경로로 바꿉니다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # I-mPine 루트

# ── 매핑: (파일, 변수, 새 값) ───────────────────────────────
PATCHES = [
    # model1_v4_final.py
    (
        "Modeling/4차/model1_v4_final.py",
        [
            (r'OUTDIR\s*=\s*["\'].*?["\']',
             'OUTDIR = str(Path(__file__).resolve().parent / "output")'),
            (r'MODELDIR\s*=\s*.*',
             'MODELDIR = OUTDIR'),
            (r'PANEL\s*=\s*.*',
             'PANEL = str(Path(__file__).resolve().parents[1] / "3차" / "CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv")'),
        ],
        # 파일 상단에 추가할 import
        "from pathlib import Path\nimport os\nos.makedirs(Path(__file__).resolve().parent / 'output', exist_ok=True)"
    ),
    # model1_final_재구현_TierA_TierB_검증.py
    (
        "Modeling/6차/model1_final_재구현_TierA_TierB_검증.py",
        [
            (r'MOD\s*=\s*r?["\'].*?["\']',
             'MOD = str(Path(__file__).resolve().parents[1])'),
            (r'tierA_path\s*=\s*.*',
             'tierA_path = str(Path(MOD) / "6차" / "CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv")'),
            (r'tierB_path\s*=\s*.*',
             'tierB_path = str(Path(MOD) / "3차" / "CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv")'),
        ],
        "from pathlib import Path"
    ),
    # model2_final_재구현.py
    (
        "Modeling/7차/model2_final_재구현.py",
        [
            (r'PANEL\s*=\s*r?["\'].*?["\']',
             'PANEL = str(Path(__file__).resolve().parents[1] / "6차" / "CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv")'),
            (r'OUTDIR\s*=\s*r?["\'].*?["\']',
             'OUTDIR = str(Path(__file__).resolve().parent)'),
        ],
        "from pathlib import Path\nimport os"
    ),
]

def patch_file(rel_path, replacements, header_import):
    fpath = ROOT / rel_path
    if not fpath.exists():
        print(f"  ⚠ 파일 없음: {rel_path}")
        return False
    
    text = fpath.read_text(encoding='utf-8')
    original = text
    
    # import 추가 (이미 있으면 스킵)
    if header_import and 'from pathlib import Path' not in text:
        # docstring 뒤에 삽입
        ds_end = text.find('"""', text.find('"""') + 3)
        if ds_end > 0:
            insert_pos = ds_end + 3
            text = text[:insert_pos] + '\n' + header_import + '\n' + text[insert_pos:]
        else:
            # import 블록 뒤에 삽입
            last_import = max(text.rfind('\nimport '), text.rfind('\nfrom '))
            if last_import > 0:
                eol = text.find('\n', last_import + 1)
                text = text[:eol] + '\n' + header_import + text[eol:]
            else:
                text = header_import + '\n' + text
    
    # 패턴 치환
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, count=1)
    
    if text != original:
        # 백업
        bak = fpath.with_suffix('.py.bak')
        fpath.rename(bak)
        fpath.write_text(text, encoding='utf-8')
        print(f"  ✓ 패치 완료: {rel_path} (원본 → .py.bak)")
        return True
    else:
        print(f"  - 변경 없음: {rel_path}")
        return False

def main():
    print("P1 #17 — 절대경로 → 상대경로 변환\n")
    patched = 0
    for rel_path, replacements, header in PATCHES:
        print(f"[{rel_path}]")
        if patch_file(rel_path, replacements, header):
            patched += 1
    
    print(f"\n완료: {patched}개 파일 패치")
    
    # 검증: 남은 절대경로 탐색
    print("\n=== 잔여 절대경로 스캔 ===")
    count = 0
    for py in (ROOT / "Modeling").rglob("*.py"):
        text = py.read_text(encoding='utf-8', errors='replace')
        for i, line in enumerate(text.split('\n'), 1):
            if re.search(r'[A-Z]:\\|/Users/|/home/(?!claude)', line) and not line.strip().startswith('#'):
                print(f"  {py.relative_to(ROOT)}:{i}  {line.strip()[:100]}")
                count += 1
    if count == 0:
        print("  없음 ✓")

if __name__ == '__main__':
    main()
