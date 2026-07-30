# -*- coding: utf-8 -*-
import pandas as pd

DATA = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\1차\data"
PATH = DATA + r"\CH2_전체병합패널_5도메인_2016_2023_최종보정.csv"
df = pd.read_csv(PATH)

col = "도로소나무비율_500m"
if f"{col}_보정전" in df.columns:
    print("이미 도로 보정이 적용된 파일입니다 - 중복 적용 방지를 위해 중단합니다.")
else:
    print("보정 전 연도별 평균:")
    print(df.groupby("연도")[col].mean().round(4).to_string())

    ref = df.loc[df["연도"] == 2023, ["시도", "시군구", col]].rename(columns={col: f"{col}_2023기준"})
    print("\n2023 기준값 결측:", ref[f"{col}_2023기준"].isna().sum(), "/", len(ref))

    df = df.merge(ref, on=["시도", "시군구"], how="left")
    df[f"{col}_보정전"] = df[col]
    df[col] = df[f"{col}_2023기준"]
    df = df.drop(columns=[f"{col}_2023기준"])

    print("\n보정 후 연도별 평균:")
    print(df.groupby("연도")[col].mean().round(4).to_string())

    df.to_csv(PATH, index=False, encoding="utf-8-sig")
    print("\nOVERWRITTEN:", PATH)
    print("shape:", df.shape)
