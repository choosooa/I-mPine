# -*- coding: utf-8 -*-
import os
import time
import geopandas as gpd
import pandas as pd

t_start = time.time()

ROAD_BASE = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\data\CH2\1. 환경\인위적 확산\자료\도로"
PINE_GPKG = r"C:\Users\SAMSUNG\Downloads\pine_by_sigungu.gpkg"
OUT_CSV = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\1차\data\도로소나무비율_TierA_104제외_전체8개년.csv"
CHECKPOINT_DIR = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\1차\data\_tierA_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

YEAR_CONFIG = {
    2016: ("[2016-12-23]+전국표준노드링크.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2017: ("[2017-12-21]+전국표준노드링크.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2018: ("[2018-12-21]전국표준노드링크.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2019: ("[2019-09-20]+전국표준노드링크.zip", "MOCT_LINK.shp", "ROAD_RANK_", "CONNECT_"),
    2020: ("[2020-11-30]NODELINKDATA.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2021: ("[2021-12-09]NODELINKDATA.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2022: ("[2022-07-08]NODELINKDATA2.zip", "MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
    2023: ("[2023-12-18]NODELINKDATA.zip", "[2023-12-18]NODELINKDATA/MOCT_LINK.shp", "ROAD_RANK", "CONNECT"),
}
BUFFERS = [100, 300, 500]

print("[0] 소나무 폴리곤 로드 (1회성)...", flush=True)
t0 = time.time()
pine_sgg = gpd.read_file(PINE_GPKG)
pine_sgg = pine_sgg[pine_sgg["geometry"].notna()].copy()
print(f"    pine_sgg: {len(pine_sgg)}건, {time.time()-t0:.1f}s", flush=True)

all_results = []
for year, (zip_name, shp_rel, rank_f, conn_f) in YEAR_CONFIG.items():
    ckpt_path = os.path.join(CHECKPOINT_DIR, f"year_{year}.csv")
    if os.path.exists(ckpt_path):
        print(f"=== {year}년: 체크포인트 존재, 스킵하고 로드 ===", flush=True)
        all_results.append(pd.read_csv(ckpt_path))
        continue

    print(f"=== {year}년 시작 ===", flush=True)
    t_year = time.time()
    vsi = f"/vsizip/{ROAD_BASE}\\{zip_name}/{shp_rel}"
    where = f"{rank_f} IN ('101','102','103','105')"  # 104 제외 (Tier A)
    links = gpd.read_file(vsi, where=where, columns=[rank_f, conn_f], engine="pyogrio")
    conn_int = pd.to_numeric(links[conn_f], errors="coerce").fillna(-1).astype(int)
    links = links[conn_int == 0].copy()
    links = links.to_crs(epsg=5179)
    print(f"    필터 후 세그먼트: {len(links)}건", flush=True)

    year_rows = []
    for dist in BUFFERS:
        t0 = time.time()
        buffered = links.geometry.buffer(dist)
        union_poly = buffered.union_all() if hasattr(buffered, "union_all") else buffered.unary_union
        inter_area = pine_sgg.geometry.intersection(union_poly).area
        for sigungu_cd, area_m2 in zip(pine_sgg["sigungu_cd"], inter_area):
            year_rows.append({"year": year, "sigungu_cd": sigungu_cd, "buffer_m": dist,
                               "road_inter_ha": area_m2 / 10000.0})
        print(f"    {dist}m 완료: {time.time()-t0:.1f}s", flush=True)

    year_df = pd.DataFrame(year_rows)
    year_df.to_csv(ckpt_path, index=False, encoding="utf-8-sig")
    all_results.append(year_df)
    print(f"=== {year}년 완료: {time.time()-t_year:.1f}s (체크포인트 저장) ===", flush=True)

final = pd.concat(all_results, ignore_index=True)
final.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"\nSAVED: {OUT_CSV}", flush=True)
print(f"전체 소요시간: {time.time()-t_start:.1f}s ({(time.time()-t_start)/60:.1f}분)", flush=True)
print("ALL DONE", flush=True)
