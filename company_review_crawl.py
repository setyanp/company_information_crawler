# -*- coding: utf-8 -*-
"""
get company review of the user from jobstreet, indoor, and glassdoor
and put it into the database

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time,sys,logging,re
from db_helper.db_helper import DBHelper
import pandas as pd

#initiate DB connection
db_dialect = 'mysql+pymysql'
db_username = '' #insert db uname
db_password = '' #insert db password
db_host = '' #insert db hostname
db_database = '' #insert database name
db = DBHelper(db_dialect,db_username,db_password,db_host,db_database)

#Logging setup
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter=logging.Formatter('%(asctime)s | %(levelname)s -> %(message)s')
# creating a handler to log on the filesystem
file_handler=logging.FileHandler('error_log.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)

logger.addHandler(file_handler)

def set_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=1200,1080')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return (webdriver.Chrome(ChromeDriverManager().install(),options=options))



## ACCESS INDEED ##
def ind_fetch_review(review_page,ind_reviews,company_name):
    soup = BeautifulSoup(review_page, 'html.parser')
    try:
        review_box = soup.find_all('div',{'class':'cmp-Review-container'})    
        for box in review_box:
            try:
                title = box.find('div',{'class':'cmp-Review-title'}).text
            except:
                continue
            ind_reviews['review_title'].append(title)
            try:
                ind_company_name = soup.find('span',{'class':'cmp-CompactHeaderCompanyName'}).text
            except:
                ind_company_name = company_name
            ind_reviews['ind_company_name'].append(ind_company_name)
            try:
                rating = box.find('div',{'class':'cmp-ReviewRating-text'}).text
            except:
                rating = ""
            ind_reviews['rating'].append(rating)
            try:
                reviewer = box.find('div',{'class':'cmp-Review-author'}).text
                reviewer_data = reviewer.split(" - ")
                position = reviewer_data[0]
                location = reviewer_data[1]
                date = reviewer_data[2]
            except:
                reviewer = ""
            ind_reviews['position'].append(position)
            ind_reviews['location'].append(location)
            ind_reviews['review_date'].append(date)
            try:
                review = box.find('div',{'class':'cmp-Review-text'}).text
                review = re.sub('\s+',' ',review)
            except:
                review = ""
            ind_reviews['review'].append(review)
        return(ind_reviews)
    except:
        logger.error(f"cant get {company_name} review on indeed")
        return(ind_reviews)

def ind_access(company_name):
    ind_reviews = {}
    ind_reviews["ind_company_name"] = []
    ind_reviews['review_title'] = []
    ind_reviews['rating'] = []
    ind_reviews['position'] = []
    ind_reviews['location'] = []
    ind_reviews['review_date'] = []
    ind_reviews['review'] = []
    
    driver = set_browser()
    indeed_link = "https://malaysia.indeed.com/companies"
    driver.get(indeed_link)
    time.sleep(7)
    try:
        driver.find_element_by_xpath("//input[@id='search-by-company-input']").send_keys(company_name)
        driver.find_element_by_xpath("//button[@id='cmp-discovery-cs-submit']").click()
    except:
        logger.error(f"cant search {company_name} on indeed")
    try:
        time.sleep(5)
        driver.find_element_by_xpath("//div[@class='cmp-company-tile-blue-name']/a[@itemprop='url']").click()
        time.sleep(3)
        driver.find_element_by_xpath("//li[@class='cmp-CompactHeaderMenuItem'][2]/a[@class='cmp-CompactHeaderMenuItem-link cmp-u-noUnderline']").click()
    except:
        logger.error(f"indeed cant found {company_name}")
        return(ind_reviews)
       
    review_page_url =  driver.find_element_by_xpath("//div[@id='cmp-container']")
    review_page = review_page_url.get_attribute("outerHTML")
    
    ind_reviews = ind_fetch_review(review_page,ind_reviews,company_name)
    time.sleep(1)
    driver.close()
    return(ind_reviews)
    

## ACCESS GLASSDOOR ##
def gd_fetch_review(detail_review_html,gd_reviews,company_name):
    soup_review = BeautifulSoup(detail_review_html, 'html.parser')
    try:
        review_box = soup_review.find_all('div',{'class':'gdReview'})
        for box in review_box:
            try:
                review_title = box.find('h2',{'class':'h2 summary strong mt-0 mb-xsm'}).text
            except:
                continue
            gd_reviews['review_title'].append(review_title)
            try:
                gd_company_name = soup_review.find('span',{'id':'DivisionsDropdownComponent'}).text
            except:
                gd_company_name = company_name
            gd_reviews['gd_company_name'].append(gd_company_name.lower().replace("&rsquo;","'"))
            try:
                rating = box.find('div',{'class':'v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__small'}).text
            except:
                rating = ""
            gd_reviews['rating'].append(rating)
            try:
                position = box.find('span',{'class':'authorJobTitle middle'}).text
            except:
                position = ""
            gd_reviews['position'].append(position)
            try:
                work_duration = box.find('p',{'class':'mainText mb-0'}).text
            except:
                work_duration = ""
            gd_reviews['work_duration'].append(work_duration)
            try:
                review_date = box.find('time',{'class':'date subtle small'}).text
            except:
                review_date = ""
            gd_reviews['review_date'].append(review_date)
            try:
                pros = box.find_all('div',{'class':'v2__EIReviewDetailsV2__fullWidth'})[0].text
                pros = re.sub('\s+',' ',pros)
                pros = pros[4:].replace("\r\n"," ").replace("&rsquo;","'").lstrip()
            except:
                pros = ""
            gd_reviews['pros'].append(pros)   
            try:
                cons = box.find_all('div',{'class':'v2__EIReviewDetailsV2__fullWidth'})[1].text
                cons = re.sub('\s+',' ',cons)
                cons = cons[4:].replace("\r\n"," ").replace("&rsquo;","'").lstrip()
            except:
                cons = ""
            gd_reviews['cons'].append(cons)
        return(gd_reviews)
    except:
        logger.error(f'reviews company {company_name} not found on glassdoor')
        return(gd_reviews)

def gd_access(company_name):
    driver = set_browser()
    
    gd_reviews = {}
    gd_reviews['gd_company_name'] = []
    gd_reviews['review_title'] = []
    gd_reviews['rating'] = []
    gd_reviews['position'] = []
    gd_reviews['work_duration'] = []
    gd_reviews['review_date'] = []
    gd_reviews['pros'] = []
    gd_reviews['cons'] = []
    
    location = "Malaysia"
    gd_link = "https://www.glassdoor.com/member/home/companies.htm"
    driver.get(gd_link)
    time.sleep(4)
    

    
    if(driver.current_url != gd_link):
        user_id = "" ## insert your glasdoor email
        password_login = "" ## insert your glassdoor password
        driver.find_element_by_xpath("//input[@id='userEmail']").send_keys(user_id)
        driver.find_element_by_xpath("//input[@id='userPassword']").send_keys(password_login)
        driver.find_element_by_xpath("//button[@name='submit']").click()
    time.sleep(7)
    if(driver.current_url != gd_link):
        try:
            driver.find_element_by_xpath("//input[@id='KeywordSearch']").send_keys(company_name)
            driver.find_element_by_xpath("//input[@id='LocationSearch']").clear()
            driver.find_element_by_xpath("//input[@id='LocationSearch']").send_keys(location, Keys.ENTER)
            driver.find_element_by_xpath("//button[@class='gd-btn-mkt']").click()
        except:
            logger.error(f"cant search {company_name} on glassdoor")
            return(gd_reviews)
    else:
        try:
            driver.find_element_by_xpath("//input[@id='sc.keyword']").send_keys(company_name)
            driver.find_element_by_xpath("//input[@id='sc.location']").clear()
            driver.find_element_by_xpath("//input[@id='sc.location']").send_keys(location, Keys.ENTER)
        except:
            logger.error(f"cant search {company_name} on glassdoor")
            return(gd_reviews)
    time.sleep(10)
    try:
        if("Overview" not in driver.current_url):
            search_result_page = driver.find_element_by_xpath("//div[@id='PageBodyContents']")
            search_result_source = search_result_page.get_attribute("outerHTML")

            search_soup = BeautifulSoup(search_result_source, 'html.parser')
            
            search_result = search_soup.find_all('div',{'class':'col-9 pr-0'})
            
            for i in range(len(search_result)):
                location = search_result[i].find('p',{'class':'hqInfo adr m-0'}).text.lower()
                company_name_result =  search_result[i].find('h2').find('a').text.lower()
                if ("malaysia" in location or company_name in company_name_result):
                    click_number = i+1
                    driver.find_element_by_xpath(f"(//div[@class='col-9 pr-0']//h2//a)[{click_number}]").click()
                    time.sleep(5)
                    break
                else:
                    continue
    except:
        logger.error(f"cant found {company_name} on glassdoor")
        return(gd_reviews)
    try:
        driver.find_element_by_xpath("//a[@class='eiCell cell reviews '][1]").click()
    except:
        logger.error(f"cant found {company_name} reviews on glassdoor")
        return(gd_reviews)
    time.sleep(7)
    detail_review_element = driver.find_element_by_xpath("//div[@id='PageContent']")
    detail_review_html = detail_review_element.get_attribute("outerHTML")
    gd_reviews = gd_fetch_review(detail_review_html,gd_reviews,company_name)
    time.sleep(1)
    driver.close()
    return(gd_reviews)    
    

## ACCESS JOBSTREET ##
def js_fetch_review(js_reviews,js_source,company_name):
    soup_reviews = BeautifulSoup(js_source, 'html.parser')
    try:
        review_box = soup_reviews.find_all('div',{'class':'_3Y961Q5RKApy6FsXD-WEqq'})
        for box in review_box:
            try:
                title = box.find('h3',{'class':'_3MyALCcnLdxQbK6kunFzgk'}).text
                title = title.replace("\u200b","")
                title = re.sub('\s+',' ',title).lstrip()
            except:
                continue
            js_reviews['review_title'].append(title)
            try:
                js_company_name = soup_reviews.find('h1',{'class':'_12x74-XLiHCJbGS0ymy4W3'}).text
            except:
                js_company_name = company_name
            js_reviews['js_company_name'].append(js_company_name)
            try:
                rating = box.find('span',{'class':'Tlh9F04dzRFo78gJPlhMM'}).text
            except:
                rating = ""
            js_reviews['rating'].append(rating)
            try:
                date = box.find('p',{'class':'_1_dikBfyioZMrCoMA4C9hZ'}).text
            except:
                date = ""
            js_reviews['review_date'].append(date)
            try:
                position = box.find('p',{'class':'_1xPYIUfA9IwtVyBsOt_SaR'}).text
            except:
                position = ""
            js_reviews['position'].append(position)
            try:
                experience = box.find('div',{'id':'years-worked-with'}).text
            except:
                experience = ""
            js_reviews['experience'].append(experience)
            try:
                good_things = box.find('div',{'id':'good-review'}).text
                good_things = good_things.replace("Continue reading", "").replace("\u200b","")
                good_things = re.sub('\s+',' ',good_things).lstrip()
            except:
                good_things = ""
            js_reviews['good_things'].append(good_things)
            try:
                challenges = box.find('div',{'id':'challange-review'}).text

                challenges = challenges.replace("Continue reading", "").replace("\u200b","")
                challenges = re.sub('\s+',' ',challenges).lstrip()
            except:
                challenges = ""
            js_reviews['challenges'].append(challenges)
        return(js_reviews)
    except:
        logger.error(f'reviews company {company_name} not found')
        return(js_reviews)
    
def js_access(company_name):
    driver = set_browser()
    js_link = "https://www.jobstreet.com.my/en/companies/browse-reviews"
    driver.get(js_link)
    time.sleep(7)
    
    js_reviews = {}
    js_reviews['js_company_name'] = []
    js_reviews['rating'] = []
    js_reviews['position'] = []
    js_reviews['experience'] = []
    js_reviews['review_date'] = []
    js_reviews['review_title'] = []
    js_reviews['good_things'] = []
    js_reviews['challenges'] = []
    
    try:
        driver.find_element_by_xpath("//div[@class='_1k2gzoZHonK6KGE2eiCRz9']")
        time.sleep(1)
        driver.find_element_by_xpath("//span[@class='_1Lef0kL128VE4yMbviZ6Kk']/*[name()='svg'][@class='_3whuHPmGZhGiaL3OQ6KH5l _yK8zLfn0AZiFQ9Tjo2z1']").click()
        driver.find_element_by_xpath("//input[@class='_3lkNK00yp4N6QJVBpkm7M0']").send_keys(company_name, Keys.ENTER)
    except:
        driver.find_element_by_xpath("//input[@class='_3lkNK00yp4N6QJVBpkm7M0']").send_keys(company_name, Keys.ENTER)
        time.sleep(10)
        try:
            driver.find_element_by_xpath("//div[@class='_1k2gzoZHonK6KGE2eiCRz9']")
            driver.find_element_by_xpath("//span[@class='_1Lef0kL128VE4yMbviZ6Kk']/*[name()='svg'][@class='_3whuHPmGZhGiaL3OQ6KH5l _yK8zLfn0AZiFQ9Tjo2z1']").click()
        except:
            time.sleep(1)
    time.sleep(5)
    try:
        driver.find_element_by_xpath("//a[@class='tNpZ-r8HSFPRZ6NJvAkbQ']").click()
    except:
        logger.error(f'company {company_name} not found')
        return(js_reviews)        
    try:
        driver.get(driver.current_url + "/reviews")
    except:
        logger.error(f'reviews {company_name} not found')
        return(js_reviews)
    time.sleep(3)
    js_page_url = driver.find_element_by_xpath("//div[@id='app']")
    js_source = js_page_url.get_attribute("outerHTML")
    
    js_reviews = js_fetch_review(js_reviews,js_source,company_name)
    
    time.sleep(1)
    driver.close()
    return(js_reviews)
    

## INPUT TO DB ###
def get_company_info(csv_path):
    return_value = {}
    company_list = pd.read_csv(csv_path)
    for i in range(10):
        try:
            print(company_list['company_name'][i])
            company_name = company_list['company_name'][i]
            js_reviews = js_access(company_name)
            gd_reviews = gd_access(company_name)
            ind_reviews = ind_access(company_name)
            if(len(js_reviews["review_title"]) > 0):
                insert_data = db.storeJobstreetReview(js_reviews,company_name)
            if(len(gd_reviews["review_title"]) > 0):
                insert_data = db.storeGlassdoorReview(gd_reviews,company_name)
            if(len(ind_reviews["review_title"]) > 0):
                insert_data = db.storeIndeedReview(ind_reviews,company_name)
            return_value["insert_data"] = insert_data
        except:
            continue
    return return_value

if __name__ == "__main__":
    try:
        get_company_info(sys.argv[1])
    except:
        print("please input csv file path")