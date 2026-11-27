import pandas as pd  # 표(데이터) 다루는 라이브러리, pd라는 줄임말로 사용

# CSV 파일을 읽어서 df(데이터프레임 = 표)에 저장
df = pd.read_csv("sales_sample.csv", encoding="utf-8")

# 1. 행·열 개수: shape는 (행 개수, 열 개수) 두 값을 돌려줌
print("=== 1. 행·열 개수 ===")
rows, cols = df.shape  # 두 값을 하나씩 나눠 받기
print(f"행 {rows}개, 열 {cols}개")
print()  # 빈 줄 하나 띄우기

# 2. 열 이름과 자료형: dtypes는 각 열이 숫자인지 글자인지 알려줌
print("=== 2. 열 이름과 자료형 ===")
print(df.dtypes)
print()

# 3. 빈칸 개수: isna()로 빈칸이면 True, sum()으로 True 개수를 열마다 더함
print("=== 3. 열별 빈칸 개수 ===")
print(df.isna().sum())
print()

# 4. 숫자 열 요약: describe()는 숫자 열의 개수·평균·최소·최대 등을 계산
print("=== 4. 숫자 열 요약 ===")
print(df.describe())
print()

# 5. 조건으로 고르기: 서울 지역이면서 매출 10만 원 이상인 주문
print("=== 5. 서울 & 매출 10만 원 이상 주문 ===")
is_seoul = df["region"] == "서울"  # 지역이 서울인지 행마다 True/False
is_big = df["sales"] >= 100000  # 매출이 10만 원 이상인지 행마다 True/False
seoul_big = df[is_seoul & is_big]  # 두 조건이 모두 True인 행만 남기기
print(f"{len(seoul_big)}건")  # len()은 남은 행 개수 = 주문 건수
print()

# 6. 지역별 매출 합계를 큰 순서로
print("=== 6. 지역별 매출 합계 (큰 순서) ===")
region_sales = df.groupby("region")["sales"].sum()  # 지역끼리 묶어서 매출 더하기
region_sales = region_sales.sort_values(ascending=False)  # ascending=False: 큰 값부터
print(region_sales)
print()

# 7. 월별 매출 합계 (1월 → 10월 순서)
print("=== 7. 월별 매출 합계 ===")
df["date"] = pd.to_datetime(df["date"])  # 글자로 읽힌 date를 진짜 날짜로 변환 (.dt 쓰려면 필요)
month = df["date"].dt.month  # 날짜에서 월 숫자(1~12)만 꺼내기
month_sales = df.groupby(month)["sales"].sum()  # 같은 월끼리 묶어서 매출 더하기
print(month_sales)
print()

# 8. 카테고리별 매출 합계를 큰 순서로
print("=== 8. 카테고리별 매출 합계 (큰 순서) ===")
category_sales = df.groupby("category")["sales"].sum()  # 카테고리끼리 묶어서 매출 더하기
category_sales = category_sales.sort_values(ascending=False)  # 큰 값부터 정렬
print(category_sales)
