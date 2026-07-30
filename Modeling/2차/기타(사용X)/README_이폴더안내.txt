이 폴더 사용 안내 (README)

이 폴더의 스크립트/로그는 2차 시점의 초기 실험용 프로토타입이며, 최종 채택된 파이프라인이 아니다.
알려진 문제:

1. Mac 경로 하드코딩
   final_modeling.txt, model_b_stage1.txt, model_b_stage3.txt, national_response_robustness.txt,
   early_warning_test.txt 전부 OUTDIR이 "/Users/chanhaeng17/Desktop/..." 로컬 경로로 고정되어 있음.
   실행 환경 이관 시 경로 수정 필요.

2. early_warning_test.txt의 데이터 누수(leakage) 버그
   _gm(지자체 그룹평균) 항을 train/holdout으로 나누기 전에 전체 df에서 계산(41~54번째 줄
   add_gm(df, allx) 호출이 train/holdout 분리보다 앞섬) -> 홀드아웃 정보가 그룹평균에 섞여
   들어가는 전형적 데이터 누수.
   -> 이 버그는 발견 후 이후 버전에서 수정됨: Model 2 최종판(3차 이후)은 _gm을 훈련기간에서만
      계산해 홀드아웃에 고정 적용하는 frozen-gm 방식으로 교체됨. 즉 이 파일의 버그가 실제로
      이후 개선의 계기가 된 것으로, 개발 과정의 정상적인 기록이다.

3. final_modeling_수정본.txt는 위 두 파일과 별개로, 접경지역 GIS 이슈 조사용 실험이며 어떤
   공식 보고서에도 반영되지 않았다. 자세한 내용은 final_modeling_수정본_안내.txt 참고.

결론: 이 폴더의 코드는 참고용 기록이며 최종 채택 코드가 아니다. 실제 최종 파이프라인은
2~6차 각 폴더의 정식 스크립트(예: model1_final.py 등)를 참고할 것.
