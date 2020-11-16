# -*- coding: utf-8 -*-
"""
get company information from jobstreet, indoor, and glassdoor
and put it into the database

information that crawled is:
id,
company_name,
js_company_name,
js_company_logo,
js_company_website,
js_company_category,
js_company_information,
js_company_join_us, => paragraph that tell why user should join the company
js_company_banner,
js_company_photo,
js_company_location,
js_company_size,
ind_company_name,
ind_company_logo,
ind_company_website,
ind_company_information,
ind_company_location,
ind_company_size
ind_company_industry,
ind_company_video,
ind_company_photo,
gd_company_name,
gd_company_logo,
gd_company_website,
gd_company_information,
gd_company_location,
gd_company_size,
gd_company_industry,
gd_company_photo,
created_at,
updated_at,

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

    # auto install newest version of ChromeDriverManager
    return (webdriver.Chrome(ChromeDriverManager().install(),options=options))

## ACCESS JOBSTREET ##
def js_fetch_data(db_input,js_source):
    soup = BeautifulSoup(js_source, 'html.parser')
    try:
        company_logo = soup.find('img',{'class':'_1Cy6lcihWpceLLGB3qdmV1'})
        db_input['js_company_logo'] = company_logo['src']
        if("data:image/png" in db_input['js_company_logo']):
            db_input['js_company_logo'] = None
        db_input['js_company_name'] = soup.find('h1',{'class':'_12x74-XLiHCJbGS0ymy4W3'}).text
        db_input['js_company_category'] = soup.find('h3',{'class':'_4M9M6BL6WODIESLy62e7B'}).text
    except:
        logger.error(f"js information not found for {db_input['company_name']}")
        return(db_input)
    try:
        js_company_information = soup.find('div',{'class':'_3OMs-aRPjPeeTHwPNJStcd'}).text
        js_company_information = js_company_information.replace("\u200b","")
        db_input['js_company_information'] = re.sub('\s+',' ',js_company_information).lstrip()
    except:
        db_input['js_company_information'] = None
        logger.error(f"js company basic information not found for {db_input['company_name']}")
    try:
        db_input['js_company_join_us'] = soup.find_all('div',{'class':'_1VBSqtP4zA2yuaZlFQOv5s'})[1].text
        db_input['js_company_join_us'] = db_input['js_company_join_us'].replace("\u200b","")
        db_input['js_company_join_us'] = re.sub('\s+',' ',re.sub('\s+',' ',db_input['js_company_join_us'])).split("us?",1)[1].lstrip()

        if("Continue reading" in db_input['js_company_join_us']):
           db_input['js_company_join_us'] = db_input['js_company_join_us'].replace("Continue reading","")
    except:
        db_input['js_company_join_us'] = None
        logger.error(f"js company why join us not found for {db_input['company_name']}")
    try:
        company_banner_src = soup.find('img',{'class':'_15hB9eJ5YpdQ2gFguVXaY8'})
        db_input['js_company_banner'] = company_banner_src['src']
    except:
        db_input['js_company_banner'] = None
        logger.error(f"js company banner not found for {db_input['company_name']}")
    try:
        company_photos = soup.find_all('div',{'class':'_1IMdRlqiUkqQKGfNraCJMS'})
        photo_url_array = []
        
        for photo in company_photos:
            photo_url =  re.search('url\((.*)\)', photo['style']).group(1)
            photo_url_array.append(photo_url)
        db_input['js_company_photo'] = ",".join(photo_url_array)
        db_input['js_company_photo'] = db_input['js_company_photo'].replace('"','')
        if(len(photo_url_array) == 0):
            db_input['js_company_photo'] = None
    except:
        db_input['js_company_photo'] = None
        logger.error(f"js company photo not found for {db_input['company_name']}")
    try:
        another_informations = soup.find_all('div',{'class':'tLym6yVY9nZDzFy00pE51'})
        for another_information in another_informations:
            text_result = text_result = another_information.find('h4',{'class':'_20_RFwflXkbrxAcEmd-yl7'}).text.lower()
            if("location" in text_result and 'js_company_location' not in db_input):
                get_location = another_information.find('p',{'class':'_2VUHEvZBE00PkfHVPj0A5k'}).text
                get_location = re.sub('\s+',' ',get_location)
                db_input['js_company_location'] = get_location
            elif("company size" in text_result):
                company_size = another_information.find('p',{'class':'_2VUHEvZBE00PkfHVPj0A5k'}).text
                company_size = re.sub('\s+',' ',company_size)
                db_input['js_company_size'] = company_size
            elif("website" in text_result):
                website = another_information.find('p',{'class':'_2VUHEvZBE00PkfHVPj0A5k'}).text
                db_input['js_company_website'] = website
            else:
                continue
    except:
        logger.error(f"js company detail information not found for {db_input['company_name']}")
    if('js_company_location' not in db_input):
        db_input['js_company_location'] = None
    if('js_company_size' not in db_input):
        db_input['js_company_size'] = None
    if('js_company_website' not in db_input):
        db_input['js_company_website'] = None
    
    return(db_input)

def js_access(db_input):
    driver = set_browser()
    js_link = "https://www.jobstreet.com.my/en/companies/browse-reviews"
    driver.get(js_link)
    time.sleep(7)
    
    company_name = db_input['company_name']
    
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
        return(db_input)
    js_page_url = driver.find_element_by_xpath("//div[@id='app']")
    js_source = js_page_url.get_attribute("outerHTML")
    
    db_input = js_fetch_data(db_input,js_source)
    time.sleep(1)
    driver.close()
    return(db_input)
    

## ACCESS GLASSDOOR ##
def gd_fetch_data(db_input,gd_source):
    soup = BeautifulSoup(gd_source, 'html.parser')
    try:
        db_input['gd_company_name'] = soup.find('div',{'class':'header cell info'}).text.lstrip()
        if(db_input['gd_company_name'] == "M&G plc" and db_input['company_name'] != "M&G plc"):
            db_input.pop('gd_company_name', None)
            return(db_input)
    except:
        logger.error(f"gd name not found for {db_input['company_name']}")
        return(db_input)
    try:
        glassdoor_company_logo = soup.find('span',{'class':'sqLogo tighten lgSqLogo logoOverlay'})
        glassdoor_company_logo = glassdoor_company_logo.find('img')
        db_input['gd_company_logo'] = glassdoor_company_logo['src']
    except:
        db_input['gd_company_logo'] = None
    try:
        glassdoor_all_info = soup.find('div',{'id':'EmpBasicInfo'})
        glassdoor_info_details = glassdoor_all_info.find_all('div',recursive=False)
        company_introduction = glassdoor_info_details[2].find('div')
        company_introduction = company_introduction['data-full']
        db_input['gd_company_information'] = company_introduction.replace("&rsquo;","'").lstrip()
    except:
        db_input['gd_company_information'] = None
        logger.error(f"gd company about not found for {db_input['company_name']}")
    try:
        company_datas = soup.find_all('div',{'class':'infoEntity'})
        db_input['gd_company_website'] = company_datas[0].text.lower().split("website",1)[1]
        db_input['gd_company_location'] = company_datas[1].text.lower().split("headquarters",1)[1]
        db_input['gd_company_size'] = company_datas[2].text.lower().split("size",1)[1]
        db_input['gd_company_industry'] = company_datas[5].text.lower().split("industry",1)[1]
    except:
        db_input['gd_company_website'] = None
        db_input['gd_company_location'] = None
        db_input['gd_company_size'] = None
        db_input['gd_company_industry'] = None
        logger.error(f"gd company details not found for {db_input['company_name']}")
        
    return(db_input)
    
def gd_fetch_photo(db_input,gd_photo_source):
    photo_soup = BeautifulSoup(gd_photo_source, 'html.parser')
    try:
        gd_company_photos = photo_soup.find('ul',{'class':'grid'})
        gd_company_photo = gd_company_photos.find_all('img')
        gd_photo_url_array = []
    
        for photo in gd_company_photo:
            photo_url =  photo['src']
            if(".jpg" in photo_url):
                gd_photo_url_array.append(photo_url)
            else:
                continue
        gd_photo_url_array = ",".join(gd_photo_url_array)
        gd_photo_url_array = gd_photo_url_array.replace("/lst/","/l/")
        db_input['gd_company_photo'] = gd_photo_url_array
    except:
        db_input['gd_company_photo'] = None
        logger.error(f"gd company photo not found for {db_input['company_name']}")
    return(db_input)
    
def gd_access(db_input):
    driver = set_browser()
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
            driver.find_element_by_xpath("//input[@id='KeywordSearch']").send_keys(db_input['company_name'])
            driver.find_element_by_xpath("//input[@id='LocationSearch']").clear()
            driver.find_element_by_xpath("//input[@id='LocationSearch']").send_keys(location, Keys.ENTER)
            driver.find_element_by_xpath("//button[@class='gd-btn-mkt']").click()
        except:
            logger.error(f"cant search {db_input['company_name']} on glassdoor")
            return(db_input)
    else:
        try:
            driver.find_element_by_xpath("//input[@id='sc.keyword']").send_keys(db_input['company_name'])
            driver.find_element_by_xpath("//input[@id='sc.location']").clear()
            driver.find_element_by_xpath("//input[@id='sc.location']").send_keys(location, Keys.ENTER)
        except:
            logger.error(f"cant search {db_input['company_name']} on glassdoor")
            return(db_input)
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
                if ("malaysia" in location or db_input['company_name'] in company_name_result):
                    click_number = i+1
                    driver.find_element_by_xpath(f"(//div[@class='col-9 pr-0']//h2//a)[{click_number}]").click()
                    time.sleep(5)
                    break
                else:
                    continue
    except:
        logger.error(f"cant found {db_input['company_name']} on glassdoor")
        return(db_input)
    
    gd_page_url =  driver.find_element_by_xpath("//div[@class='pageContentWrapper ']")
    gd_source = gd_page_url.get_attribute("outerHTML")    
    db_input = gd_fetch_data(db_input,gd_source)
    
    time.sleep(4)
    photo_soup = BeautifulSoup(gd_source, 'html.parser')
    data_number = photo_soup.find_all('span',{'class':'num h2'})
    
    try:
        total_photo = int(data_number[6].text)
        if(total_photo > 0 and ("gd_company_name" in db_input)):
            driver.find_element_by_xpath("//a[@class='eiCell cell photos ']").click()
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 1000)")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 1500)")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 2500)")
            time.sleep(1)
            gd_photo_page_url =  driver.find_element_by_xpath("//div[@class='photoGrid']")
            gd_photo_source = gd_photo_page_url.get_attribute("outerHTML")
            
            db_input = gd_fetch_photo(db_input,gd_photo_source)
        else:
            db_input['gd_company_photo'] = None
    except:
        db_input['gd_company_photo'] = None
        logger.error(f"cant found photo of {db_input['company_name']} on glassdoor")
    driver.close()
    return(db_input)
    
## INDEED ACCESS ##
def ind_fetch_data(db_input,ind_source):
    soup = BeautifulSoup(ind_source, 'html.parser')
    try:
        db_input['ind_company_name'] = soup.find('span',{'class':'cmp-CompactHeaderCompanyName'}).text.lstrip()
    except:
        logger.error(f"indeed can't get company data {db_input['company_name']}")
        return(db_input)
    try:
        ind_company_logo_url = soup.find('img',{'class':'cmp-CompactHeaderCompanyLogo-logo'})
        db_input['ind_company_logo'] = ind_company_logo_url['src']
        if("placeholder-logo-128" in db_input['ind_company_logo']):
            db_input['ind_company_logo'] = None
    except:
        db_input['ind_company_logo'] = None
        logger.error(f"indeed can't get company logo {db_input['company_name']}")
    try:
        ind_company_about_div = soup.find('div',{'id':'cmp-about'})
        db_input['ind_company_information'] = ind_company_about_div.find('div').text
    except:
        db_input['ind_company_information'] = None
        logger.error(f"indeed can't get company information {db_input['company_name']}")
    try:
        ind_sidebar_details = soup.find('dl',{'id':'cmp-company-details-sidebar'})
        ind_company_detail_key = ind_sidebar_details.find_all('dt')
        ind_company_detail_item = ind_sidebar_details.find_all('dd')
        for i in range(len(ind_company_detail_item)):
            key_text = ind_company_detail_key[i].text.lower()
            item_text = ind_company_detail_item[i].text.lower()
            if("headquarters" in key_text):
                db_input['ind_company_location'] = item_text
            elif("employees" in key_text):
                db_input['ind_company_size'] = item_text
            elif("industry" in key_text):
                db_input['ind_company_industry'] = item_text
            elif("links" in key_text):
                ind_comp_website_a = ind_company_detail_item[i].find('a')
                db_input['ind_company_website'] = ind_comp_website_a['href']
            else:
                continue
    except:
        logger.error(f"indeed can't get company detail {db_input['company_name']}")
    if('ind_company_location' not in db_input):
        db_input['ind_company_location'] = None
    if('ind_company_size' not in db_input):
        db_input['ind_company_size'] = None
    if('ind_company_industry' not in db_input):
        db_input['ind_company_industry'] = None
    if('ind_company_website' not in db_input):
        db_input['ind_company_website'] = None
    try:
        ind_company_vid = soup.find_all('div',{'class':'cmp-user-video'})
        ind_video_url_array = []        
        for video in ind_company_vid:
            video_urls =  video.find('iframe')
            video_url = video_urls['src']
            ind_video_url_array.append(video_url)
        db_input['ind_company_video'] = ",".join(ind_video_url_array)
        if(len(db_input['ind_company_video']) == 0):
            db_input['ind_company_video'] = None
    except:
        db_input['ind_company_video'] = None
        logger.error(f"indeed can't get company video {db_input['company_name']}")
    return(db_input)
    
def ind_fetch_photo(db_input,photo_source):
    photo_soup = BeautifulSoup(photo_source, 'html.parser')
    try:
        ind_company_photo = photo_soup.find_all('img',{'class':'cmp-PhotoGridTiles-img'})
        ind_photo_url_array = []
    
        for photo in ind_company_photo:
            photo_url =  photo['src']
            photo_url = "https://malaysia.indeed.com" + photo_url
            ind_photo_url_array.append(photo_url)
        ind_photo_url_array = ",".join(ind_photo_url_array)
        db_input['ind_company_photo'] = ind_photo_url_array.replace("-sqt-","-l-")
        if (len(ind_photo_url_array) == 0):
            db_input['ind_company_photo'] = None
    except:
        db_input['ind_company_photo'] = None
        logger.error(f"indeed can't get company photo {db_input['company_name']}")
    return(db_input)
    
def ind_access(db_input):
    driver = set_browser()
    company_name = db_input['company_name']
    indeed_link = "https://malaysia.indeed.com/companies"
    driver.get(indeed_link)
    time.sleep(7)
    try:
        driver.find_element_by_xpath("//input[@id='search-by-company-input']").send_keys(company_name)
        driver.find_element_by_xpath("//button[@id='cmp-discovery-cs-submit']").click()
    except:
        logger.error(f"cant search {db_input['company_name']} on indeed")
    try:
        time.sleep(5)
        driver.find_element_by_xpath("//div[@class='cmp-company-tile-blue-name']/a[@itemprop='url']").click()
        time.sleep(3)
        driver.find_element_by_xpath("//li[@class='cmp-CompactHeaderMenuItem'][1]/a[@class='cmp-CompactHeaderMenuItem-link cmp-u-noUnderline']").click()
    except:
        logger.error(f"indeed cant found {db_input['company_name']}")
        return(db_input)

    ind_page_url =  driver.find_element_by_xpath("//div[@id='cmp-root']")
    ind_source = ind_page_url.get_attribute("outerHTML")
    
    db_input = ind_fetch_data(db_input,ind_source)
    
    try:
        time.sleep(2)
        driver.find_element_by_xpath("//li[@class='cmp-CompactHeaderMenuItem'][4]/a[@class='cmp-CompactHeaderMenuItem-link cmp-u-noUnderline']").click()
    except:
        logger.error(f"indeed failed click photo {db_input['company_name']}")
    time.sleep(2)
    photo_page_url =  driver.find_element_by_xpath("//div[@class='cmp-PhotoGridList']")
    photo_source = photo_page_url.get_attribute("outerHTML")
    
    db_input = ind_fetch_photo(db_input,photo_source)
    driver.close()
    return(db_input)
    
## INPUT TO DB ###
def get_company_info(csv_path):
    return_value = {}
    company_list = pd.read_csv(csv_path)
    for i in range(len(company_list)):
        db_input = {}
        try:
            print(company_list['company_name'][i])
            db_input['company_name'] = company_list['company_name'][i]
            db_input = js_access(db_input)
            db_input = ind_access(db_input)
            db_input = gd_access(db_input)

            try:
                if(('js_company_name' in db_input) or ('gd_company_name' in db_input) or ('ind_company_name' in db_input)):
                    insert_data = db.findOrCreateInformation(db_input)
            except:
                logger.error(f"cant insert into DB {db_input['company_name']}")
            return_value['insert_data'] = insert_data
        except:
            continue
    return return_value

if __name__ == "__main__":
    try:
        get_company_info(sys.argv[1])
    except:
        print("please input csv file path")