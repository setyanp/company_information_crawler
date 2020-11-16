## Installation

```bash
pip install -r requirement.txt
```

## Create DB with 5 tables

i'm using MYSQL for this project, you can change to any db type or dialect, you can also change the table or column name but you need to change the setup later

- company_information_crawl (table for store basic information company like name, logo, location, etc)
    column list:
    - id
    - company_name
    - js_company_name
    - js_company_logo
    - js_company_website
    - js_company_category
    - js_company_information
    - js_company_join_us
    - js_company_banner
    - js_company_photo
    - js_company_location
    - js_company_size
    - ind_company_name
    - ind_company_logo
    - ind_company_website
    - ind_company_information
    - ind_company_location
    - ind_company_size
    - ind_company_industry
    - ind_company_video
    - ind_company_photo
    - gd_company_name
    - gd_company_logo
    - gd_company_website
    - gd_company_information
    - gd_company_location
    - gd_company_size
    - gd_company_industry
    - gd_company_photo
    - created_at
    - updated_at

- company_review_crawl (table to store company rating from the user review, like rating of work life balance, etc)
    column list:
    - id
    - company_id
    - company_name
    - js_company_name
    - js_overal_rating
    - js_work_life_rating
    - js_carrer_dev_rating
    - js_benefits_rating
    - js_management_rating
    - js_working_environtment
    - js_stress_level
    - js_friend_recommend
    - js_salary_rating
    - js_processing_time
    - js_created_at
    - js_updated_at
    - gd_company_name
    - gd_overal_rating
    - gd_culture_rating
    - gd_work_life_rating
    - gd_management_rating
    - gd_benefits_rating
    - gd_opportunity_rating
    - gd_friend_recommend
    - gd_business_outlook
    - gd_created_at
    - gd_updated_at

- jobstreet_review_crawl (table to store user reviews from jobstreet)
    column list:
    - id
    - company_name
    - js_company_name
    - review_title
    - rating
    - position
    - experience
    - review_date
    - good_things
    - challenges
    - created_at
    - updated_at

- glassdoor_review_crawl (table to store user reviews from glassdoor)
    column list:
    - id
    - company_name
    - gd_company_name
    - review_title
    - rating
    - position
    - work_duration
    - review_date
    - pros
    - cons
    - created_at
    - updated_at

- indeed_review_crawl (table to store user reviews from indeed)
    column list:
    - id
    - company_name
    - ind_company_name
    - review_title
    - rating
    - position
    - location
    - review_date
    - review
    - created_at
    - updated_at

## Create CSV that have "company_name" as column name (and company_id for rating crawler)

## fill db information every file and email & password for login glassdoor

## run the file

- to collecting company's basic information:
    '''bash
    python company_information_crawl.py csv_file.csv
    '''

- to collecting company's rating from user reviews:
    '''bash
    python company_rating_crawl.py csv_file.csv
    '''

- to collecting company's user review:
    '''bash
    python company_review_crawl.py csv_file.csv
    '''