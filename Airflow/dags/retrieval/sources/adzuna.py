import requests as r
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.config import adzuna_setting
from common.logger import airflow_logger as logger
from utils.common import get_hash
from utils.models import Job
from load.loader import Loader # retriving all at once taking time for currently loading one by one



# https://api.adzuna.com/v1/api/jobs/in/search/?app_id=&app_key=s&sort_by=date&max_days_old=1
"""
{
      "description": "vCommission Media is a Leading Global Affiliate Marketing Network , delivering performance on web and mobile to worldwide advertisers through a growing network of over 100K affiliates . With presence in India, Singapore, UAE, UK, and USA , vCommission empowers meaningful digital growth across multiple verticals — Ecommerce, Travel, Utility, LeadGen IN, LeadGen & PPC US, and India COD Ecom. We are looking for an experienced Media Buyer (Meta Ads Manager) to lead high-performance paid social camp…",
      "contract_type": "permanent",
      "company": {
        "__CLASS__": "Adzuna::API::Response::Company",
        "display_name": "vCommission"
      },
      "location": {
        "__CLASS__": "Adzuna::API::Response::Location",
        "area": [
          "India",
          "Haryana",
          "Gurgaon",
          "Mini Sectt."
        ],
        "display_name": "Mini Sectt., Gurgaon"
      },
      "salary_max": 288000,
      "salary_is_predicted": "0",
      "created": "2026-07-13T16:30:04Z",
      "id": "5798794539",
      "contract_time": "full_time",
      "adref": "eyJhbGciOiJIUzI1NiJ9.eyJzIjoiTEdCZ2RiaC04UkdTYjhQUkFSdVF2USIsImkiOiI1Nzk4Nzk0NTM5In0.L8BlS1E7D7VOJ2hnrB7T1r1Djr1FH--0nKJ0HyxqYi0",
      "category": {
        "label": "PR, Advertising & Marketing Jobs",
        "__CLASS__": "Adzuna::API::Response::Category",
        "tag": "pr-advertising-marketing-jobs"
      },
      "title": "Media Buyer : Meta Ads",
      "__CLASS__": "Adzuna::API::Response::Job",
      "latitude": 28.4596,
      "longitude": 77.07225,
      "redirect_url": "https://www.adzuna.in/details/5798794539?utm_medium=api&utm_source=e23c4cd2",
      "salary_min": 288000
    },
"""
class Adzuna:
    def __init__(self):
        self.base_url = adzuna_setting.BASE_URL
        self.params = {
        "app_id": adzuna_setting.APP_ID,
        "app_key": adzuna_setting.API_KEY,
        "sort_by": adzuna_setting.SORT_BY,
        "max_days_old": adzuna_setting.MAX_DAYS_OLD,
        "results_per_page": adzuna_setting.RESULTS_PER_PAGE
    }
        self.loadder = Loader()
    
    def fetch_single_page(self, uri):
        res = r.get(uri, params=self.params, timeout=(5, 30))
        res.raise_for_status()
        return res.json()
    
    def fetch(self):
        try:
            results=[]
            page = 1
            logger.info("Fetching records from Adzuna")
            while True:
                uri = f'{self.base_url}{page}'
                data = self.fetch_single_page(uri)
                jobs = data.get("results", [])
                if not jobs:
                    logger(f"No more jobs at page {page}")
                    break
                page_result=[]
                for job in jobs:
                    mapped_job = self.map_adzuna_job(job)
                    # results.append(mapped_job)
                    page_result.append(mapped_job.model_dump())
                self.loadder.load(page_result)
                page+=1
                # forced break
                # if page==100:
                #     break
            logger.info("Fetch completed from Adzuna")
            return [job.model_dump() for job in results]
        except Exception as e:
            logger.info(f"Error while fetching from Adzuna {e}")
            return []
        
    def map_adzuna_job(self, data: dict) -> Job:
        hash_id = get_hash(f"{data.get('title')}{data.get('company').get('display_name')}{data.get('location').get('display_name')}")
        # posted_date = data.get('created')
        # posted_date = posted_date.astimezone(timezone.utc).replace(tzinfo=None)
        return Job(
            id= hash_id,
            title= data.get('title'),
            company= data.get('company').get('display_name'),
            description= data.get('description'),
            location= data.get('location').get('display_name'),
            employment_type= data.get('contract_type'),
            salary_min= data.get('salary_min'),
            salary_max= data.get('salary_max'),
            source= 'Adzuna',
            apply_url= data.get('redirect_url'),
            posted_date= data.get('created')
        )