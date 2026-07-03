'''
IMF에서 제공하는 국가별 GDP를 구하세요. (https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29)
국가별 GDP를 확인할 수 있는 테이블을 만드세요.
해당 테이블에는 GDP가 높은 국가들이 먼저 나와야 합니다.
GDP의 단위는 1B USD이어야 하고 소수점 2자리까지만 표시해 주세요.
IMF에서 매년 2회 이 자료를 제공하기 때문에 정보가 갱신되더라도 해당 코드를 재사용해서 정보를 얻을 수 있어야 합니다.

화면 출력
GDP가 100B USD이상이 되는 국가만을 구해서 화면에 출력해야 합니다.
각 Region별로 top5 국가의 GDP 평균을 구해서 화면에 출력해야 합니다.
'''
from bs4 import BeautifulSoup
import country_converter as coco
import requests
import pandas as pd
import io
from datetime import datetime
import logging

#모든 rows 출력되도록 설정
pd.set_option('display.max_rows', None)

#중요하지 않은 alert 제거
logging.getLogger('country_converter').setLevel(logging.ERROR)

def log_progress(message):
    """
    ETL 프로세스의 진행 상황을 파일에 기록하는 함수입니다.
    """
    # 요구사항에 맞춘 시간 포맷: Year-Monthname-Day-Hour-Minute-Second
    timestamp_format = '%Y-%B-%d-%H-%M-%S'
    
    # 현재 시간 가져오기 및 포맷팅
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    
    # 'a' 모드로 열어서 기존 내용에 추가(Append)되도록 설정
    with open("etl_project_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp}, {message}\n")

def extract_from_wikipedia(url):
    """
    위키피디아로부터 데이터를 추출하는 함수입니다.
    """

    log_progress("Extract phase Started")
    #헤더 후보 설정
    headers_1 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    headers_2 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}
    try:
        # 첫 번째 헤더로 시도
        response = requests.get(url, headers=headers_1)
    except:
        # 실패하면 두 번째 헤더로 시도
        response = requests.get(url, headers=headers_2)

    # print(response)
    soup = BeautifulSoup(response.text, 'html.parser')

    #현재 페이지에서 table 태그 모두 선택하기
    table = soup.select('table')

    # 판다스의 read_html 로 테이블 정보 읽기
    table_df_list = pd.read_html(io.StringIO(str(table)))

    # 데이터프레임 선택하기
    table_df = table_df_list[2]
    table_df1 = table_df[['Country/Territory', 'IMF (2026)[1]']]

    # 컬럼명 변경
    table_df1 = table_df1.rename(columns={
        'Country/Territory': 'Country',
        'IMF (2026)[1]': 'GDP_USD_billion'
    })

    log_progress("Extract phase Ended")
    return table_df1
    
def load_df_to_json(df):
    """
    데이터프레임을 json파일로 변환하여 저장하는 함수입니다.
    """

    log_progress("Load phase Started")

    # 데이터프레임을 json으로 저장
    df.to_json(
    'Countries_by_GDP.json', 
    orient='records', 
    force_ascii=False, 
    indent=4
    )

    log_progress("Load phase Ended")
   
def transform_df_data(df):
    """
    데이터프레임의 데이터를 정제하고 변환하는 함수입니다.
    """
    log_progress("Transform phase Started")
    df = df[df['Country'] != 'World'].copy()

    # 국가명 정제 (국가명 뒤에 붙어있는 [n 1] 과 같은 내용을 제거)
    df['Country'] = df['Country'].str.replace(r'\[.*?\]', '', regex=True).str.strip()

    # country_converter를 활용하여 대륙 단위 Region 컬럼 생성
    cc = coco.CountryConverter()
    df['Region'] = cc.convert(names=df['Country'].tolist(), to='continent')

    # country_converter로 Region이 지정되지 않은 나라는 수동으로 지정
    df.loc[df['Country'] == 'Zanzibar', 'Region'] = 'Sub-Saharan Africa' 
    df.loc[df['Country'] == 'Channel Islands', 'Region'] = 'Northern Europe'

    # IMF_GDP 컬럼의 쉼표(,)를 제거하고 문자열을 숫자형(Float)으로 변환
    df['GDP_USD_billion'] = df['GDP_USD_billion'].astype(str).str.replace(',', '', regex=True)
    df['GDP_USD_billion'] = pd.to_numeric(df['GDP_USD_billion'], errors='coerce')

    # 결측치(NaN)가 생겼을 경우 해당 row 제거
    df = df.dropna(subset=['GDP_USD_billion'])
    # 1000으로 나누어 단위를 1B 달러로 맞추고 소수점 2자리까지 반올림
    df['GDP_USD_billion'] = (df['GDP_USD_billion'] / 1000).round(2)

    # 'Country' 컬럼의 값이 'World'가 아닌(!=) 행들만 다시 df에 저장
    df = df[df['Country'] != 'World'].copy()

    log_progress("Transform phase Ended")
    return df

def print_gdp_over_100b(df):
    """
    GDP 100B 이상을 출력하는 함수입니다.
    """
    
    # 'IMF_GDP' 컬럼 값이 100 이상인 행만 선택
    gdp_over_100b = df[df['GDP_USD_billion'] >= 0]

    # 상위 국가부터 확인하기 위해 내림차순 정렬 (선택 사항)
    gdp_over_100b = gdp_over_100b.sort_values(by='GDP_USD_billion', ascending=False)

    print("--- GDP 100B USD 이상 국가 목록 ---")
    # 필요한 컬럼만 선택하여 출력
    print(gdp_over_100b[['Country', 'GDP_USD_billion']])

def print_gdp_top5_by_region(df):
    """
    지역별 top5 GDP의 평균을 출력하는 함수입니다.
    """
    print("--- 각 Region별 Top 5 국가의 GDP 평균 (단위: 1B USD) ---")
    
    # 1. Region별로 그룹화한 뒤, IMF_GDP가 가장 큰 5개(nlargest)를 뽑아 평균(mean)을 구합니다.
    top5_avg_series = df.groupby('Region')['GDP_USD_billion'].apply(lambda x: x.nlargest(5).mean())
    
    # 2. 보기 좋게 데이터프레임으로 바꾸고, 내림차순 정렬을 해줍니다.
    top5_avg_df = top5_avg_series.reset_index()
    top5_avg_df.columns = ['Region', 'Top5_Avg_GDP_USD_billion']
    top5_avg_df = top5_avg_df.sort_values(by='Top5_Avg_GDP_USD_billion', ascending=False)
    
    # 3. 소수점 2자리까지 깔끔하게 포맷팅하여 출력
    top5_avg_df['Top5_Avg_GDP_USD_billion'] = top5_avg_df['Top5_Avg_GDP_USD_billion'].round(2)
    
    # 인덱스 번호 없이 깔끔하게 텍스트로 출력합니다.
    print(top5_avg_df.to_string(index=False))

if __name__ == "__main__":
    # 데이터 Extract
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"
    df = extract_from_wikipedia(url)

    # 데이터 Transform
    transformed_df = transform_df_data(df)
    
    # 데이터 Load (Extract한 데이터)
    load_df_to_json(transformed_df)

    # 결과물 출력 
    print_gdp_over_100b(transformed_df)
    print()
    print_gdp_top5_by_region(transformed_df)

