# -*- coding: utf-8 -*-
"""
get company rating from the user
and put it into the database

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests, time, sys, datetime, logging, re
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

### JOBSTREEET ###

def get_data_jobstreet(current_url,db_input,driver):
    source = requests.get(current_url).text
    soup = BeautifulSoup(source, 'html.parser')
    # jobstreet_input = {}
    detail_rating_array = []
    db_input['js_company_name'] = soup.find('h1',{'class':'_12x74-XLiHCJbGS0ymy4W3'}).text
    try:
        db_input['js_overal_rating'] = soup.find('h3',{'class':'bdUh8gNcTQA1ylvV8C38H'}).text
        friend_recommend = soup.find('span',{'class':'lW4-t2VNJP9bJiLQROUPO'}).text
        db_input['js_friend_recommend'] = re.sub('\D', '', friend_recommend)
        salary_rating = soup.find_all('div',{'class':'_1gI3visUCBog7H-CLrbPiA'})[2].text
        db_input['js_salary_rating'] = re.sub('\D', '', salary_rating)
    except:
        logger.error(f"rating not found for {db_input['company_name']}")
    try:
        driver.find_element_by_xpath("//span[@class='_1Lef0kL128VE4yMbviZ6Kk _2OB8mZUfjge3-NtWvcMAaT']/*[name()='svg'][@class='_3whuHPmGZhGiaL3OQ6KH5l Qthfr2_F5cWNSxbXOmDFA']").click()
        time.sleep(1)
        detail_rating_popup = driver.find_element_by_xpath("//div[@class='TltZ6b2JnBS0wooPRzNRC']")
        detail_rating_html = detail_rating_popup.get_attribute("outerHTML")
        soup_detail_rating = BeautifulSoup(detail_rating_html, 'html.parser')
        detail_ratings = soup_detail_rating.find_all('span',{'class':'OX0_TZZSlhMhIywgR8jko'})
        for details in detail_ratings:
            detail_rating_array.append(details.text)
        db_input['js_work_life_rating'] = detail_rating_array[0]
        db_input['js_carrer_dev_rating'] = detail_rating_array[1]
        db_input['js_benefits_rating'] = detail_rating_array[2]
        db_input['js_management_rating'] = detail_rating_array[3]
        db_input['js_working_environtment'] = detail_rating_array[4]
        db_input['js_stress_level'] = soup_detail_rating.find('div',{'class':'_1KNcRH74asnnEB9uUe_IBQ'}).text
    except:
        logger.error(f"detail rating not found for {db_input['company_name']}")
    try:
        average_process_times = soup.find('div',{'class':'_2m4xhUrF_OAoi38R1ZdMJl'}).text
        average_process_time = average_process_times.split("Processing Time",1)[1]
        if (average_process_time == "a day"):
            db_input['js_processing_time'] = 1
        else:
            db_input['js_processing_time'] = re.sub('\D', '', average_process_time)
    except:
        logger.error(f"processing time not found for {db_input['company_name']}")
    # db_input['js_created_at'] = datetime.datetime.now()
    db_input['js_updated_at'] = datetime.datetime.now()
    return(db_input)

def access_jobstreet(db_input):
    driver = set_browser()
    driver.get("https://www.jobstreet.com.my/en/companies")
    time.sleep(5)
    try:
        driver.find_element_by_xpath("//div[@class='_1k2gzoZHonK6KGE2eiCRz9']")
        time.sleep(1)
        driver.find_element_by_xpath("//span[@class='_1Lef0kL128VE4yMbviZ6Kk']/*[name()='svg'][@class='_3whuHPmGZhGiaL3OQ6KH5l _yK8zLfn0AZiFQ9Tjo2z1']").click()
        driver.find_element_by_name("query").send_keys(db_input['company_name'], Keys.ENTER)
    except:
        driver.find_element_by_name("query").send_keys(db_input['company_name'], Keys.ENTER)
    time.sleep(3)
    try:
        driver.find_element_by_xpath("//a[@class='tNpZ-r8HSFPRZ6NJvAkbQ']").click()
        current_url = driver.current_url
    except:
        print("company not found")
        logger.error(f"company {db_input['company_name']} not found on jobstreet")
        return(db_input)
    db_input = get_data_jobstreet(current_url,db_input,driver)
    driver.close()
    return(db_input)

### GLASSDOOR ###

def get_data_glassdoor(detail_rating_html,gd_input):
    soup_rating = BeautifulSoup(detail_rating_html, 'html.parser')
    detail_rating_arrays = []
    additional_rating_arrays = []
    gd_input['gd_company_name'] = soup_rating.find('h1',{'class':'eiRatingTrends__RatingTrendsStyle__title mt-std mt-lg-xxsm px-sm px-lg-std'}).text
    gd_input['gd_company_name'] = gd_input['gd_company_name'].lower().replace(" ratings and trends","")
    try:
        gd_input['gd_overal_rating'] = soup_rating.find('span',{'class':'eiRatingTrends__RatingTrendsStyle__overallRatingNum'}).text
        detail_rating = soup_rating.find_all('div',{'class':'col-2 p-0 eiRatingTrends__RatingTrendsStyle__ratingNum'})
        for rating in detail_rating:
            detail_rating_arrays.append(rating.text)
        gd_input['gd_culture_rating'] = detail_rating_arrays[1]
        gd_input['gd_work_life_rating'] = detail_rating_arrays[2]
        gd_input['gd_management_rating'] = detail_rating_arrays[3]
        gd_input['gd_benefits_rating'] = detail_rating_arrays[4]
        gd_input['gd_opportunity_rating'] = detail_rating_arrays[5]
        additional_rating = soup_rating.find_all('tspan',{'class':'donut__DonutStyle__donutchart_text_val'})
        for additionals in additional_rating:
            additional_rating_arrays.append(additionals.text)
        gd_input['gd_friend_recommend'] = additional_rating_arrays[0]
        gd_input['gd_business_outlook'] = additional_rating_arrays[2]
    except:
        logger.error(f"detail rating not found for {gd_input['gd_company_name']}")
    # gd_input['gd_created_at'] = datetime.datetime.now()
    gd_input['gd_updated_at'] = datetime.datetime.now()
    for key,value in gd_input.items():
        if(gd_input[key] == 'N/A'):
            gd_input[key] = None
    return(gd_input)

def access_glassdoor(gd_input):
    driver = set_browser()
    # driver = webdriver.Chrome(executable_path=chrome_driver_location)
    location = "Malaysia"
    user_id = "" ## insert your glasdoor email
    password_login = "" ## insert your glassdoor password
    glassdoor_link = "https://www.glassdoor.com/index.htm"
    try:
        driver.get(glassdoor_link)
        try:
            driver.find_element_by_xpath("//div[@class='locked-home-sign-in']").click()
            time.sleep(2)
            driver.find_element_by_xpath("//form[@name='emailSignInForm']//input[@id='userEmail']").send_keys(user_id)
            driver.find_element_by_xpath("//form[@name='emailSignInForm']//input[@id='userPassword']").send_keys(password_login)
            driver.find_element_by_xpath("//form[@name='emailSignInForm']//button[@name='submit']").click()
        except:
            driver.close()
            logger.error(f"failed to login glassdoor")
            return(gd_input)
        time.sleep(3)
        try:
            driver.find_element_by_xpath("//input[@id='sc.keyword']").send_keys(gd_input['company_name'])
            try:
                driver.find_element_by_xpath("//div[@class='context-picker inactive']").click()
                driver.find_element_by_xpath("//ul[@class='context-choice-list']//li[@class='reviews ']").click()
            except:
                driver.find_element_by_xpath("//div[@class='ml-xsm search__SearchStyles__searchDropdown css-1ohf0ui']").click()
                time.sleep(2)
                dropdown = driver.find_element_by_xpath("//div[@class='dropDownOptionsContainer']")
                dropdown.find_element_by_xpath("//ul//li[@class='dropdownOption   ']").click()
            driver.find_element_by_xpath("//input[@id='sc.location']").clear()
            driver.find_element_by_xpath("//input[@id='sc.location']").send_keys(location)
            try:
                driver.find_element_by_xpath("//button[@id='HeroSearchButton']").click()
            except:
                driver.find_element_by_xpath("//button[@class='gd-ui-button ml-std col-auto css-1m85qmw']").click()
        except:
            driver.close()
            logger.error(f"cant search {gd_input['company_name']} on glassdoor")
            return(gd_input)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v2__EIReviewsRatingsStylesV2__ratingInfo']")))
            driver.find_element_by_xpath("//div[@class='v2__EIReviewsRatingsStylesV2__ratingInfo']").click()
            detail_rating = driver.find_element_by_xpath("//div[@class='lib__ModalStyle__fullHeight ']")
            detail_rating_html = detail_rating.get_attribute("outerHTML")
        except:
            driver.close()
            logger.error(f"cant found {gd_input['company_name']} on glassdoor")
            return(gd_input)
        gd_input = get_data_glassdoor(detail_rating_html,gd_input)
        driver.close()
        return(gd_input)
    except:
        driver.close()
        return logger.error(f"cant access glassdoor")


## INPUT TO DB ###
def get_company_data(csv_path):
    return_value = {}
    company_list = pd.read_csv(csv_path)
    for i in range(len(company_list)):
        db_input = {}
        try:
            db_input['company_id'] = int(company_list['company_id'][i])
            if "property" in db_input['company_name']:
                db_input['company_name'] = db_input['company_name'].replace('property','properti')
            db_input = access_jobstreet(db_input)
            db_input = access_glassdoor(db_input)
            try:
                if ('js_company_name' in db_input) or ('gd_company_name' in db_input):
                    insert_data = db.findOrCreateReview(db_input)
            except:
                logger.error('cant insert into DB')
            return_value['insert_data'] = insert_data
            return_value['js_company_data'] = db_input
        except:
            continue
    return return_value

if __name__ == "__main__":
    try:
        get_company_data(sys.argv[1])
    except:
        print("please input csv file path")