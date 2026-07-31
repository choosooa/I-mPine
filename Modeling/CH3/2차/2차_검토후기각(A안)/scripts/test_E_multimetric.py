# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    for prefix in [f'window.{varname} = ', f'const {varname} = ']:
        i = text.find(prefix)
        if i >= 0:
            start = i + len(prefix)
            obj, end = json.JSONDecoder().raw_decode(text[start:])
            return obj
    raise ValueError("not found: " + varname)

ch1 = load_js(ROOT / "ch1/data.js", "CH1_DATA")
ch2 = load_js(ROOT / "ch2/data.js", "CH2_DATA")

print("CH1_DATA keys:", list(ch1.keys()))
print("sggBurden sample:", ch1['sggBurden'][0] if 'sggBurden' in ch1 else 'N/A')
print()
print("sggBurden count:", len(ch1.get('sggBurden', [])))
