'''
코드를 수정해서 아래 요구사항을 구현하세요.
추출한 데이터를 데이터베이스에 저장하세요. 'Countries_by_GDP'라는 테이블명으로 'World_Economies.db'라는 데이터 베이스에 저장되어야 합니다. 해당 테이블은 'Country', 'GDP_USD_billion'라는 어트리뷰트를 반드시 가져야 합니다.
데이터베이스는 sqlite3 라이브러리를 사용해서 만드세요.
필요한 모든 작업을 수행하는 'etl_project_gdp_with_sql.py' 코드를 작성하세요. (기존 코드와 별도로 2개의 코드를 제출해야 합니다.)

화면 출력
SQL Query를 사용해야 합니다.
GDP가 100B USD이상이 되는 국가만을 구해서 화면에 출력해야 합니다.
각 Region별로 top5 국가의 GDP 평균을 구해서 화면에 출력해야 합니다.
'''

import etl_project_gdp as etl
import pandas as pd
import sqlite3

pd.set_option('display.max_rows', None)

class Database:
    """
    데이터베이스 관련된 클래스 입니다.
    """
    def __init__(self):
        self.conn = sqlite3.connect('World_Economies.db')
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        if self.cursor is not None:
            columns = [desc[0] for desc in self.cursor.description]
            print(" | ".join(columns))
            print("-" * 50)

            for row in rows:
                print(" | ".join(map(str, row)))

    def close(self):
        self.conn.close()

def load_to_db(df):
    """
    데이터프레임을 데이터베이스에 저장하는 함수입니다.
    """

    # 1. Load 단계 시작 로그 기록
    etl.log_progress("Load phase Started")
    
    db_name='World_Economies.db'
    table_name='Countries_by_GDP'
    # 2. SQLite 데이터베이스 파일 연결
    # 파일이 없으면 새로 생성하고, 있으면 연결합니다.
    conn = sqlite3.connect(db_name)
    
    # 3. Pandas의 to_sql을 이용하여 테이블로 적재
    # if_exists='replace': 기존에 동일한 이름의 테이블이 있다면 덮어씁니다.
    # index=False: 불필요한 행 번호(인덱스) 컬럼 생성을 방지합니다.
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 4. 작업 완료 후 안전하게 DB 연결 닫기
    conn.close()

    # 5. Load 단계 종료 로그 기록
    etl.log_progress("Load phase Ended")

def print_with_sql():
    """
    SQL을 활용하여 결과물을 출력하는 함수입니다.
    """
    # 데이터베이스 연결
    db = Database()
    # db.execute("SELECT * FROM Countries_by_GDP")
    print("GDP 100B USD 이상 국가 목록")
    db.execute('SELECT Country, GDP_USD_billion FROM Countries_by_GDP WHERE GDP_USD_billion >= 100 ORDER BY GDP_USD_billion DESC;')

    print()
    print("각 Region별 Top 5 국가의 GDP 평균")
    db.execute('WITH RankedGDP AS (SELECT Region, Country, GDP_USD_billion, ROW_NUMBER() OVER (PARTITION BY Region ORDER BY GDP_USD_billion DESC) as rnk FROM Countries_by_GDP) ' \
    'SELECT Region, ROUND(AVG(GDP_USD_billion), 2) AS Top5_Avg_GDP_USD_billion FROM RankedGDP WHERE rnk <= 5 GROUP BY Region ORDER BY Top5_Avg_GDP_USD_billion DESC;')

# 데이터 Extract
url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"
df = etl.extract_from_wikipedia(url)

# 데이터 Transform
transformed_df = etl.transform_df_data(df)

# 데이터 Load
load_to_db(transformed_df)

# sql을 활용하여 출력
print_with_sql()