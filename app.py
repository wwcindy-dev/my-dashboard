import streamlit as st  # 화면(웹 페이지)을 만드는 라이브러리
import pandas as pd  # 표(데이터)를 다루는 라이브러리

# 페이지 기본 설정: 브라우저 탭 제목, 화면을 넓게 사용
st.set_page_config(page_title="매출 현황", layout="wide")


DATA_FILE = "sales_sample.csv"  # 불러올 데이터 파일 이름
REQUIRED_COLUMNS = ["date", "region", "category", "sales", "quantity"]  # 꼭 있어야 하는 열

# 화면 맨 위 제목과 캡션(작은 설명 글) - 데이터에 문제가 있어도 제목은 먼저 보이도록 맨 앞에 둠
st.title("영업팀 지역별 매출 현황")
st.caption("데이터 기준: 2026년 1~10월 · 출처: sales_sample.csv")


# 데이터 불러오기 함수
# @st.cache_data: 처음 한 번만 파일을 읽고, 그 뒤로는 기억해 둔 결과를 바로 씀
# (사이드바 조건을 바꿀 때마다 화면 코드가 처음부터 다시 실행되기 때문에 필요)
# 날짜 변환은 열 검사 뒤에 따로 함 (date 열이 없을 때 여기서 오류가 나지 않게)
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE, encoding="utf-8")


# try ~ except: 파일을 읽다가 문제가 생기면 빨간 에러 대신 안내 문구를 보여 줌
# st.stop(): 아래 코드를 더 실행하지 않고 여기서 화면을 멈춤
try:
    df = load_data()
except FileNotFoundError:  # 1) 파일이 없을 때
    st.warning(
        f"데이터 파일 '{DATA_FILE}'을(를) 찾을 수 없습니다. "
        "파일 이름이 맞는지, app.py와 같은 폴더에 있는지, "
        "그 폴더에서 streamlit run app.py를 실행했는지 확인해 주세요."
    )
    st.stop()
except pd.errors.EmptyDataError:  # 파일은 있는데 내용이 비어 있을 때
    st.warning(f"데이터 파일 '{DATA_FILE}'이(가) 비어 있습니다. 내용이 들어 있는 파일로 바꿔 주세요.")
    st.stop()
except UnicodeDecodeError:  # 한글 저장 방식(인코딩)이 다를 때
    st.warning(f"데이터 파일 '{DATA_FILE}'의 한글을 읽을 수 없습니다. 파일을 UTF-8 형식으로 다시 저장해 주세요.")
    st.stop()
except Exception:  # 그 밖에 예상하지 못한 읽기 문제
    st.warning(f"데이터 파일 '{DATA_FILE}'을(를) 읽지 못했습니다. 올바른 CSV 파일인지 확인해 주세요.")
    st.stop()

# 2) 꼭 필요한 열이 모두 있는지 검사: 목록에서 df에 없는 열만 골라 담음
missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
if missing:
    st.warning(
        f"데이터에 꼭 필요한 열이 없습니다: {', '.join(missing)}. "
        "CSV 파일 첫 줄(열 이름)에 이 열을 추가하거나 이름을 맞게 고쳐 주세요."
    )
    st.stop()

# 자료형 바꾸기: errors="coerce"는 바꿀 수 없는 값을 에러 대신 빈칸(NaT/NaN)으로 만듦
df["date"] = pd.to_datetime(df["date"], errors="coerce")  # 글자 → 날짜
df["sales"] = pd.to_numeric(df["sales"], errors="coerce")  # 글자 → 숫자
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

# 빈칸이 하나라도 있는 행은 빼기 (그래프·계산이 깨지지 않게)
bad_rows = df[REQUIRED_COLUMNS].isna().any(axis=1)  # 행마다 빈칸이 있으면 True
df = df[~bad_rows]  # ~는 True/False를 뒤집음 → 빈칸 없는 행만 남김
if bad_rows.sum() > 0:
    st.info(
        f"날짜·숫자가 잘못되었거나 빈칸인 {bad_rows.sum()}건은 빼고 보여 줍니다. "
        "모두 보려면 CSV 파일에서 해당 행을 고쳐 주세요."
    )
if df.empty:  # 쓸 수 있는 행이 하나도 없으면 멈춤
    st.warning("사용할 수 있는 데이터가 한 건도 없습니다. CSV 파일의 날짜와 매출 값을 확인해 주세요.")
    st.stop()

# 왼쪽 사이드바: 지역·카테고리·기간 조건 고르기
st.sidebar.header("조건 선택")

# 1) 지역: 여러 개 선택 가능 (기본값 = 모든 지역)
region_list = sorted(df["region"].unique())  # 지역 이름을 중복 없이 뽑아 가나다순 정렬
selected_regions = st.sidebar.multiselect("지역", region_list, default=region_list)

# 2) 카테고리: 드롭다운에서 하나 고르기 (맨 앞에 '전체' 추가)
category_list = ["전체"] + sorted(df["category"].unique())
selected_category = st.sidebar.selectbox("카테고리", category_list)

# 3) 기간: 시작일~종료일을 고르는 슬라이더
min_date = df["date"].min().date()  # 데이터의 첫 날짜 (.date()는 시간 빼고 날짜만)
max_date = df["date"].max().date()  # 데이터의 마지막 날짜
if min_date == max_date:
    # 데이터가 하루치뿐이면 슬라이더를 만들 수 없으므로(시작=끝) 날짜만 글로 보여 줌
    st.sidebar.write(f"기간: {min_date} (하루치 데이터)")
    start_date, end_date = min_date, max_date
else:
    # value에 (시작, 끝) 두 값을 주면 양쪽 손잡이가 있는 범위 슬라이더가 됨
    start_date, end_date = st.sidebar.slider(
        "기간",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD",  # 슬라이더에 날짜를 보여주는 모양
    )

# 조건에 맞는 행만 골라 filtered 만들기
cond_region = df["region"].isin(selected_regions)  # 고른 지역 목록 안에 있으면 True
if selected_category == "전체":
    cond_category = True  # '전체'면 카테고리 조건 없음 (모두 통과)
else:
    cond_category = df["category"] == selected_category  # 고른 카테고리면 True
dates = df["date"].dt.date  # 비교하려고 날짜만 꺼냄
# between(시작, 끝): 시작 이상 그리고 끝 이하면 True (양 끝 날짜도 포함)
cond_date = dates.between(start_date, end_date)
filtered = df[cond_region & cond_category & cond_date]  # 세 조건 모두 True인 행만

# 필터 아래에 몇 건이 골라졌는지 표시
st.sidebar.write(f"선택 조건: {len(filtered):,}건 / 전체 {len(df):,}건")

# 3) 골라진 데이터가 0건이면 안내만 하고 지표·그래프·표는 그리지 않음 (0으로 나누기 방지)
if filtered.empty:
    st.info(
        "선택한 조건에 맞는 데이터가 없습니다. "
        "조건을 넓혀 보세요: 사이드바에서 지역을 더 고르거나, 카테고리를 '전체'로 바꾸거나, 기간을 늘려 주세요."
    )
    st.stop()

# 본문 탭 두 개 만들기
tab_summary, tab_detail = st.tabs(["요약", "상세 데이터"])

with tab_summary:  # '요약' 탭 안에 들어갈 내용
    # 핵심 숫자 3개 계산
    total_sales = filtered["sales"].sum()  # 총 매출: 매출 열을 모두 더함
    order_count = len(filtered)  # 주문 건수: 행 개수 = 주문 수
    avg_order = total_sales / order_count  # 평균 주문액: 총 매출 ÷ 주문 건수

    # 가로로 3칸 나누기: col1, col2, col3에 하나씩 넣음
    col1, col2, col3 = st.columns(3)
    # st.metric: 큰 글씨로 숫자 카드 보여주기
    # f"{값:,.0f}": 천 단위 쉼표(,)를 넣고 소수점 0자리(.0f)로 반올림
    col1.metric("총 매출", f"{total_sales:,.0f}원")
    col2.metric("주문 건수", f"{order_count:,}건")
    col3.metric("평균 주문액", f"{avg_order:,.0f}원")

    # 그래프 두 개를 가로로 나란히 놓기 위해 2칸으로 나눔
    left, right = st.columns(2)

    with left:  # 왼쪽 칸: 월별 매출 추이
        st.subheader("월별 매출 추이")
        # dt.strftime("%Y-%m"): 날짜를 "2026-01" 같은 월 글자로 바꿈
        month = filtered["date"].dt.strftime("%Y-%m")
        # 같은 월끼리 묶어 매출 합계 → reset_index()로 '월', '매출' 두 열짜리 표로 만듦
        month_sales = filtered.groupby(month)["sales"].sum().reset_index()
        month_sales.columns = ["월", "매출"]  # 열 이름을 한국어로
        # 선 그래프: x축은 월, y축은 매출
        st.line_chart(month_sales, x="월", y="매출", y_label="매출(원)")

    with right:  # 오른쪽 칸: 지역별 매출
        st.subheader("지역별 매출")
        # 지역끼리 묶어 매출 합계 → 표로 만들기
        region_sales = filtered.groupby("region")["sales"].sum().reset_index()
        region_sales.columns = ["지역", "매출"]
        # 막대 그래프: sort="-매출"은 매출 큰 순서(앞의 -가 '큰 값부터')로 막대 정렬
        st.bar_chart(region_sales, x="지역", y="매출", y_label="매출(원)", sort="-매출")

with tab_detail:  # '상세 데이터' 탭 안에 들어갈 내용
    # 조건으로 걸러낸 데이터를 표로 보여주기
    # width="stretch": 표를 화면 폭에 꽉 맞춤 / hide_index=True: 왼쪽 행 번호(0, 1, 2…) 숨김
    st.dataframe(filtered, width="stretch", hide_index=True)
