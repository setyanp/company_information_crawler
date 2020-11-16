import sqlalchemy as db
import datetime

class DBHelper:
    def __init__(self,db_dialect,db_username,db_password,db_host,db_database):
        self.engine = db.create_engine(db_dialect + '://' + db_username + ':' + db_password + '@' + db_host + '/' + db_database)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
        #initate table
        self.user = db.Table('user', self.metadata, autoload=True, autoload_with=self.engine)
        self.company_review_crawl = db.Table('company_review_crawl', self.metadata, autoload=True, autoload_with=self.engine)
        self.company_information_crawl = db.Table('company_information_crawl', self.metadata, autoload=True, autoload_with=self.engine)
        self.jobstreet_review_crawl = db.Table('jobstreet_review_crawl', self.metadata, autoload=True, autoload_with=self.engine)
        self.glassdoor_review_crawl = db.Table('glassdoor_review_crawl', self.metadata, autoload=True, autoload_with=self.engine)
        self.indeed_review_crawl = db.Table('indeed_review_crawl', self.metadata, autoload=True, autoload_with=self.engine)

    def findOrCreateReview(self,data_list):
        try:
            query = db.select([self.company_review_crawl]).where(self.company_review_crawl.c.company_id==data_list['company_id'])
            result_proxy = self.connection.execute(query)
            result_set = result_proxy.fetchall()
            result_proxy.close()
        except Exception as e:
            print(e)
        if (len(result_set) < 1):
            try:
                data_list['js_created_at'] = datetime.datetime.now()
                data_list['gd_created_at'] = datetime.datetime.now()
                query = db.insert(self.company_review_crawl).values(data_list)
                resultproxy = self.connection.execute(query)
                resultproxy.close()
            except Exception as e:
                print(e)
            success_input = 1
        else:
            try:
                query = db.update(self.company_review_crawl).values(data_list).where(self.company_review_crawl.c.company_id==data_list['company_id'])
                resultproxy = self.connection.execute(query)
                resultproxy.close()
            except Exception as e:
                print(e)
            success_input = 0
        return (success_input)
    
    def findOrCreateInformation(self,data_list):
        try:
            query = db.select([self.company_information_crawl]).where(self.company_information_crawl.c.company_name==data_list['company_name'])
            result_proxy = self.connection.execute(query)
            result_set = result_proxy.fetchall()
            result_proxy.close()
        except Exception as e:
            print(e)
        if (len(result_set) < 1):
            try:
                data_list['created_at'] = datetime.datetime.now()
                data_list['updated_at'] = datetime.datetime.now()
                query = db.insert(self.company_information_crawl).values(data_list)
                resultproxy = self.connection.execute(query)
                resultproxy.close()
            except Exception as e:
                print(e)
            success_input = 1
        else:
            try:
                query = db.update(self.company_information_crawl).values(data_list).where(self.company_information_crawl.c.company_name==data_list['company_name'])
                resultproxy = self.connection.execute(query)
                resultproxy.close()
            except Exception as e:
                print(e)
            success_input = 2
        return (success_input)
    
    def storeJobstreetReview(self,data_list,company_name):
        success_input = 0
        for i in range(len(data_list['review_title'])):
            data_input = {}
            data_input['js_company_name'] = data_list['js_company_name'][i]
            data_input['rating'] = data_list['rating'][i]
            data_input['position'] = data_list['position'][i]
            data_input['experience'] = data_list['experience'][i]
            data_input['review_date'] = data_list['review_date'][i]
            data_input['review_title'] = data_list['review_title'][i]
            data_input['good_things'] = data_list['good_things'][i]
            data_input['challenges'] = data_list['challenges'][i]
            try:
                query = db.select([self.jobstreet_review_crawl]).where(db.and_(self.jobstreet_review_crawl.c.review_title==data_list['review_title'][i],self.jobstreet_review_crawl.c.js_company_name==data_list['js_company_name'][i]))
                result_proxy = self.connection.execute(query)
                result_set = result_proxy.fetchall()
                result_proxy.close()
            except Exception as e:
                continue
                print(e)
            if (len(result_set) < 1):
                try:
                    data_input['company_name'] = company_name
                    data_input['created_at'] = datetime.datetime.now()
                    data_input['updated_at'] = datetime.datetime.now()
                    query = db.insert(self.jobstreet_review_crawl).values(data_input)
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
                success_input = success_input + 1
            else:
                try:
                    query = db.update(self.jobstreet_review_crawl).values(data_input).where(db.and_(self.jobstreet_review_crawl.c.review_title==data_list['review_title'][i],self.jobstreet_review_crawl.c.js_company_name==data_list['js_company_name'][i]))
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
        return (success_input)
    
    def storeIndeedReview(self,data_list,company_name):
        success_input = 0
        for i in range(len(data_list['review_title'])):
            data_input = {}
            data_input['ind_company_name'] = data_list['ind_company_name'][i]
            data_input['rating'] = data_list['rating'][i]
            data_input['position'] = data_list['position'][i]
            data_input['location'] = data_list['location'][i]
            data_input['review_date'] = data_list['review_date'][i]
            data_input['review_title'] = data_list['review_title'][i]
            data_input['review'] = data_list['review'][i]
            try:
                query = db.select([self.indeed_review_crawl]).where(db.and_(self.indeed_review_crawl.c.review_title==data_list['review_title'][i],self.indeed_review_crawl.c.ind_company_name==data_list['ind_company_name'][i]))
                result_proxy = self.connection.execute(query)
                result_set = result_proxy.fetchall()
                result_proxy.close()
            except Exception as e:
                continue
                print(e)
            if (len(result_set) < 1):
                try:
                    data_input['company_name'] = company_name
                    data_input['created_at'] = datetime.datetime.now()
                    data_input['updated_at'] = datetime.datetime.now()
                    query = db.insert(self.indeed_review_crawl).values(data_input)
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
                success_input = success_input + 1
            else:
                try:
                    query = db.update(self.indeed_review_crawl).values(data_input).where(db.and_(self.indeed_review_crawl.c.review_title==data_list['review_title'][i],self.indeed_review_crawl.c.ind_company_name==data_list['ind_company_name'][i]))
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
        return (success_input)
    
    def storeGlassdoorReview(self,data_list,company_name):
        success_input = 0
        for i in range(len(data_list['review_title'])):
            data_input = {}
            data_input['gd_company_name'] = data_list['gd_company_name'][i]
            data_input['rating'] = data_list['rating'][i]
            data_input['position'] = data_list['position'][i]
            data_input['work_duration'] = data_list['work_duration'][i]
            data_input['review_date'] = data_list['review_date'][i]
            data_input['review_title'] = data_list['review_title'][i]
            data_input['pros'] = data_list['pros'][i]
            data_input['cons'] = data_list['cons'][i]
            try:
                query = db.select([self.glassdoor_review_crawl]).where(db.and_(self.glassdoor_review_crawl.c.review_title==data_list['review_title'][i],self.glassdoor_review_crawl.c.gd_company_name==data_list['gd_company_name'][i]))
                result_proxy = self.connection.execute(query)
                result_set = result_proxy.fetchall()
                result_proxy.close()
            except Exception as e:
                continue
                print(e)
            if (len(result_set) < 1):
                try:
                    data_input['company_name'] = company_name
                    data_input['created_at'] = datetime.datetime.now()
                    data_input['updated_at'] = datetime.datetime.now()
                    query = db.insert(self.glassdoor_review_crawl).values(data_input)
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
                success_input = success_input + 1
            else:
                try:
                    query = db.update(self.glassdoor_review_crawl).values(data_input).where(db.and_(self.glassdoor_review_crawl.c.review_title==data_list['review_title'][i],self.glassdoor_review_crawl.c.gd_company_name==data_list['gd_company_name'][i]))
                    resultproxy = self.connection.execute(query)
                    resultproxy.close()
                except Exception as e:
                    print(e)
        return (success_input)

