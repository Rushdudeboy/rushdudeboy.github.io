import requests
import pandas as pd
from datetime import datetime
import time

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 타겟 기업 키워드 리스트
        self.target_companies = ["삼성", "SK", "LG", "네이버", "카카오", "토스", "크래프톤"]

    def fetch_targeted_jobs(self):
        results = []
        
        for company_keyword in self.target_companies:
            print(f"[{company_keyword}] 관련 채용공고 수집 중...")
            
            # 원티드 검색 API를 활용하여 각 기업 키워드 검색
            url = f"https://www.wanted.co.kr/api/v4/jobs?country=kr&job_sort=company.response_rate_order&locations=all&years=-1&query={company_keyword}&limit=20"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                for job in data.get('data', []):
                    company_name = job.get('company', {}).get('name', '')
                    
                    # 검색 결과 중 실제 기업명에 타겟 키워드가 포함된 경우만 추출
                    # 예: "삼성전자", "네이버웹툰", "토스뱅크" 등 모두 포함
                    if company_keyword.lower() in company_name.lower():
                        results.append({
                            'target_group': company_keyword,
                            'company_name': company_name,
                            'job_title': job.get('position'),
                            'url': f"https://www.wanted.co.kr/wd/{job.get('id')}",
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                # API 서버 부하를 막기 위해 1초 대기 (GitHub Actions 차단 방지)
                time.sleep(1)
                
            except Exception as e:
                print(f"{company_keyword} 데이터 수집 중 오류 발생: {e}")
                
        return results

if __name__ == "__main__":
    print("지정된 대기업 및 IT/스타트업 채용공고 수집을 시작합니다...")
    scraper = JobScraper()
    jobs_data = scraper.fetch_targeted_jobs()
    
    if jobs_data:
        df = pd.DataFrame(jobs_data)
        
        # GitHub Actions 덮어쓰기용 파일명
        filename = "jobs_data_latest.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"성공적으로 총 {len(df)}건의 데이터를 '{filename}'에 저장했습니다.")
    else:
        print("수집된 데이터가 없습니다.")
