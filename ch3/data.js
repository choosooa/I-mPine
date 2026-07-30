/* ============================================================================
   CH3_DATA — 우선지원 전략 설계 실측 데이터
   ----------------------------------------------------------------------------
   01/02: ../ch2/data.js(CH2_DATA, 실측)의 배분갭·유형화를 그대로 사용해 계산.
   03: 산림청 『2025년 산림산업조사(2024년 기준)』 표4-2·4-62·4-63·4-66·4-67에서 직접 추출한 실측치.
   04: 6차 §9 3단계 시나리오는 이미 서술로 완료(정량 시군구별 표는 미반영), 단기경보결합은
   Modeling/7차(Model2 재구현)의 2022년 기준 재발위험확률을 사용함.
   ============================================================================ */

window.CH3_DATA = {
  "meta": {
    "n_sido": 17,
    "special_zone_ref": 12,
    "ch2_linked": true,
    "resolution_note": "CH2는 222개 시군구 단위, 산림산업조사(03번 섹션)는 17개 광역시도 단위까지만 공개됨 — 시군구별 정부지원필요도·참여경험 값은 관할 시도 값을 그대로 적용한 근사치.",
    "source": "CH2: Modeling/6차 최종판(model1_final 재구현) · Model2: Modeling/7차(model2_final 재구현) · 산업기반: 산림청 『2025년 산림산업조사(2024년 기준)』 표4-2·4-62·4-63·4-66·4-67",
    "priority_note": "우선지원 순위 = 취약성지수 − 배분갭(배분갭이 음수=과소배분일수록 순위 상승). 실행가능성 매트릭스의 y축은 관할 시도 산림산업 정부지원필요도 평균(5점 척도)."
  },
  "prioritySggList": [
    {
      "sgg_codes": [
        "46890"
      ],
      "시도명": "전라남도",
      "시군구명": "완도군",
      "index_main": 1.233,
      "배분갭": -7.332,
      "priority_score": 8.565,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1098499867422982,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 1
    },
    {
      "sgg_codes": [
        "28720"
      ],
      "시도명": "인천광역시",
      "시군구명": "옹진군",
      "index_main": 0.857,
      "배분갭": -6.735,
      "priority_score": 7.592,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.060532066204447,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 2
    },
    {
      "sgg_codes": [
        "46900"
      ],
      "시도명": "전라남도",
      "시군구명": "진도군",
      "index_main": 0.629,
      "배분갭": -6.378,
      "priority_score": 7.007,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1114111818164084,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 3
    },
    {
      "sgg_codes": [
        "46870"
      ],
      "시도명": "전라남도",
      "시군구명": "영광군",
      "index_main": 0.559,
      "배분갭": -6.267,
      "priority_score": 6.826,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1834140531714647,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 4
    },
    {
      "sgg_codes": [
        "29110"
      ],
      "시도명": "광주광역시",
      "시군구명": "동구",
      "index_main": 0.531,
      "배분갭": -6.223,
      "priority_score": 6.754,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0807779084481519,
      "정부지원필요도_시도평균": 3.18,
      "priority_rank": 5
    },
    {
      "sgg_codes": [
        "27140"
      ],
      "시도명": "대구광역시",
      "시군구명": "동구",
      "index_main": 0.524,
      "배분갭": -6.212,
      "priority_score": 6.736,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.9978548552987484,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 6
    },
    {
      "sgg_codes": [
        "51170"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "동해시",
      "index_main": 0.489,
      "배분갭": -6.156,
      "priority_score": 6.645,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.1019200480491874,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 7
    },
    {
      "sgg_codes": [
        "27200"
      ],
      "시도명": "대구광역시",
      "시군구명": "남구",
      "index_main": 0.456,
      "배분갭": -6.104,
      "priority_score": 6.56,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0996444251557434,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 8
    },
    {
      "sgg_codes": [
        "51230"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "삼척시",
      "index_main": 0.453,
      "배분갭": -6.099,
      "priority_score": 6.552,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0935319191616418,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 9
    },
    {
      "sgg_codes": [
        "46910"
      ],
      "시도명": "전라남도",
      "시군구명": "신안군",
      "index_main": 0.835,
      "배분갭": -5.714,
      "priority_score": 6.549,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1329124599749242,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 10
    },
    {
      "sgg_codes": [
        "51210"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "속초시",
      "index_main": 0.428,
      "배분갭": -6.059,
      "priority_score": 6.487,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0652425256302868,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 11
    },
    {
      "sgg_codes": [
        "11620"
      ],
      "시도명": "서울특별시",
      "시군구명": "관악구",
      "index_main": 0.4,
      "배분갭": -6.016,
      "priority_score": 6.416,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0466499995199244,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 12
    },
    {
      "sgg_codes": [
        "46710"
      ],
      "시도명": "전라남도",
      "시군구명": "담양군",
      "index_main": 0.384,
      "배분갭": -5.99,
      "priority_score": 6.374,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.2806453073114639,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 13
    },
    {
      "sgg_codes": [
        "46730"
      ],
      "시도명": "전라남도",
      "시군구명": "구례군",
      "index_main": 0.364,
      "배분갭": -5.959,
      "priority_score": 6.323,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.3041568893230673,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 14
    },
    {
      "sgg_codes": [
        "11110"
      ],
      "시도명": "서울특별시",
      "시군구명": "종로구",
      "index_main": 0.359,
      "배분갭": -5.951,
      "priority_score": 6.31,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0462836888791204,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 15
    },
    {
      "sgg_codes": [
        "11380"
      ],
      "시도명": "서울특별시",
      "시군구명": "은평구",
      "index_main": 0.314,
      "배분갭": -5.88,
      "priority_score": 6.194,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0449320246041645,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 16
    },
    {
      "sgg_codes": [
        "46110"
      ],
      "시도명": "전라남도",
      "시군구명": "목포시",
      "index_main": 0.305,
      "배분갭": -5.866,
      "priority_score": 6.171,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1498576840610301,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 17
    },
    {
      "sgg_codes": [
        "51820"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "고성군",
      "index_main": 0.298,
      "배분갭": -5.854,
      "priority_score": 6.152,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.059494140975988,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 18
    },
    {
      "sgg_codes": [
        "45790"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "고창군",
      "index_main": 0.262,
      "배분갭": -5.798,
      "priority_score": 6.06,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1845641058285971,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 19
    },
    {
      "sgg_codes": [
        "46860"
      ],
      "시도명": "전라남도",
      "시군구명": "함평군",
      "index_main": 0.258,
      "배분갭": -5.791,
      "priority_score": 6.049,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1877471024881047,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 20
    },
    {
      "sgg_codes": [
        "11215"
      ],
      "시도명": "서울특별시",
      "시군구명": "광진구",
      "index_main": 0.23,
      "배분갭": -5.748,
      "priority_score": 5.978,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0435872109187783,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 21
    },
    {
      "sgg_codes": [
        "41271",
        "41273"
      ],
      "시도명": "경기도",
      "시군구명": "안산시",
      "index_main": 0.225,
      "배분갭": -5.739,
      "priority_score": 5.964,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0425726185652606,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 22
    },
    {
      "sgg_codes": [
        "11290"
      ],
      "시도명": "서울특별시",
      "시군구명": "성북구",
      "index_main": 0.221,
      "배분갭": -5.732,
      "priority_score": 5.953,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0435967687851289,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 23
    },
    {
      "sgg_codes": [
        "41310"
      ],
      "시도명": "경기도",
      "시군구명": "구리시",
      "index_main": 0.199,
      "배분갭": -5.698,
      "priority_score": 5.897,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0500342480924665,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 24
    },
    {
      "sgg_codes": [
        "11305"
      ],
      "시도명": "서울특별시",
      "시군구명": "강북구",
      "index_main": 0.176,
      "배분갭": -5.662,
      "priority_score": 5.838,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0428505752920411,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 25
    },
    {
      "sgg_codes": [
        "29170"
      ],
      "시도명": "광주광역시",
      "시군구명": "북구",
      "index_main": 0.175,
      "배분갭": -5.661,
      "priority_score": 5.836,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0734377292575864,
      "정부지원필요도_시도평균": 3.18,
      "priority_rank": 26
    },
    {
      "sgg_codes": [
        "47940"
      ],
      "시도명": "경상북도",
      "시군구명": "울릉군",
      "index_main": 0.086,
      "배분갭": -5.75,
      "priority_score": 5.836,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1020210145540409,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 27
    },
    {
      "sgg_codes": [
        "46820"
      ],
      "시도명": "전라남도",
      "시군구명": "해남군",
      "index_main": 0.156,
      "배분갭": -5.631,
      "priority_score": 5.787,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1903585359333966,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 28
    },
    {
      "sgg_codes": [
        "11170"
      ],
      "시도명": "서울특별시",
      "시군구명": "용산구",
      "index_main": 0.15,
      "배분갭": -5.621,
      "priority_score": 5.771,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.04245653065458,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 29
    },
    {
      "sgg_codes": [
        "11260"
      ],
      "시도명": "서울특별시",
      "시군구명": "중랑구",
      "index_main": 0.124,
      "배분갭": -5.579,
      "priority_score": 5.703,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0425110732321446,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 30
    },
    {
      "sgg_codes": [
        "43745"
      ],
      "시도명": "충청북도",
      "시군구명": "증평군",
      "index_main": -0.222,
      "배분갭": -5.77,
      "priority_score": 5.548,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0691467369550234,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 31
    },
    {
      "sgg_codes": [
        "11650"
      ],
      "시도명": "서울특별시",
      "시군구명": "서초구",
      "index_main": 0.058,
      "배분갭": -5.475,
      "priority_score": 5.533,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0453238761018136,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 32
    },
    {
      "sgg_codes": [
        "46830"
      ],
      "시도명": "전라남도",
      "시군구명": "영암군",
      "index_main": 0.047,
      "배분갭": -5.458,
      "priority_score": 5.505,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0629634516353906,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 33
    },
    {
      "sgg_codes": [
        "46810"
      ],
      "시도명": "전라남도",
      "시군구명": "강진군",
      "index_main": 0.024,
      "배분갭": -5.422,
      "priority_score": 5.446,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0628527547855941,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 34
    },
    {
      "sgg_codes": [
        "47760"
      ],
      "시도명": "경상북도",
      "시군구명": "영양군",
      "index_main": 0.577,
      "배분갭": -4.846,
      "priority_score": 5.423,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.2118555187418711,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 35
    },
    {
      "sgg_codes": [
        "46170"
      ],
      "시도명": "전라남도",
      "시군구명": "나주시",
      "index_main": 0.012,
      "배분갭": -5.403,
      "priority_score": 5.415,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1568814277201861,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 36
    },
    {
      "sgg_codes": [
        "41210"
      ],
      "시도명": "경기도",
      "시군구명": "광명시",
      "index_main": 0.002,
      "배분갭": -5.387,
      "priority_score": 5.389,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.0397773247392428,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 37
    },
    {
      "sgg_codes": [
        "51790"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "화천군",
      "index_main": -0.029,
      "배분갭": -5.338,
      "priority_score": 5.309,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0457636783697159,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 38
    },
    {
      "sgg_codes": [
        "41370"
      ],
      "시도명": "경기도",
      "시군구명": "오산시",
      "index_main": -0.036,
      "배분갭": -5.327,
      "priority_score": 5.291,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0392035455378999,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 39
    },
    {
      "sgg_codes": [
        "46790"
      ],
      "시도명": "전라남도",
      "시군구명": "화순군",
      "index_main": 0.389,
      "배분갭": -4.894,
      "priority_score": 5.283,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.1101827878884675,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 40
    },
    {
      "sgg_codes": [
        "26110"
      ],
      "시도명": "부산광역시",
      "시군구명": "중구",
      "index_main": -0.051,
      "배분갭": -5.304,
      "priority_score": 5.253,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0784794707141242,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 41
    },
    {
      "sgg_codes": [
        "41150"
      ],
      "시도명": "경기도",
      "시군구명": "의정부시",
      "index_main": -0.052,
      "배분갭": -5.301,
      "priority_score": 5.249,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.1445216395701973,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 42
    },
    {
      "sgg_codes": [
        "11590"
      ],
      "시도명": "서울특별시",
      "시군구명": "동작구",
      "index_main": -0.073,
      "배분갭": -5.269,
      "priority_score": 5.196,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0399650489887198,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 43
    },
    {
      "sgg_codes": [
        "11680"
      ],
      "시도명": "서울특별시",
      "시군구명": "강남구",
      "index_main": -0.113,
      "배분갭": -5.206,
      "priority_score": 5.093,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0418316864997707,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 44
    },
    {
      "sgg_codes": [
        "45730"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "무주군",
      "index_main": -0.133,
      "배분갭": -5.174,
      "priority_score": 5.041,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1083540481454376,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 45
    },
    {
      "sgg_codes": [
        "11230"
      ],
      "시도명": "서울특별시",
      "시군구명": "동대문구",
      "index_main": -0.133,
      "배분갭": -5.174,
      "priority_score": 5.041,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0379316579073868,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 46
    },
    {
      "sgg_codes": [
        "11530"
      ],
      "시도명": "서울특별시",
      "시군구명": "구로구",
      "index_main": -0.163,
      "배분갭": -5.126,
      "priority_score": 4.963,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0488833240782056,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 47
    },
    {
      "sgg_codes": [
        "11140"
      ],
      "시도명": "서울특별시",
      "시군구명": "중구",
      "index_main": -0.178,
      "배분갭": -5.103,
      "priority_score": 4.925,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0375974699628611,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 48
    },
    {
      "sgg_codes": [
        "41390"
      ],
      "시도명": "경기도",
      "시군구명": "시흥시",
      "index_main": -0.216,
      "배분갭": -5.043,
      "priority_score": 4.827,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0395921288908022,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 49
    },
    {
      "sgg_codes": [
        "47111",
        "47113"
      ],
      "시도명": "경상북도",
      "시군구명": "포항시",
      "index_main": 0.513,
      "배분갭": -4.302,
      "priority_score": 4.815,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.9985527469505592,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 50
    },
    {
      "sgg_codes": [
        "41190"
      ],
      "시도명": "경기도",
      "시군구명": "부천시",
      "index_main": -0.224,
      "배분갭": -5.03,
      "priority_score": 4.806,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0354833039591835,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 51
    },
    {
      "sgg_codes": [
        "47750"
      ],
      "시도명": "경상북도",
      "시군구명": "청송군",
      "index_main": 0.32,
      "배분갭": -4.484,
      "priority_score": 4.804,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.2473449247907657,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 52
    },
    {
      "sgg_codes": [
        "51150"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "강릉시",
      "index_main": 0.165,
      "배분갭": -4.616,
      "priority_score": 4.781,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0517589593778312,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 53
    },
    {
      "sgg_codes": [
        "30140"
      ],
      "시도명": "대전광역시",
      "시군구명": "중구",
      "index_main": -0.243,
      "배분갭": -5.0,
      "priority_score": 4.757,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0525609568239274,
      "정부지원필요도_시도평균": 3.04,
      "priority_rank": 54
    },
    {
      "sgg_codes": [
        "41410"
      ],
      "시도명": "경기도",
      "시군구명": "군포시",
      "index_main": -0.246,
      "배분갭": -4.995,
      "priority_score": 4.749,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0380069308938226,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 55
    },
    {
      "sgg_codes": [
        "11200"
      ],
      "시도명": "서울특별시",
      "시군구명": "성동구",
      "index_main": -0.246,
      "배분갭": -4.995,
      "priority_score": 4.749,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0371736411303717,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 56
    },
    {
      "sgg_codes": [
        "11350"
      ],
      "시도명": "서울특별시",
      "시군구명": "노원구",
      "index_main": 0.343,
      "배분갭": -4.32,
      "priority_score": 4.663,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.047298516384176,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 57
    },
    {
      "sgg_codes": [
        "46130"
      ],
      "시도명": "전라남도",
      "시군구명": "여수시",
      "index_main": 0.987,
      "배분갭": -3.669,
      "priority_score": 4.656,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9991540537069136,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 58
    },
    {
      "sgg_codes": [
        "51780"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "철원군",
      "index_main": -0.309,
      "배분갭": -4.895,
      "priority_score": 4.586,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0521753290646131,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 59
    },
    {
      "sgg_codes": [
        "47830"
      ],
      "시도명": "경상북도",
      "시군구명": "고령군",
      "index_main": 0.672,
      "배분갭": -3.89,
      "priority_score": 4.562,
      "dominant_domain": "산업기반부족형",
      "recommended_policy": "산업기반·업계 육성 연계 지원",
      "재발위험확률": 0.9988156529432574,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 60
    },
    {
      "sgg_codes": [
        "43760"
      ],
      "시도명": "충청북도",
      "시군구명": "괴산군",
      "index_main": -0.607,
      "배분갭": -5.161,
      "priority_score": 4.554,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.039400981645499,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 61
    },
    {
      "sgg_codes": [
        "46800"
      ],
      "시도명": "전라남도",
      "시군구명": "장흥군",
      "index_main": -0.324,
      "배분갭": -4.872,
      "priority_score": 4.548,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0626907419488683,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 62
    },
    {
      "sgg_codes": [
        "43720"
      ],
      "시도명": "충청북도",
      "시군구명": "보은군",
      "index_main": -0.621,
      "배분갭": -5.139,
      "priority_score": 4.518,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0504471859489639,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 63
    },
    {
      "sgg_codes": [
        "45740"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "장수군",
      "index_main": -0.351,
      "배분갭": -4.829,
      "priority_score": 4.478,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.1372038811935621,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 64
    },
    {
      "sgg_codes": [
        "43770"
      ],
      "시도명": "충청북도",
      "시군구명": "음성군",
      "index_main": -0.699,
      "배분갭": -5.016,
      "priority_score": 4.317,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0397891948126813,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 65
    },
    {
      "sgg_codes": [
        "43150"
      ],
      "시도명": "충청북도",
      "시군구명": "제천시",
      "index_main": -0.708,
      "배분갭": -5.002,
      "priority_score": 4.294,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.830133247900552,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 66
    },
    {
      "sgg_codes": [
        "28140"
      ],
      "시도명": "인천광역시",
      "시군구명": "동구",
      "index_main": -0.445,
      "배분갭": -4.683,
      "priority_score": 4.238,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": null,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 67
    },
    {
      "sgg_codes": [
        "28177"
      ],
      "시도명": "인천광역시",
      "시군구명": "미추홀구",
      "index_main": -0.451,
      "배분갭": -4.674,
      "priority_score": 4.223,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0324870908024116,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 68
    },
    {
      "sgg_codes": [
        "46720"
      ],
      "시도명": "전라남도",
      "시군구명": "곡성군",
      "index_main": 0.356,
      "배분갭": -3.831,
      "priority_score": 4.187,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.3947913227500295,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 69
    },
    {
      "sgg_codes": [
        "41290"
      ],
      "시도명": "경기도",
      "시군구명": "과천시",
      "index_main": 0.219,
      "배분갭": -3.841,
      "priority_score": 4.06,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.076153278014111,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 70
    },
    {
      "sgg_codes": [
        "51190"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "태백시",
      "index_main": -0.52,
      "배분갭": -4.563,
      "priority_score": 4.043,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0453187033877918,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 71
    },
    {
      "sgg_codes": [
        "41281",
        "41285",
        "41287"
      ],
      "시도명": "경기도",
      "시군구명": "고양시",
      "index_main": -0.527,
      "배분갭": -4.551,
      "priority_score": 4.024,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0320381216368013,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 72
    },
    {
      "sgg_codes": [
        "47840"
      ],
      "시도명": "경상북도",
      "시군구명": "성주군",
      "index_main": -0.161,
      "배분갭": -4.133,
      "priority_score": 3.972,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9983415214450844,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 73
    },
    {
      "sgg_codes": [
        "45800"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "부안군",
      "index_main": 0.401,
      "배분갭": -3.439,
      "priority_score": 3.84,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.2507205709648076,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 74
    },
    {
      "sgg_codes": [
        "51800"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "양구군",
      "index_main": -0.001,
      "배분갭": -3.827,
      "priority_score": 3.826,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0433982711312118,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 75
    },
    {
      "sgg_codes": [
        "45720"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "진안군",
      "index_main": -0.608,
      "배분갭": -4.424,
      "priority_score": 3.816,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0588079472160303,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 76
    },
    {
      "sgg_codes": [
        "51760"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "평창군",
      "index_main": -0.623,
      "배분갭": -4.399,
      "priority_score": 3.776,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0398642698883932,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 77
    },
    {
      "sgg_codes": [
        "51730"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "횡성군",
      "index_main": -0.191,
      "배분갭": -3.892,
      "priority_score": 3.701,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8379168200066949,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 78
    },
    {
      "sgg_codes": [
        "41570"
      ],
      "시도명": "경기도",
      "시군구명": "김포시",
      "index_main": -0.691,
      "배분갭": -4.292,
      "priority_score": 3.601,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0298037689914561,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 79
    },
    {
      "sgg_codes": [
        "47210"
      ],
      "시도명": "경상북도",
      "시군구명": "영주시",
      "index_main": -0.132,
      "배분갭": -3.72,
      "priority_score": 3.588,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9951486209868844,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 80
    },
    {
      "sgg_codes": [
        "11500"
      ],
      "시도명": "서울특별시",
      "시군구명": "강서구",
      "index_main": -0.088,
      "배분갭": -3.666,
      "priority_score": 3.578,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0357629148962155,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 81
    },
    {
      "sgg_codes": [
        "47730"
      ],
      "시도명": "경상북도",
      "시군구명": "의성군",
      "index_main": 0.437,
      "배분갭": -3.133,
      "priority_score": 3.57,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9979438361040288,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 82
    },
    {
      "sgg_codes": [
        "47250"
      ],
      "시도명": "경상북도",
      "시군구명": "상주시",
      "index_main": -0.133,
      "배분갭": -3.655,
      "priority_score": 3.522,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9983517567727164,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 83
    },
    {
      "sgg_codes": [
        "45710"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "완주군",
      "index_main": -0.229,
      "배분갭": -3.72,
      "priority_score": 3.491,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1000915906172716,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 84
    },
    {
      "sgg_codes": [
        "51830"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "양양군",
      "index_main": 0.65,
      "배분갭": -2.796,
      "priority_score": 3.446,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1838216599763442,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 85
    },
    {
      "sgg_codes": [
        "11470"
      ],
      "시도명": "서울특별시",
      "시군구명": "양천구",
      "index_main": -0.178,
      "배분갭": -3.412,
      "priority_score": 3.234,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0352755662022212,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 86
    },
    {
      "sgg_codes": [
        "47930"
      ],
      "시도명": "경상북도",
      "시군구명": "울진군",
      "index_main": 0.843,
      "배분갭": -2.367,
      "priority_score": 3.21,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.2674205115596284,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 87
    },
    {
      "sgg_codes": [
        "45190"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "남원시",
      "index_main": 0.094,
      "배분갭": -3.077,
      "priority_score": 3.171,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.3054656627505479,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 88
    },
    {
      "sgg_codes": [
        "47150"
      ],
      "시도명": "경상북도",
      "시군구명": "김천시",
      "index_main": -0.366,
      "배분갭": -3.433,
      "priority_score": 3.067,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9984134346785524,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 89
    },
    {
      "sgg_codes": [
        "11740"
      ],
      "시도명": "서울특별시",
      "시군구명": "강동구",
      "index_main": -0.117,
      "배분갭": -3.147,
      "priority_score": 3.03,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0347837132459948,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 90
    },
    {
      "sgg_codes": [
        "44200"
      ],
      "시도명": "충청남도",
      "시군구명": "아산시",
      "index_main": -0.546,
      "배분갭": -3.338,
      "priority_score": 2.792,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0573384767808195,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 91
    },
    {
      "sgg_codes": [
        "29155"
      ],
      "시도명": "광주광역시",
      "시군구명": "남구",
      "index_main": 0.1,
      "배분갭": -2.414,
      "priority_score": 2.514,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.2909342299833529,
      "정부지원필요도_시도평균": 3.18,
      "priority_rank": 92
    },
    {
      "sgg_codes": [
        "47280"
      ],
      "시도명": "경상북도",
      "시군구명": "문경시",
      "index_main": -0.204,
      "배분갭": -2.547,
      "priority_score": 2.343,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.1252909041104443,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 93
    },
    {
      "sgg_codes": [
        "43130"
      ],
      "시도명": "충청북도",
      "시군구명": "충주시",
      "index_main": -1.103,
      "배분갭": -3.014,
      "priority_score": 1.911,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0599369818689628,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 94
    },
    {
      "sgg_codes": [
        "43730"
      ],
      "시도명": "충청북도",
      "시군구명": "옥천군",
      "index_main": -1.125,
      "배분갭": -2.969,
      "priority_score": 1.844,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0708401279272,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 95
    },
    {
      "sgg_codes": [
        "11410"
      ],
      "시도명": "서울특별시",
      "시군구명": "서대문구",
      "index_main": 0.086,
      "배분갭": -1.732,
      "priority_score": 1.818,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0343834989994791,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 96
    },
    {
      "sgg_codes": [
        "41111",
        "41113",
        "41115",
        "41117"
      ],
      "시도명": "경기도",
      "시군구명": "수원시",
      "index_main": -0.061,
      "배분갭": -1.847,
      "priority_score": 1.786,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0814359396488376,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 97
    },
    {
      "sgg_codes": [
        "44270"
      ],
      "시도명": "충청남도",
      "시군구명": "당진시",
      "index_main": -0.338,
      "배분갭": -2.065,
      "priority_score": 1.727,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0588862284429978,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 98
    },
    {
      "sgg_codes": [
        "11545"
      ],
      "시도명": "서울특별시",
      "시군구명": "금천구",
      "index_main": -0.111,
      "배분갭": -1.803,
      "priority_score": 1.692,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0330675364046486,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 99
    },
    {
      "sgg_codes": [
        "44800"
      ],
      "시도명": "충청남도",
      "시군구명": "홍성군",
      "index_main": 0.088,
      "배분갭": -1.363,
      "priority_score": 1.451,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0717605509051437,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 100
    },
    {
      "sgg_codes": [
        "26470"
      ],
      "시도명": "부산광역시",
      "시군구명": "연제구",
      "index_main": 0.316,
      "배분갭": -1.025,
      "priority_score": 1.341,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0974217459060877,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 101
    },
    {
      "sgg_codes": [
        "28237"
      ],
      "시도명": "인천광역시",
      "시군구명": "부평구",
      "index_main": -0.299,
      "배분갭": -1.489,
      "priority_score": 1.19,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0292562248621224,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 102
    },
    {
      "sgg_codes": [
        "26350"
      ],
      "시도명": "부산광역시",
      "시군구명": "해운대구",
      "index_main": 1.174,
      "배분갭": 0.118,
      "priority_score": 1.056,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9991791124902047,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 103
    },
    {
      "sgg_codes": [
        "51810"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "인제군",
      "index_main": 0.014,
      "배분갭": -0.918,
      "priority_score": 0.932,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.2236443232230505,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 104
    },
    {
      "sgg_codes": [
        "51720"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "홍천군",
      "index_main": -0.294,
      "배분갭": -1.215,
      "priority_score": 0.921,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.996269064145502,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 105
    },
    {
      "sgg_codes": [
        "11440"
      ],
      "시도명": "서울특별시",
      "시군구명": "마포구",
      "index_main": -0.255,
      "배분갭": -1.022,
      "priority_score": 0.767,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.030213325185748,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 106
    },
    {
      "sgg_codes": [
        "46150"
      ],
      "시도명": "전라남도",
      "시군구명": "순천시",
      "index_main": -0.039,
      "배분갭": -0.799,
      "priority_score": 0.76,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9984034433612996,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 107
    },
    {
      "sgg_codes": [
        "46770"
      ],
      "시도명": "전라남도",
      "시군구명": "고흥군",
      "index_main": 0.431,
      "배분갭": -0.282,
      "priority_score": 0.713,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.2502015799849271,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 108
    },
    {
      "sgg_codes": [
        "47290"
      ],
      "시도명": "경상북도",
      "시군구명": "경산시",
      "index_main": 0.213,
      "배분갭": -0.007,
      "priority_score": 0.22,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.8801387434151626,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 109
    },
    {
      "sgg_codes": [
        "48870"
      ],
      "시도명": "경상남도",
      "시군구명": "함양군",
      "index_main": 0.019,
      "배분갭": -0.144,
      "priority_score": 0.163,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.4898150176693833,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 110
    },
    {
      "sgg_codes": [
        "28110"
      ],
      "시도명": "인천광역시",
      "시군구명": "중구",
      "index_main": -0.054,
      "배분갭": -0.071,
      "priority_score": 0.017,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0485615925845534,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 111
    },
    {
      "sgg_codes": [
        "11710"
      ],
      "시도명": "서울특별시",
      "시군구명": "송파구",
      "index_main": -0.356,
      "배분갭": -0.286,
      "priority_score": -0.07,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0343445839301818,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 112
    },
    {
      "sgg_codes": [
        "26320"
      ],
      "시도명": "부산광역시",
      "시군구명": "북구",
      "index_main": 0.795,
      "배분갭": 0.991,
      "priority_score": -0.196,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9884663352284154,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 113
    },
    {
      "sgg_codes": [
        "48890"
      ],
      "시도명": "경상남도",
      "시군구명": "합천군",
      "index_main": 0.797,
      "배분갭": 1.153,
      "priority_score": -0.356,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9696044573250828,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 114
    },
    {
      "sgg_codes": [
        "11320"
      ],
      "시도명": "서울특별시",
      "시군구명": "도봉구",
      "index_main": -0.196,
      "배분갭": 0.225,
      "priority_score": -0.421,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0491243055001932,
      "정부지원필요도_시도평균": 3.01,
      "priority_rank": 115
    },
    {
      "sgg_codes": [
        "47770"
      ],
      "시도명": "경상북도",
      "시군구명": "영덕군",
      "index_main": 0.49,
      "배분갭": 0.955,
      "priority_score": -0.465,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9989692041452908,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 116
    },
    {
      "sgg_codes": [
        "45770"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "순창군",
      "index_main": 0.134,
      "배분갭": 0.599,
      "priority_score": -0.465,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9681454034195568,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 117
    },
    {
      "sgg_codes": [
        "51750"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "영월군",
      "index_main": 0.054,
      "배분갭": 0.539,
      "priority_score": -0.485,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0585580837509927,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 118
    },
    {
      "sgg_codes": [
        "26500"
      ],
      "시도명": "부산광역시",
      "시군구명": "수영구",
      "index_main": 0.304,
      "배분갭": 0.835,
      "priority_score": -0.531,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.3050213565678932,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 119
    },
    {
      "sgg_codes": [
        "48820"
      ],
      "시도명": "경상남도",
      "시군구명": "고성군",
      "index_main": 1.168,
      "배분갭": 1.723,
      "priority_score": -0.555,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.999721986281064,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 120
    },
    {
      "sgg_codes": [
        "48840"
      ],
      "시도명": "경상남도",
      "시군구명": "남해군",
      "index_main": 1.125,
      "배분갭": 1.776,
      "priority_score": -0.651,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9994332830943696,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 121
    },
    {
      "sgg_codes": [
        "48860"
      ],
      "시도명": "경상남도",
      "시군구명": "산청군",
      "index_main": 0.84,
      "배분갭": 1.597,
      "priority_score": -0.757,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9373922814287684,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 122
    },
    {
      "sgg_codes": [
        "51130"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "원주시",
      "index_main": -0.579,
      "배분갭": 0.207,
      "priority_score": -0.786,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9921580603482408,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 123
    },
    {
      "sgg_codes": [
        "44825"
      ],
      "시도명": "충청남도",
      "시군구명": "태안군",
      "index_main": 0.18,
      "배분갭": 1.25,
      "priority_score": -1.07,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.2046424986211147,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 124
    },
    {
      "sgg_codes": [
        "26530"
      ],
      "시도명": "부산광역시",
      "시군구명": "사상구",
      "index_main": 0.563,
      "배분갭": 2.111,
      "priority_score": -1.548,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.2179224313967105,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 125
    },
    {
      "sgg_codes": [
        "47170"
      ],
      "시도명": "경상북도",
      "시군구명": "안동시",
      "index_main": 0.238,
      "배분갭": 1.79,
      "priority_score": -1.552,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9881397372945318,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 126
    },
    {
      "sgg_codes": [
        "46840"
      ],
      "시도명": "전라남도",
      "시군구명": "무안군",
      "index_main": 0.207,
      "배분갭": 2.078,
      "priority_score": -1.871,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9004416201714596,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 127
    },
    {
      "sgg_codes": [
        "48220"
      ],
      "시도명": "경상남도",
      "시군구명": "통영시",
      "index_main": 1.195,
      "배분갭": 3.153,
      "priority_score": -1.958,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9991917730093318,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 128
    },
    {
      "sgg_codes": [
        "26410"
      ],
      "시도명": "부산광역시",
      "시군구명": "금정구",
      "index_main": 0.925,
      "배분갭": 3.017,
      "priority_score": -2.092,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.999082099653286,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 129
    },
    {
      "sgg_codes": [
        "48720"
      ],
      "시도명": "경상남도",
      "시군구명": "의령군",
      "index_main": 0.869,
      "배분갭": 3.01,
      "priority_score": -2.141,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.999140482643391,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 130
    },
    {
      "sgg_codes": [
        "48850"
      ],
      "시도명": "경상남도",
      "시군구명": "하동군",
      "index_main": 0.821,
      "배분갭": 3.064,
      "priority_score": -2.243,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9990869374677624,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 131
    },
    {
      "sgg_codes": [
        "48310"
      ],
      "시도명": "경상남도",
      "시군구명": "거제시",
      "index_main": 1.063,
      "배분갭": 3.319,
      "priority_score": -2.256,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9997127009525572,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 132
    },
    {
      "sgg_codes": [
        "30110"
      ],
      "시도명": "대전광역시",
      "시군구명": "동구",
      "index_main": -0.409,
      "배분갭": 1.855,
      "priority_score": -2.264,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.034526481462637,
      "정부지원필요도_시도평균": 3.04,
      "priority_rank": 133
    },
    {
      "sgg_codes": [
        "44210"
      ],
      "시도명": "충청남도",
      "시군구명": "서산시",
      "index_main": 0.057,
      "배분갭": 2.327,
      "priority_score": -2.27,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.093159037665068,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 134
    },
    {
      "sgg_codes": [
        "26260"
      ],
      "시도명": "부산광역시",
      "시군구명": "동래구",
      "index_main": 0.424,
      "배분갭": 2.743,
      "priority_score": -2.319,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1166592957646729,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 135
    },
    {
      "sgg_codes": [
        "43800"
      ],
      "시도명": "충청북도",
      "시군구명": "단양군",
      "index_main": -0.323,
      "배분갭": 2.083,
      "priority_score": -2.406,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.8671219151549692,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 136
    },
    {
      "sgg_codes": [
        "28260"
      ],
      "시도명": "인천광역시",
      "시군구명": "서구",
      "index_main": -0.339,
      "배분갭": 2.119,
      "priority_score": -2.458,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0417241932681693,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 137
    },
    {
      "sgg_codes": [
        "26170"
      ],
      "시도명": "부산광역시",
      "시군구명": "동구",
      "index_main": 0.363,
      "배분갭": 2.899,
      "priority_score": -2.536,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0924416575544628,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 138
    },
    {
      "sgg_codes": [
        "48880"
      ],
      "시도명": "경상남도",
      "시군구명": "거창군",
      "index_main": -0.117,
      "배분갭": 2.598,
      "priority_score": -2.715,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.3819352442835323,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 139
    },
    {
      "sgg_codes": [
        "47920"
      ],
      "시도명": "경상북도",
      "시군구명": "봉화군",
      "index_main": -0.171,
      "배분갭": 2.629,
      "priority_score": -2.8,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.1720186767060995,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 140
    },
    {
      "sgg_codes": [
        "26710"
      ],
      "시도명": "부산광역시",
      "시군구명": "기장군",
      "index_main": 0.709,
      "배분갭": 3.616,
      "priority_score": -2.907,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9996582514157792,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 141
    },
    {
      "sgg_codes": [
        "26440"
      ],
      "시도명": "부산광역시",
      "시군구명": "강서구",
      "index_main": 0.23,
      "배분갭": 3.218,
      "priority_score": -2.988,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9870533728641664,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 142
    },
    {
      "sgg_codes": [
        "47900"
      ],
      "시도명": "경상북도",
      "시군구명": "예천군",
      "index_main": -0.601,
      "배분갭": 2.444,
      "priority_score": -3.045,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.5019537180441745,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 143
    },
    {
      "sgg_codes": [
        "26140"
      ],
      "시도명": "부산광역시",
      "시군구명": "서구",
      "index_main": 0.383,
      "배분갭": 3.489,
      "priority_score": -3.106,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.7809367442484133,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 144
    },
    {
      "sgg_codes": [
        "30200"
      ],
      "시도명": "대전광역시",
      "시군구명": "유성구",
      "index_main": -0.165,
      "배분갭": 2.958,
      "priority_score": -3.123,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1931301122289972,
      "정부지원필요도_시도평균": 3.04,
      "priority_rank": 145
    },
    {
      "sgg_codes": [
        "47850"
      ],
      "시도명": "경상북도",
      "시군구명": "칠곡군",
      "index_main": -0.181,
      "배분갭": 2.945,
      "priority_score": -3.126,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9989034022974782,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 146
    },
    {
      "sgg_codes": [
        "48740"
      ],
      "시도명": "경상남도",
      "시군구명": "창녕군",
      "index_main": 0.536,
      "배분갭": 3.781,
      "priority_score": -3.245,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9988663643022644,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 147
    },
    {
      "sgg_codes": [
        "48240"
      ],
      "시도명": "경상남도",
      "시군구명": "사천시",
      "index_main": 0.705,
      "배분갭": 3.965,
      "priority_score": -3.26,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.99907459295973,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 148
    },
    {
      "sgg_codes": [
        "51770"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "정선군",
      "index_main": -0.191,
      "배분갭": 3.084,
      "priority_score": -3.275,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8501285937742304,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 149
    },
    {
      "sgg_codes": [
        "45180"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "정읍시",
      "index_main": -0.015,
      "배분갭": 3.283,
      "priority_score": -3.298,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.8971044055034328,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 150
    },
    {
      "sgg_codes": [
        "26230"
      ],
      "시도명": "부산광역시",
      "시군구명": "부산진구",
      "index_main": 0.305,
      "배분갭": 3.636,
      "priority_score": -3.331,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.967233739805046,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 151
    },
    {
      "sgg_codes": [
        "26380"
      ],
      "시도명": "부산광역시",
      "시군구명": "사하구",
      "index_main": 0.413,
      "배분갭": 3.888,
      "priority_score": -3.475,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9569332868732306,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 152
    },
    {
      "sgg_codes": [
        "47820"
      ],
      "시도명": "경상북도",
      "시군구명": "청도군",
      "index_main": -0.176,
      "배분갭": 3.367,
      "priority_score": -3.543,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9992569730119416,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 153
    },
    {
      "sgg_codes": [
        "44180"
      ],
      "시도명": "충청남도",
      "시군구명": "보령시",
      "index_main": -0.156,
      "배분갭": 3.44,
      "priority_score": -3.596,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8414196193268991,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 154
    },
    {
      "sgg_codes": [
        "43750"
      ],
      "시도명": "충청북도",
      "시군구명": "진천군",
      "index_main": -1.182,
      "배분갭": 2.525,
      "priority_score": -3.707,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0572841282076565,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 155
    },
    {
      "sgg_codes": [
        "48170"
      ],
      "시도명": "경상남도",
      "시군구명": "진주시",
      "index_main": 0.624,
      "배분갭": 4.371,
      "priority_score": -3.747,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9992787821709672,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 156
    },
    {
      "sgg_codes": [
        "47130"
      ],
      "시도명": "경상북도",
      "시군구명": "경주시",
      "index_main": 0.137,
      "배분갭": 3.9,
      "priority_score": -3.763,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9998038627868544,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 157
    },
    {
      "sgg_codes": [
        "47230"
      ],
      "시도명": "경상북도",
      "시군구명": "영천시",
      "index_main": -0.345,
      "배분갭": 3.429,
      "priority_score": -3.774,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.998606496244018,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 158
    },
    {
      "sgg_codes": [
        "26290"
      ],
      "시도명": "부산광역시",
      "시군구명": "남구",
      "index_main": 0.503,
      "배분갭": 4.28,
      "priority_score": -3.777,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9417985566756744,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 159
    },
    {
      "sgg_codes": [
        "27260"
      ],
      "시도명": "대구광역시",
      "시군구명": "수성구",
      "index_main": 0.258,
      "배분갭": 4.124,
      "priority_score": -3.866,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.70157432089704,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 160
    },
    {
      "sgg_codes": [
        "46880"
      ],
      "시도명": "전라남도",
      "시군구명": "장성군",
      "index_main": -0.238,
      "배분갭": 3.656,
      "priority_score": -3.894,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.2531548475582951,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 161
    },
    {
      "sgg_codes": [
        "29200"
      ],
      "시도명": "광주광역시",
      "시군구명": "광산구",
      "index_main": -0.014,
      "배분갭": 3.9,
      "priority_score": -3.914,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.4618850755593797,
      "정부지원필요도_시도평균": 3.18,
      "priority_rank": 162
    },
    {
      "sgg_codes": [
        "48730"
      ],
      "시도명": "경상남도",
      "시군구명": "함안군",
      "index_main": 0.339,
      "배분갭": 4.274,
      "priority_score": -3.935,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9992198128345404,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 163
    },
    {
      "sgg_codes": [
        "51110"
      ],
      "시도명": "강원특별자치도",
      "시군구명": "춘천시",
      "index_main": -0.476,
      "배분갭": 3.598,
      "priority_score": -4.074,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9034420091033942,
      "정부지원필요도_시도평균": 2.81,
      "priority_rank": 164
    },
    {
      "sgg_codes": [
        "46230"
      ],
      "시도명": "전라남도",
      "시군구명": "광양시",
      "index_main": 0.441,
      "배분갭": 4.6,
      "priority_score": -4.159,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9987863146138496,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 165
    },
    {
      "sgg_codes": [
        "48330"
      ],
      "시도명": "경상남도",
      "시군구명": "양산시",
      "index_main": 0.31,
      "배분갭": 4.533,
      "priority_score": -4.223,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.999623011484716,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 166
    },
    {
      "sgg_codes": [
        "43740"
      ],
      "시도명": "충청북도",
      "시군구명": "영동군",
      "index_main": -1.222,
      "배분갭": 3.031,
      "priority_score": -4.253,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.7532612561043003,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 167
    },
    {
      "sgg_codes": [
        "44250"
      ],
      "시도명": "충청남도",
      "시군구명": "계룡시",
      "index_main": -0.01,
      "배분갭": 4.299,
      "priority_score": -4.309,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0550641343510225,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 168
    },
    {
      "sgg_codes": [
        "48121",
        "48123",
        "48125",
        "48127",
        "48129"
      ],
      "시도명": "경상남도",
      "시군구명": "창원시",
      "index_main": 0.345,
      "배분갭": 4.742,
      "priority_score": -4.397,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9990626770008968,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 169
    },
    {
      "sgg_codes": [
        "26200"
      ],
      "시도명": "부산광역시",
      "시군구명": "영도구",
      "index_main": 0.583,
      "배분갭": 5.037,
      "priority_score": -4.454,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9334365713053684,
      "정부지원필요도_시도평균": 2.97,
      "priority_rank": 170
    },
    {
      "sgg_codes": [
        "27710"
      ],
      "시도명": "대구광역시",
      "시군구명": "달성군",
      "index_main": 0.534,
      "배분갭": 5.118,
      "priority_score": -4.584,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9987700730423816,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 171
    },
    {
      "sgg_codes": [
        "48270"
      ],
      "시도명": "경상남도",
      "시군구명": "밀양시",
      "index_main": 0.575,
      "배분갭": 5.204,
      "priority_score": -4.629,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9995356924883472,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 172
    },
    {
      "sgg_codes": [
        "30170"
      ],
      "시도명": "대전광역시",
      "시군구명": "서구",
      "index_main": -0.454,
      "배분갭": 4.244,
      "priority_score": -4.698,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0430768807196381,
      "정부지원필요도_시도평균": 3.04,
      "priority_rank": 173
    },
    {
      "sgg_codes": [
        "44770"
      ],
      "시도명": "충청남도",
      "시군구명": "서천군",
      "index_main": -0.192,
      "배분갭": 4.6,
      "priority_score": -4.792,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.4292758989757583,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 174
    },
    {
      "sgg_codes": [
        "46780"
      ],
      "시도명": "전라남도",
      "시군구명": "보성군",
      "index_main": -0.198,
      "배분갭": 4.688,
      "priority_score": -4.886,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8923798639268581,
      "정부지원필요도_시도평균": 2.88,
      "priority_rank": 175
    },
    {
      "sgg_codes": [
        "44150"
      ],
      "시도명": "충청남도",
      "시군구명": "공주시",
      "index_main": -0.634,
      "배분갭": 4.307,
      "priority_score": -4.941,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.0581929985285505,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 176
    },
    {
      "sgg_codes": [
        "48250"
      ],
      "시도명": "경상남도",
      "시군구명": "김해시",
      "index_main": 0.315,
      "배분갭": 5.273,
      "priority_score": -4.958,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9991612168288504,
      "정부지원필요도_시도평균": 3.07,
      "priority_rank": 177
    },
    {
      "sgg_codes": [
        "27290"
      ],
      "시도명": "대구광역시",
      "시군구명": "달서구",
      "index_main": 0.183,
      "배분갭": 5.158,
      "priority_score": -4.975,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9980073883589602,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 178
    },
    {
      "sgg_codes": [
        "41820"
      ],
      "시도명": "경기도",
      "시군구명": "가평군",
      "index_main": -0.279,
      "배분갭": 4.699,
      "priority_score": -4.978,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.997277576366588,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 179
    },
    {
      "sgg_codes": [
        "41670"
      ],
      "시도명": "경기도",
      "시군구명": "여주시",
      "index_main": -0.534,
      "배분갭": 4.56,
      "priority_score": -5.094,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9168813261456916,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 180
    },
    {
      "sgg_codes": [
        "45750"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "임실군",
      "index_main": -0.462,
      "배분갭": 4.7,
      "priority_score": -5.162,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9073771249752576,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 181
    },
    {
      "sgg_codes": [
        "41590"
      ],
      "시도명": "경기도",
      "시군구명": "화성시",
      "index_main": -0.533,
      "배분갭": 4.675,
      "priority_score": -5.208,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.3079521224010855,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 182
    },
    {
      "sgg_codes": [
        "41630"
      ],
      "시도명": "경기도",
      "시군구명": "양주시",
      "index_main": -0.208,
      "배분갭": 5.003,
      "priority_score": -5.211,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.892639390063076,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 183
    },
    {
      "sgg_codes": [
        "45210"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "김제시",
      "index_main": -0.368,
      "배분갭": 4.907,
      "priority_score": -5.275,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.1784094691518919,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 184
    },
    {
      "sgg_codes": [
        "30230"
      ],
      "시도명": "대전광역시",
      "시군구명": "대덕구",
      "index_main": -0.427,
      "배분갭": 4.849,
      "priority_score": -5.276,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0497686504389445,
      "정부지원필요도_시도평균": 3.04,
      "priority_rank": 185
    },
    {
      "sgg_codes": [
        "43111",
        "43112",
        "43113",
        "43114"
      ],
      "시도명": "충청북도",
      "시군구명": "청주시",
      "index_main": -0.975,
      "배분갭": 4.428,
      "priority_score": -5.403,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.7429794145061913,
      "정부지원필요도_시도평균": 3.17,
      "priority_rank": 186
    },
    {
      "sgg_codes": [
        "44710"
      ],
      "시도명": "충청남도",
      "시군구명": "금산군",
      "index_main": -0.445,
      "배분갭": 4.986,
      "priority_score": -5.431,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1736933461660373,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 187
    },
    {
      "sgg_codes": [
        "31170"
      ],
      "시도명": "울산광역시",
      "시군구명": "동구",
      "index_main": 0.485,
      "배분갭": 6.0,
      "priority_score": -5.515,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9999626605515112,
      "정부지원필요도_시도평균": 2.8,
      "priority_rank": 188
    },
    {
      "sgg_codes": [
        "45140"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "익산시",
      "index_main": -0.475,
      "배분갭": 5.059,
      "priority_score": -5.534,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9007255483993422,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 189
    },
    {
      "sgg_codes": [
        "44131",
        "44133"
      ],
      "시도명": "충청남도",
      "시군구명": "천안시",
      "index_main": -1.028,
      "배분갭": 4.718,
      "priority_score": -5.746,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8053889024729091,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 190
    },
    {
      "sgg_codes": [
        "27230"
      ],
      "시도명": "대구광역시",
      "시군구명": "북구",
      "index_main": 0.062,
      "배분갭": 5.821,
      "priority_score": -5.759,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9980295265619116,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 191
    },
    {
      "sgg_codes": [
        "28200"
      ],
      "시도명": "인천광역시",
      "시군구명": "남동구",
      "index_main": -0.423,
      "배분갭": 5.362,
      "priority_score": -5.785,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.033539887728007,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 192
    },
    {
      "sgg_codes": [
        "31200"
      ],
      "시도명": "울산광역시",
      "시군구명": "북구",
      "index_main": 0.481,
      "배분갭": 6.514,
      "priority_score": -6.033,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9999352597602138,
      "정부지원필요도_시도평균": 2.8,
      "priority_rank": 193
    },
    {
      "sgg_codes": [
        "31710"
      ],
      "시도명": "울산광역시",
      "시군구명": "울주군",
      "index_main": 0.149,
      "배분갭": 6.243,
      "priority_score": -6.094,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.999741022363116,
      "정부지원필요도_시도평균": 2.8,
      "priority_rank": 194
    },
    {
      "sgg_codes": [
        "44810"
      ],
      "시도명": "충청남도",
      "시군구명": "예산군",
      "index_main": -0.391,
      "배분갭": 5.729,
      "priority_score": -6.12,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.1207038954317527,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 195
    },
    {
      "sgg_codes": [
        "47190"
      ],
      "시도명": "경상북도",
      "시군구명": "구미시",
      "index_main": -0.167,
      "배분갭": 5.972,
      "priority_score": -6.139,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9976860420449224,
      "정부지원필요도_시도평균": 3.54,
      "priority_rank": 196
    },
    {
      "sgg_codes": [
        "41830"
      ],
      "시도명": "경기도",
      "시군구명": "양평군",
      "index_main": -0.509,
      "배분갭": 5.664,
      "priority_score": -6.173,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9975739145078582,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 197
    },
    {
      "sgg_codes": [
        "31110"
      ],
      "시도명": "울산광역시",
      "시군구명": "중구",
      "index_main": 0.382,
      "배분갭": 6.741,
      "priority_score": -6.359,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9999088781696928,
      "정부지원필요도_시도평균": 2.8,
      "priority_rank": 198
    },
    {
      "sgg_codes": [
        "31140"
      ],
      "시도명": "울산광역시",
      "시군구명": "남구",
      "index_main": -0.25,
      "배분갭": 6.227,
      "priority_score": -6.477,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.999951303342336,
      "정부지원필요도_시도평균": 2.8,
      "priority_rank": 199
    },
    {
      "sgg_codes": [
        "44790"
      ],
      "시도명": "충청남도",
      "시군구명": "청양군",
      "index_main": -0.406,
      "배분갭": 6.087,
      "priority_score": -6.493,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.3390420681356816,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 200
    },
    {
      "sgg_codes": [
        "29140"
      ],
      "시도명": "광주광역시",
      "시군구명": "서구",
      "index_main": -0.298,
      "배분갭": 6.289,
      "priority_score": -6.587,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.3714957406662472,
      "정부지원필요도_시도평균": 3.18,
      "priority_rank": 201
    },
    {
      "sgg_codes": [
        "28245"
      ],
      "시도명": "인천광역시",
      "시군구명": "계양구",
      "index_main": -0.484,
      "배분갭": 6.275,
      "priority_score": -6.759,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0330906789185914,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 202
    },
    {
      "sgg_codes": [
        "41650"
      ],
      "시도명": "경기도",
      "시군구명": "포천시",
      "index_main": -0.439,
      "배분갭": 6.324,
      "priority_score": -6.763,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9967616644286236,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 203
    },
    {
      "sgg_codes": [
        "44230"
      ],
      "시도명": "충청남도",
      "시군구명": "논산시",
      "index_main": -0.629,
      "배분갭": 6.248,
      "priority_score": -6.877,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.7752238874494172,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 204
    },
    {
      "sgg_codes": [
        "28710"
      ],
      "시도명": "인천광역시",
      "시군구명": "강화군",
      "index_main": -0.965,
      "배분갭": 5.927,
      "priority_score": -6.892,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0304819858344458,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 205
    },
    {
      "sgg_codes": [
        "41430"
      ],
      "시도명": "경기도",
      "시군구명": "의왕시",
      "index_main": -0.208,
      "배분갭": 6.723,
      "priority_score": -6.931,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.1161564273839677,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 206
    },
    {
      "sgg_codes": [
        "44760"
      ],
      "시도명": "충청남도",
      "시군구명": "부여군",
      "index_main": -0.548,
      "배분갭": 6.423,
      "priority_score": -6.971,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.8015453580818531,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 207
    },
    {
      "sgg_codes": [
        "41461",
        "41463",
        "41465"
      ],
      "시도명": "경기도",
      "시군구명": "용인시",
      "index_main": -0.384,
      "배분갭": 6.819,
      "priority_score": -7.203,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9979909850799026,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 208
    },
    {
      "sgg_codes": [
        "41250"
      ],
      "시도명": "경기도",
      "시군구명": "동두천시",
      "index_main": -0.115,
      "배분갭": 7.127,
      "priority_score": -7.242,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.8990160289321306,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 209
    },
    {
      "sgg_codes": [
        "28185"
      ],
      "시도명": "인천광역시",
      "시군구명": "연수구",
      "index_main": -0.649,
      "배분갭": 6.662,
      "priority_score": -7.311,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.0307928225677188,
      "정부지원필요도_시도평균": 3.21,
      "priority_rank": 210
    },
    {
      "sgg_codes": [
        "41360"
      ],
      "시도명": "경기도",
      "시군구명": "남양주시",
      "index_main": -0.266,
      "배분갭": 7.383,
      "priority_score": -7.649,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.99813286379692,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 211
    },
    {
      "sgg_codes": [
        "41220"
      ],
      "시도명": "경기도",
      "시군구명": "평택시",
      "index_main": -0.549,
      "배분갭": 7.161,
      "priority_score": -7.71,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.5026695488187393,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 212
    },
    {
      "sgg_codes": [
        "41450"
      ],
      "시도명": "경기도",
      "시군구명": "하남시",
      "index_main": -0.185,
      "배분갭": 7.647,
      "priority_score": -7.832,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9984087675557476,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 213
    },
    {
      "sgg_codes": [
        "45130"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "군산시",
      "index_main": -0.617,
      "배분갭": 7.219,
      "priority_score": -7.836,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.8757784751394667,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 214
    },
    {
      "sgg_codes": [
        "41550"
      ],
      "시도명": "경기도",
      "시군구명": "안성시",
      "index_main": -0.783,
      "배분갭": 7.123,
      "priority_score": -7.906,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.9165020865804596,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 215
    },
    {
      "sgg_codes": [
        "41500"
      ],
      "시도명": "경기도",
      "시군구명": "이천시",
      "index_main": -0.791,
      "배분갭": 7.338,
      "priority_score": -8.129,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9960694797522396,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 216
    },
    {
      "sgg_codes": [
        "41800"
      ],
      "시도명": "경기도",
      "시군구명": "연천군",
      "index_main": -0.55,
      "배분갭": 7.682,
      "priority_score": -8.232,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9948103436677154,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 217
    },
    {
      "sgg_codes": [
        "27170"
      ],
      "시도명": "대구광역시",
      "시군구명": "서구",
      "index_main": -0.425,
      "배분갭": 8.192,
      "priority_score": -8.617,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.997167682140822,
      "정부지원필요도_시도평균": 3.55,
      "priority_rank": 218
    },
    {
      "sgg_codes": [
        "41131",
        "41133",
        "41135"
      ],
      "시도명": "경기도",
      "시군구명": "성남시",
      "index_main": -0.394,
      "배분갭": 8.553,
      "priority_score": -8.947,
      "dominant_domain": "인위적확산-우세형",
      "recommended_policy": "원목유통·도로변 관리(이동경로 차단)",
      "재발위험확률": 0.9976304592079072,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 219
    },
    {
      "sgg_codes": [
        "45111",
        "45113"
      ],
      "시도명": "전북특별자치도",
      "시군구명": "전주시",
      "index_main": -1.122,
      "배분갭": 7.875,
      "priority_score": -8.997,
      "dominant_domain": "노출도-우세형",
      "recommended_policy": "예찰·모니터링 인프라 확충",
      "재발위험확률": 0.1255856125775837,
      "정부지원필요도_시도평균": 2.68,
      "priority_rank": 220
    },
    {
      "sgg_codes": [
        "41480"
      ],
      "시도명": "경기도",
      "시군구명": "파주시",
      "index_main": -0.925,
      "배분갭": 8.582,
      "priority_score": -9.507,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.0812044739599576,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 221
    },
    {
      "sgg_codes": [
        "41610"
      ],
      "시도명": "경기도",
      "시군구명": "광주시",
      "index_main": -0.743,
      "배분갭": 9.182,
      "priority_score": -9.925,
      "dominant_domain": "복합형",
      "recommended_policy": "기본 대응체계·인력 확충",
      "재발위험확률": 0.9960198920952396,
      "정부지원필요도_시도평균": 3.5,
      "priority_rank": 222
    }
  ],
  "policyCatalog": [
    {
      "domain": "노출도-우세형",
      "policy": "예찰·모니터링 인프라 확충",
      "actions": [
        "예찰인력 증원",
        "드론·위성 모니터링 도입",
        "조기발견 신고체계 강화"
      ],
      "trigger": "축A=노출도-우세형 & 축B=부족",
      "evidence": "6차 §9.1 지원패키지 매칭 기준 그대로 적용"
    },
    {
      "domain": "인위적확산-우세형",
      "policy": "원목유통·도로변 관리(이동경로 차단)",
      "actions": [
        "원목생산업체 방제 점검 의무화",
        "도로변 소나무 완충구역 관리",
        "이동통제구역 지정 검토"
      ],
      "trigger": "축A=인위적확산-우세형 & 축B=부족",
      "evidence": "6차 §9.1 지원패키지 매칭 기준 그대로 적용"
    },
    {
      "domain": "복합형",
      "policy": "기본 대응체계·인력 확충",
      "actions": [
        "방제인력 기본 정원 확충",
        "지자체 대응예산 최소 하한선 보장",
        "인접 지자체 공동대응체계 구축"
      ],
      "trigger": "축A=복합형 & 축B=부족",
      "evidence": "6차 §9.1 지원패키지 매칭 기준 그대로 적용"
    },
    {
      "domain": "산업기반부족형",
      "policy": "산업기반·업계 육성 연계 지원",
      "actions": [
        "산림산업 정부지원사업 접근성 개선(홍보·안내 강화)",
        "판로개척·시장개척 지원 연계",
        "원목생산업체 대상 방제 인센티브"
      ],
      "trigger": "취약성지수 상위 & 관할 시도 정부지원필요도 평균 ≥3.2 또는 참여경험 ≤0.5%",
      "evidence": "산림청 『2025년 산림산업조사(2024년 기준)』 표4-63·표4-66 기준"
    }
  ],
  "industryBySido": [
    {
      "시도명": "서울특별시",
      "사업체수": 20615,
      "정부지원필요도_평균": 3.01,
      "애로_국내판매비율": 47.3,
      "참여경험_있음비율": 1.9,
      "희망_판로개척비율": 63.9
    },
    {
      "시도명": "부산광역시",
      "사업체수": 7318,
      "정부지원필요도_평균": 2.97,
      "애로_국내판매비율": 39.2,
      "참여경험_있음비율": 0.0,
      "희망_판로개척비율": 45.7
    },
    {
      "시도명": "대구광역시",
      "사업체수": 5331,
      "정부지원필요도_평균": 3.55,
      "애로_국내판매비율": 82.3,
      "참여경험_있음비율": 0.1,
      "희망_판로개척비율": 95.1
    },
    {
      "시도명": "인천광역시",
      "사업체수": 4938,
      "정부지원필요도_평균": 3.21,
      "애로_국내판매비율": 46.3,
      "참여경험_있음비율": 0.3,
      "희망_판로개척비율": 57.4
    },
    {
      "시도명": "광주광역시",
      "사업체수": 3839,
      "정부지원필요도_평균": 3.18,
      "애로_국내판매비율": 33.8,
      "참여경험_있음비율": 0.1,
      "희망_판로개척비율": 58.4
    },
    {
      "시도명": "대전광역시",
      "사업체수": 5964,
      "정부지원필요도_평균": 3.04,
      "애로_국내판매비율": 38.3,
      "참여경험_있음비율": 0.4,
      "희망_판로개척비율": 46.0
    },
    {
      "시도명": "울산광역시",
      "사업체수": 2420,
      "정부지원필요도_평균": 2.8,
      "애로_국내판매비율": 14.5,
      "참여경험_있음비율": 0.0,
      "희망_판로개척비율": 43.5
    },
    {
      "시도명": "세종특별자치시",
      "사업체수": 1130,
      "정부지원필요도_평균": 2.87,
      "애로_국내판매비율": 24.1,
      "참여경험_있음비율": 0.8,
      "희망_판로개척비율": 36.7
    },
    {
      "시도명": "경기도",
      "사업체수": 38526,
      "정부지원필요도_평균": 3.5,
      "애로_국내판매비율": 48.6,
      "참여경험_있음비율": 1.7,
      "희망_판로개척비율": 60.7
    },
    {
      "시도명": "강원특별자치도",
      "사업체수": 6751,
      "정부지원필요도_평균": 2.81,
      "애로_국내판매비율": 10.6,
      "참여경험_있음비율": 0.8,
      "희망_판로개척비율": 43.1
    },
    {
      "시도명": "충청북도",
      "사업체수": 7035,
      "정부지원필요도_평균": 3.17,
      "애로_국내판매비율": 43.1,
      "참여경험_있음비율": 2.3,
      "희망_판로개척비율": 50.6
    },
    {
      "시도명": "충청남도",
      "사업체수": 8732,
      "정부지원필요도_평균": 3.21,
      "애로_국내판매비율": 32.2,
      "참여경험_있음비율": 0.2,
      "희망_판로개척비율": 50.9
    },
    {
      "시도명": "전북특별자치도",
      "사업체수": 7775,
      "정부지원필요도_평균": 2.68,
      "애로_국내판매비율": 16.1,
      "참여경험_있음비율": 3.3,
      "희망_판로개척비율": 50.1
    },
    {
      "시도명": "전라남도",
      "사업체수": 8615,
      "정부지원필요도_평균": 2.88,
      "애로_국내판매비율": 15.8,
      "참여경험_있음비율": 0.1,
      "희망_판로개척비율": 52.3
    },
    {
      "시도명": "경상북도",
      "사업체수": 8881,
      "정부지원필요도_평균": 3.54,
      "애로_국내판매비율": 80.2,
      "참여경험_있음비율": 0.3,
      "희망_판로개척비율": 93.1
    },
    {
      "시도명": "경상남도",
      "사업체수": 10019,
      "정부지원필요도_평균": 3.07,
      "애로_국내판매비율": 29.2,
      "참여경험_있음비율": 0.1,
      "희망_판로개척비율": 62.8
    },
    {
      "시도명": "제주특별자치도",
      "사업체수": 1902,
      "정부지원필요도_평균": 2.28,
      "애로_국내판매비율": 50.5,
      "참여경험_있음비율": 2.4,
      "희망_판로개척비율": 56.9
    }
  ],
  "feasibilityMatrix": [
    {
      "시도명": "전라남도",
      "시군구명": "완도군",
      "x_취약성": 1.233,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "인천광역시",
      "시군구명": "옹진군",
      "x_취약성": 0.857,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "전라남도",
      "시군구명": "진도군",
      "x_취약성": 0.629,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "전라남도",
      "시군구명": "영광군",
      "x_취약성": 0.559,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "광주광역시",
      "시군구명": "동구",
      "x_취약성": 0.531,
      "y_산업지원필요도": 3.18
    },
    {
      "시도명": "대구광역시",
      "시군구명": "동구",
      "x_취약성": 0.524,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "동해시",
      "x_취약성": 0.489,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "대구광역시",
      "시군구명": "남구",
      "x_취약성": 0.456,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "삼척시",
      "x_취약성": 0.453,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "전라남도",
      "시군구명": "신안군",
      "x_취약성": 0.835,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "속초시",
      "x_취약성": 0.428,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "서울특별시",
      "시군구명": "관악구",
      "x_취약성": 0.4,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전라남도",
      "시군구명": "담양군",
      "x_취약성": 0.384,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "전라남도",
      "시군구명": "구례군",
      "x_취약성": 0.364,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "서울특별시",
      "시군구명": "종로구",
      "x_취약성": 0.359,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "은평구",
      "x_취약성": 0.314,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전라남도",
      "시군구명": "목포시",
      "x_취약성": 0.305,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "고성군",
      "x_취약성": 0.298,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "고창군",
      "x_취약성": 0.262,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "전라남도",
      "시군구명": "함평군",
      "x_취약성": 0.258,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "서울특별시",
      "시군구명": "광진구",
      "x_취약성": 0.23,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경기도",
      "시군구명": "안산시",
      "x_취약성": 0.225,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "서울특별시",
      "시군구명": "성북구",
      "x_취약성": 0.221,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경기도",
      "시군구명": "구리시",
      "x_취약성": 0.199,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "서울특별시",
      "시군구명": "강북구",
      "x_취약성": 0.176,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "광주광역시",
      "시군구명": "북구",
      "x_취약성": 0.175,
      "y_산업지원필요도": 3.18
    },
    {
      "시도명": "경상북도",
      "시군구명": "울릉군",
      "x_취약성": 0.086,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전라남도",
      "시군구명": "해남군",
      "x_취약성": 0.156,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "서울특별시",
      "시군구명": "용산구",
      "x_취약성": 0.15,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "중랑구",
      "x_취약성": 0.124,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "충청북도",
      "시군구명": "증평군",
      "x_취약성": -0.222,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "서울특별시",
      "시군구명": "서초구",
      "x_취약성": 0.058,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전라남도",
      "시군구명": "영암군",
      "x_취약성": 0.047,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "전라남도",
      "시군구명": "강진군",
      "x_취약성": 0.024,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경상북도",
      "시군구명": "영양군",
      "x_취약성": 0.577,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전라남도",
      "시군구명": "나주시",
      "x_취약성": 0.012,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경기도",
      "시군구명": "광명시",
      "x_취약성": 0.002,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "화천군",
      "x_취약성": -0.029,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "경기도",
      "시군구명": "오산시",
      "x_취약성": -0.036,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "전라남도",
      "시군구명": "화순군",
      "x_취약성": 0.389,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "부산광역시",
      "시군구명": "중구",
      "x_취약성": -0.051,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경기도",
      "시군구명": "의정부시",
      "x_취약성": -0.052,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "서울특별시",
      "시군구명": "동작구",
      "x_취약성": -0.073,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "강남구",
      "x_취약성": -0.113,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "무주군",
      "x_취약성": -0.133,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "서울특별시",
      "시군구명": "동대문구",
      "x_취약성": -0.133,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "구로구",
      "x_취약성": -0.163,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "중구",
      "x_취약성": -0.178,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경기도",
      "시군구명": "시흥시",
      "x_취약성": -0.216,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경상북도",
      "시군구명": "포항시",
      "x_취약성": 0.513,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경기도",
      "시군구명": "부천시",
      "x_취약성": -0.224,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경상북도",
      "시군구명": "청송군",
      "x_취약성": 0.32,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "강릉시",
      "x_취약성": 0.165,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "대전광역시",
      "시군구명": "중구",
      "x_취약성": -0.243,
      "y_산업지원필요도": 3.04
    },
    {
      "시도명": "경기도",
      "시군구명": "군포시",
      "x_취약성": -0.246,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "서울특별시",
      "시군구명": "성동구",
      "x_취약성": -0.246,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "서울특별시",
      "시군구명": "노원구",
      "x_취약성": 0.343,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전라남도",
      "시군구명": "여수시",
      "x_취약성": 0.987,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "철원군",
      "x_취약성": -0.309,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "경상북도",
      "시군구명": "고령군",
      "x_취약성": 0.672,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "충청북도",
      "시군구명": "괴산군",
      "x_취약성": -0.607,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "전라남도",
      "시군구명": "장흥군",
      "x_취약성": -0.324,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "충청북도",
      "시군구명": "보은군",
      "x_취약성": -0.621,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "장수군",
      "x_취약성": -0.351,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "충청북도",
      "시군구명": "음성군",
      "x_취약성": -0.699,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "충청북도",
      "시군구명": "제천시",
      "x_취약성": -0.708,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "인천광역시",
      "시군구명": "동구",
      "x_취약성": -0.445,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "인천광역시",
      "시군구명": "미추홀구",
      "x_취약성": -0.451,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "전라남도",
      "시군구명": "곡성군",
      "x_취약성": 0.356,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경기도",
      "시군구명": "과천시",
      "x_취약성": 0.219,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "태백시",
      "x_취약성": -0.52,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "경기도",
      "시군구명": "고양시",
      "x_취약성": -0.527,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경상북도",
      "시군구명": "성주군",
      "x_취약성": -0.161,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "부안군",
      "x_취약성": 0.401,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "양구군",
      "x_취약성": -0.001,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "진안군",
      "x_취약성": -0.608,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "평창군",
      "x_취약성": -0.623,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "횡성군",
      "x_취약성": -0.191,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "경기도",
      "시군구명": "김포시",
      "x_취약성": -0.691,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경상북도",
      "시군구명": "영주시",
      "x_취약성": -0.132,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "서울특별시",
      "시군구명": "강서구",
      "x_취약성": -0.088,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경상북도",
      "시군구명": "의성군",
      "x_취약성": 0.437,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경상북도",
      "시군구명": "상주시",
      "x_취약성": -0.133,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "완주군",
      "x_취약성": -0.229,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "양양군",
      "x_취약성": 0.65,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "서울특별시",
      "시군구명": "양천구",
      "x_취약성": -0.178,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경상북도",
      "시군구명": "울진군",
      "x_취약성": 0.843,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "남원시",
      "x_취약성": 0.094,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "경상북도",
      "시군구명": "김천시",
      "x_취약성": -0.366,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "서울특별시",
      "시군구명": "강동구",
      "x_취약성": -0.117,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "충청남도",
      "시군구명": "아산시",
      "x_취약성": -0.546,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "광주광역시",
      "시군구명": "남구",
      "x_취약성": 0.1,
      "y_산업지원필요도": 3.18
    },
    {
      "시도명": "경상북도",
      "시군구명": "문경시",
      "x_취약성": -0.204,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "충청북도",
      "시군구명": "충주시",
      "x_취약성": -1.103,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "충청북도",
      "시군구명": "옥천군",
      "x_취약성": -1.125,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "서울특별시",
      "시군구명": "서대문구",
      "x_취약성": 0.086,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경기도",
      "시군구명": "수원시",
      "x_취약성": -0.061,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "충청남도",
      "시군구명": "당진시",
      "x_취약성": -0.338,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "서울특별시",
      "시군구명": "금천구",
      "x_취약성": -0.111,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "충청남도",
      "시군구명": "홍성군",
      "x_취약성": 0.088,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "부산광역시",
      "시군구명": "연제구",
      "x_취약성": 0.316,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "인천광역시",
      "시군구명": "부평구",
      "x_취약성": -0.299,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "부산광역시",
      "시군구명": "해운대구",
      "x_취약성": 1.174,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "인제군",
      "x_취약성": 0.014,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "홍천군",
      "x_취약성": -0.294,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "서울특별시",
      "시군구명": "마포구",
      "x_취약성": -0.255,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "전라남도",
      "시군구명": "순천시",
      "x_취약성": -0.039,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "전라남도",
      "시군구명": "고흥군",
      "x_취약성": 0.431,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경상북도",
      "시군구명": "경산시",
      "x_취약성": 0.213,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경상남도",
      "시군구명": "함양군",
      "x_취약성": 0.019,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "인천광역시",
      "시군구명": "중구",
      "x_취약성": -0.054,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "서울특별시",
      "시군구명": "송파구",
      "x_취약성": -0.356,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "부산광역시",
      "시군구명": "북구",
      "x_취약성": 0.795,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상남도",
      "시군구명": "합천군",
      "x_취약성": 0.797,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "서울특별시",
      "시군구명": "도봉구",
      "x_취약성": -0.196,
      "y_산업지원필요도": 3.01
    },
    {
      "시도명": "경상북도",
      "시군구명": "영덕군",
      "x_취약성": 0.49,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "순창군",
      "x_취약성": 0.134,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "영월군",
      "x_취약성": 0.054,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "부산광역시",
      "시군구명": "수영구",
      "x_취약성": 0.304,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상남도",
      "시군구명": "고성군",
      "x_취약성": 1.168,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상남도",
      "시군구명": "남해군",
      "x_취약성": 1.125,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상남도",
      "시군구명": "산청군",
      "x_취약성": 0.84,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "원주시",
      "x_취약성": -0.579,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "충청남도",
      "시군구명": "태안군",
      "x_취약성": 0.18,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "부산광역시",
      "시군구명": "사상구",
      "x_취약성": 0.563,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상북도",
      "시군구명": "안동시",
      "x_취약성": 0.238,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "전라남도",
      "시군구명": "무안군",
      "x_취약성": 0.207,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경상남도",
      "시군구명": "통영시",
      "x_취약성": 1.195,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "부산광역시",
      "시군구명": "금정구",
      "x_취약성": 0.925,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상남도",
      "시군구명": "의령군",
      "x_취약성": 0.869,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상남도",
      "시군구명": "하동군",
      "x_취약성": 0.821,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상남도",
      "시군구명": "거제시",
      "x_취약성": 1.063,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "대전광역시",
      "시군구명": "동구",
      "x_취약성": -0.409,
      "y_산업지원필요도": 3.04
    },
    {
      "시도명": "충청남도",
      "시군구명": "서산시",
      "x_취약성": 0.057,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "부산광역시",
      "시군구명": "동래구",
      "x_취약성": 0.424,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "충청북도",
      "시군구명": "단양군",
      "x_취약성": -0.323,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "인천광역시",
      "시군구명": "서구",
      "x_취약성": -0.339,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "부산광역시",
      "시군구명": "동구",
      "x_취약성": 0.363,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상남도",
      "시군구명": "거창군",
      "x_취약성": -0.117,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상북도",
      "시군구명": "봉화군",
      "x_취약성": -0.171,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "부산광역시",
      "시군구명": "기장군",
      "x_취약성": 0.709,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "부산광역시",
      "시군구명": "강서구",
      "x_취약성": 0.23,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상북도",
      "시군구명": "예천군",
      "x_취약성": -0.601,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "부산광역시",
      "시군구명": "서구",
      "x_취약성": 0.383,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "대전광역시",
      "시군구명": "유성구",
      "x_취약성": -0.165,
      "y_산업지원필요도": 3.04
    },
    {
      "시도명": "경상북도",
      "시군구명": "칠곡군",
      "x_취약성": -0.181,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경상남도",
      "시군구명": "창녕군",
      "x_취약성": 0.536,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상남도",
      "시군구명": "사천시",
      "x_취약성": 0.705,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "정선군",
      "x_취약성": -0.191,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "정읍시",
      "x_취약성": -0.015,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "부산광역시",
      "시군구명": "부산진구",
      "x_취약성": 0.305,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "부산광역시",
      "시군구명": "사하구",
      "x_취약성": 0.413,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "경상북도",
      "시군구명": "청도군",
      "x_취약성": -0.176,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "충청남도",
      "시군구명": "보령시",
      "x_취약성": -0.156,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "충청북도",
      "시군구명": "진천군",
      "x_취약성": -1.182,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "경상남도",
      "시군구명": "진주시",
      "x_취약성": 0.624,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "경상북도",
      "시군구명": "경주시",
      "x_취약성": 0.137,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경상북도",
      "시군구명": "영천시",
      "x_취약성": -0.345,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "부산광역시",
      "시군구명": "남구",
      "x_취약성": 0.503,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "대구광역시",
      "시군구명": "수성구",
      "x_취약성": 0.258,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "전라남도",
      "시군구명": "장성군",
      "x_취약성": -0.238,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "광주광역시",
      "시군구명": "광산구",
      "x_취약성": -0.014,
      "y_산업지원필요도": 3.18
    },
    {
      "시도명": "경상남도",
      "시군구명": "함안군",
      "x_취약성": 0.339,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "강원특별자치도",
      "시군구명": "춘천시",
      "x_취약성": -0.476,
      "y_산업지원필요도": 2.81
    },
    {
      "시도명": "전라남도",
      "시군구명": "광양시",
      "x_취약성": 0.441,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "경상남도",
      "시군구명": "양산시",
      "x_취약성": 0.31,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "충청북도",
      "시군구명": "영동군",
      "x_취약성": -1.222,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "충청남도",
      "시군구명": "계룡시",
      "x_취약성": -0.01,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경상남도",
      "시군구명": "창원시",
      "x_취약성": 0.345,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "부산광역시",
      "시군구명": "영도구",
      "x_취약성": 0.583,
      "y_산업지원필요도": 2.97
    },
    {
      "시도명": "대구광역시",
      "시군구명": "달성군",
      "x_취약성": 0.534,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "경상남도",
      "시군구명": "밀양시",
      "x_취약성": 0.575,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "대전광역시",
      "시군구명": "서구",
      "x_취약성": -0.454,
      "y_산업지원필요도": 3.04
    },
    {
      "시도명": "충청남도",
      "시군구명": "서천군",
      "x_취약성": -0.192,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "전라남도",
      "시군구명": "보성군",
      "x_취약성": -0.198,
      "y_산업지원필요도": 2.88
    },
    {
      "시도명": "충청남도",
      "시군구명": "공주시",
      "x_취약성": -0.634,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경상남도",
      "시군구명": "김해시",
      "x_취약성": 0.315,
      "y_산업지원필요도": 3.07
    },
    {
      "시도명": "대구광역시",
      "시군구명": "달서구",
      "x_취약성": 0.183,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "경기도",
      "시군구명": "가평군",
      "x_취약성": -0.279,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "여주시",
      "x_취약성": -0.534,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "임실군",
      "x_취약성": -0.462,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "경기도",
      "시군구명": "화성시",
      "x_취약성": -0.533,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "양주시",
      "x_취약성": -0.208,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "김제시",
      "x_취약성": -0.368,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "대전광역시",
      "시군구명": "대덕구",
      "x_취약성": -0.427,
      "y_산업지원필요도": 3.04
    },
    {
      "시도명": "충청북도",
      "시군구명": "청주시",
      "x_취약성": -0.975,
      "y_산업지원필요도": 3.17
    },
    {
      "시도명": "충청남도",
      "시군구명": "금산군",
      "x_취약성": -0.445,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "울산광역시",
      "시군구명": "동구",
      "x_취약성": 0.485,
      "y_산업지원필요도": 2.8
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "익산시",
      "x_취약성": -0.475,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "충청남도",
      "시군구명": "천안시",
      "x_취약성": -1.028,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "대구광역시",
      "시군구명": "북구",
      "x_취약성": 0.062,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "인천광역시",
      "시군구명": "남동구",
      "x_취약성": -0.423,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "울산광역시",
      "시군구명": "북구",
      "x_취약성": 0.481,
      "y_산업지원필요도": 2.8
    },
    {
      "시도명": "울산광역시",
      "시군구명": "울주군",
      "x_취약성": 0.149,
      "y_산업지원필요도": 2.8
    },
    {
      "시도명": "충청남도",
      "시군구명": "예산군",
      "x_취약성": -0.391,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경상북도",
      "시군구명": "구미시",
      "x_취약성": -0.167,
      "y_산업지원필요도": 3.54
    },
    {
      "시도명": "경기도",
      "시군구명": "양평군",
      "x_취약성": -0.509,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "울산광역시",
      "시군구명": "중구",
      "x_취약성": 0.382,
      "y_산업지원필요도": 2.8
    },
    {
      "시도명": "울산광역시",
      "시군구명": "남구",
      "x_취약성": -0.25,
      "y_산업지원필요도": 2.8
    },
    {
      "시도명": "충청남도",
      "시군구명": "청양군",
      "x_취약성": -0.406,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "광주광역시",
      "시군구명": "서구",
      "x_취약성": -0.298,
      "y_산업지원필요도": 3.18
    },
    {
      "시도명": "인천광역시",
      "시군구명": "계양구",
      "x_취약성": -0.484,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경기도",
      "시군구명": "포천시",
      "x_취약성": -0.439,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "충청남도",
      "시군구명": "논산시",
      "x_취약성": -0.629,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "인천광역시",
      "시군구명": "강화군",
      "x_취약성": -0.965,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경기도",
      "시군구명": "의왕시",
      "x_취약성": -0.208,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "충청남도",
      "시군구명": "부여군",
      "x_취약성": -0.548,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경기도",
      "시군구명": "용인시",
      "x_취약성": -0.384,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "동두천시",
      "x_취약성": -0.115,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "인천광역시",
      "시군구명": "연수구",
      "x_취약성": -0.649,
      "y_산업지원필요도": 3.21
    },
    {
      "시도명": "경기도",
      "시군구명": "남양주시",
      "x_취약성": -0.266,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "평택시",
      "x_취약성": -0.549,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "하남시",
      "x_취약성": -0.185,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "군산시",
      "x_취약성": -0.617,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "경기도",
      "시군구명": "안성시",
      "x_취약성": -0.783,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "이천시",
      "x_취약성": -0.791,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "연천군",
      "x_취약성": -0.55,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "대구광역시",
      "시군구명": "서구",
      "x_취약성": -0.425,
      "y_산업지원필요도": 3.55
    },
    {
      "시도명": "경기도",
      "시군구명": "성남시",
      "x_취약성": -0.394,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "전북특별자치도",
      "시군구명": "전주시",
      "x_취약성": -1.122,
      "y_산업지원필요도": 2.68
    },
    {
      "시도명": "경기도",
      "시군구명": "파주시",
      "x_취약성": -0.925,
      "y_산업지원필요도": 3.5
    },
    {
      "시도명": "경기도",
      "시군구명": "광주시",
      "x_취약성": -0.743,
      "y_산업지원필요도": 3.5
    }
  ],
  "simulation": {
    "status": "6차 보고서 §9(CH3 연결 — 구조취약성 개선 시나리오)에서 3단계 시나리오(보수/기준/적극)로 이미 수행됨",
    "note": "정책개입 가능 변수(지자체대응역량)를 +0.3/+0.6/+1.0 SD 개선 시 지수가 +0.075/+0.15/+0.25만큼 개선되는 것으로 산식상 계산됨(인과적 피해감소 효과 추정 아님). 부족×긴급도 결합은 위 '단기 경보 결합' 표 참고. 이 대시보드에는 아직 예방형 예산 재배분(5차 water-filling) 시군구별 시뮬레이션 결과가 반영되지 않았다.",
    "underfundedCount": 74,
    "urgentList": [
      {
        "sgg_codes": [
          "47830"
        ],
        "시도명": "경상북도",
        "시군구명": "고령군",
        "index_main": 0.672,
        "배분갭": -3.89,
        "priority_score": 4.562,
        "dominant_domain": "산업기반부족형",
        "recommended_policy": "산업기반·업계 육성 연계 지원",
        "재발위험확률": 0.9988156529432574,
        "정부지원필요도_시도평균": 3.54,
        "priority_rank": 60
      },
      {
        "sgg_codes": [
          "47111",
          "47113"
        ],
        "시도명": "경상북도",
        "시군구명": "포항시",
        "index_main": 0.513,
        "배분갭": -4.302,
        "priority_score": 4.815,
        "dominant_domain": "산업기반부족형",
        "recommended_policy": "산업기반·업계 육성 연계 지원",
        "재발위험확률": 0.9985527469505592,
        "정부지원필요도_시도평균": 3.54,
        "priority_rank": 50
      },
      {
        "sgg_codes": [
          "47840"
        ],
        "시도명": "경상북도",
        "시군구명": "성주군",
        "index_main": -0.161,
        "배분갭": -4.133,
        "priority_score": 3.972,
        "dominant_domain": "노출도-우세형",
        "recommended_policy": "예찰·모니터링 인프라 확충",
        "재발위험확률": 0.9983415214450844,
        "정부지원필요도_시도평균": 3.54,
        "priority_rank": 73
      },
      {
        "sgg_codes": [
          "27140"
        ],
        "시도명": "대구광역시",
        "시군구명": "동구",
        "index_main": 0.524,
        "배분갭": -6.212,
        "priority_score": 6.736,
        "dominant_domain": "산업기반부족형",
        "recommended_policy": "산업기반·업계 육성 연계 지원",
        "재발위험확률": 0.9978548552987484,
        "정부지원필요도_시도평균": 3.55,
        "priority_rank": 6
      },
      {
        "sgg_codes": [
          "51730"
        ],
        "시도명": "강원특별자치도",
        "시군구명": "횡성군",
        "index_main": -0.191,
        "배분갭": -3.892,
        "priority_score": 3.701,
        "dominant_domain": "노출도-우세형",
        "recommended_policy": "예찰·모니터링 인프라 확충",
        "재발위험확률": 0.8379168200066949,
        "정부지원필요도_시도평균": 2.81,
        "priority_rank": 78
      },
      {
        "sgg_codes": [
          "43150"
        ],
        "시도명": "충청북도",
        "시군구명": "제천시",
        "index_main": -0.708,
        "배분갭": -5.002,
        "priority_score": 4.294,
        "dominant_domain": "노출도-우세형",
        "recommended_policy": "예찰·모니터링 인프라 확충",
        "재발위험확률": 0.830133247900552,
        "정부지원필요도_시도평균": 3.17,
        "priority_rank": 66
      }
    ]
  }
};