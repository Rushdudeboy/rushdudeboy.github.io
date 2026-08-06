import requests
import pandas as pd
from datetime import datetime
import time

class Employment24JobScraper:
    def __init__(self):
        # 고용24(워크넷) OpenAPI 인증키 입력
        self.api_key = "여기에_고용24_인증키를_입력하세요"
        self.base_url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo.do" # 고용24 오픈API 표준 호출 엔드포인트
        
        # 타겟 기업 리스트
        self.target_companies = ["삼성", "SK", "LG", "네이버", "카카오", "토스", "크래프톤"]

    def fetch_jobs(self):
        results = []
        
        for company in self.target_companies:
            print(f"[{company}] 고용24 채용공고 수집 중...")
            
            # 고용24 OpenAPI 파라미터 규격
            params = {
                "authKey": self.api_key,
                "callTp": "L",          # L: 목록 조회
                "returnType": "JSON",   # 결과 반환 형식
                "startPage": 1,
                "display": 50,          # 한 페이지에 가져올 건수
                "keyword": company      # 검색 키워드
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    # 응답 데이터 파싱 (고용24 API 구조에 맞춰 조정)
                    contentType = response.headers.get("Content-Type", "")
                    if "application/json" in contentType:
                        data = response.json()
                        jobs = data.get('wanted', [])
                        
                        for job in jobs:
                            company_name = job.get('company', '')
                            
                            # 검색 결과 중 실제 기업명에 타겟 키워드가 포함된 경우만 필터링
                            if company.lower() in company_name.lower():
                                results.append({
                                    'target_group': company,
                                    'company_name': company_name,
                                    'job_title': job.get('title', ''),
                                    'location': job.get('workRegion', ''),
                                    'url': job.get('wantedMobileInfoUrl', job.get('srchWrkStDt', '')), # 모바일/웹 상세 링크
                                    'posted_at': job.get('regDt', ''),
                                    'deadline': job.get('closeDt', ''),
                                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                    else:
                        print(f"❌ {company} API 응답 형식 오류 (XML로 반환되었거나 키가 잘못되었습니다)")
                else:
                    print(f"❌ {company} API 요청 실패 (상태 코드: {response.status_code})")
                
                # 서버 부하 방지 딜레이
                time.sleep(1)
                
            except Exception as e:
                print(f"[{company}] 데이터 수집 중 오류 발생: {e}")
                
        return results

if __name__ == "__main__":
    print("고용24 API 기반 채용공고 수집을 시작합니다...")
    scraper = Employment24JobScraper()
    jobs_data = scraper.fetch_jobs()
    
    if jobs_data:
        df = pd.DataFrame(jobs_data)
        df.drop_duplicates(subset=['company_name', 'job_title'], keep='first', inplace=True)
        
        filename = "jobs_data_latest.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"성공적으로 총 {len(df)}건의 데이터를 '{filename}'에 저장했습니다.")
    else:
        print("수집된 데이터가 없습니다.")