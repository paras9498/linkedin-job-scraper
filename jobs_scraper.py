import json
import os
import random
import time
from copy import deepcopy
import requests
from bs4 import BeautifulSoup


# Main class to handle job scraping from LinkedIn
class CRAWLER(object):
    def __init__(self):
        self.location = 'Alabama, US'
        self.baseUrl = 'https://www.linkedin.com/jobs'
        
        # Headers to mimic a browser request
        self.getHeaders = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'csrf-token': '',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        
        # Headers specific for HTML responses
        self.htmlHeaders = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'content-type': 'text/html; charset=utf-8',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        # Setting up a session and initial job object structure
        self.session = requests.session()
        self.domain = 'linkedin.com'
        self.obj = {'title':'','location':'','description':'','domain': '', 'url': '', 'company': '','company_url':''}
        self.allJobs = []
        self.iserror = False
        
        
    # Function to save job data to a JSON file
    def save_to_json_file(self,filename):
        # If the file already exists, we load the existing data and append new jobs
        if os.path.exists(filename):
            with open(filename, 'r+') as file:
                try:
                    # Load existing data
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    # If the file is empty or invalid, start with an empty list
                    existing_data = []

                # Append new data
                existing_data.extend(self.allJobs)
                file.seek(0)  # Move the file pointer to the start of the file for overwriting

                # Write updated data back to the file
                json.dump(existing_data, file, indent=4)
        else:
            # If the file doesn't exist, create it and write the data
            with open(filename, 'w') as file:
                json.dump(self.allJobs, file, indent=4)
        
    # Function to handle HTML request  
    def html_request(self, url):
        mycount = 0
        while True:
            try:
                # Fetching the response from the given URL
                res = self.session.get(url, headers=self.htmlHeaders)
                if res.status_code == 200:
                    return True, res
                time.sleep(random.randint(1, 3))
            except Exception as e:
                print(e)
           
            mycount = mycount + 1
            if mycount > 30:
                break
        return False, False

    # Function to handle GET request with retries
    def get_request(self, url):
        mycount = 0
        while True:
            try:
                res = self.session.get(url, headers=self.getHeaders)
                if res.status_code == 200:
                    return True, res
                time.sleep(random.randint(1, 3))
            except Exception as e:
                print(e)
            print("Trying again to fetch data")
            mycount = mycount + 1
            if mycount > 30:
                break
        return False, False

    # Function to decode HTML encoded characters
    def html_decode(self, s):
        htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;'),
            (' ', '&nbsp;')
        )
        for code in htmlCodes:
            s = s.replace(code[1], code[0])
        return s
    
    # Function to extract job details
    def get_details(self, links):
        try:
            for link in links:
                try:
                    # Deepcopy to ensure job object structure isn't overwritten
                    jobObj = deepcopy(self.obj)
                    joburl = link.get('href')
                    jobObj['url'] = joburl.split('?')[0]
                    isloaded, jobres = self.get_request(joburl)
                    if isloaded:
                        jobObj['title'] = link.text.strip().lower()
                        # Parsing HTML response for job details
                        jobdetails = BeautifulSoup(jobres.text, 'lxml')
                        company = jobdetails.find('a', {'class': 'topcard__org-name-link topcard__flavor--black-link'})
                        try:
                            location = jobdetails.find('span', {'class': 'topcard__flavor topcard__flavor--bullet'}).text.strip()
                        except:
                            pass
                        if location == "":
                            location='No Location'
                        description = jobdetails.find('div', {'class': 'description__text description__text--rich'})
                        
                        # Checking for Apply Button
                        apply = "?apply=no"
                        isapply = False
                        if jobdetails.find('button',{'data-tracking-control-name': 'public_jobs_apply-link-onsite'}):
                            isapply = jobdetails.find('button',{'data-tracking-control-name': 'public_jobs_apply-link-onsite'})
                            if isapply:
                                apply = "?apply=yes"
                        if not isapply and jobdetails.find('button',{'data-tracking-control-name': 'public_jobs_apply-link-simple_onsite'}):
                            isapply = jobdetails.find('button',{'data-tracking-control-name': 'public_jobs_apply-link-simple_onsite'})
                            if isapply:
                                apply = "?apply=yes"
                        jobObj['url'] += apply
                        jobObj['company'] = company.text.strip()
                        jobObj['location'] = location
                        jobObj['description'] = str(description)
                        
                        # Handling JSON data for job description
                        try:
                            description = jobdetails.find('script', {'type': 'application/ld+json'})
                            jsn = json.loads(description.text)
                            jobObj['description'] = self.html_decode(jsn['description'])
                        except:
                            pass
                        
                        # Get company URL if available 
                        try:
                            if company:
                                company_url = company.get('href').split("?")[0]
                                jobObj['company_url'] = company_url  
                        except:
                            pass
                        jobObj['domain'] = 'linkedin.com'
                        # Append valid job objects to the job list
                        if jobObj['title'] != '' and jobObj['url'] != '':
                            self.allJobs.append(jobObj)
                            print(
                                jobObj['title'] + "\n" + jobObj['location'] + "\n" + jobObj['company'] + "\n" + jobObj[
                                    'url'])
                except:
                    pass
            
        except Exception as e:
            print(e)
            pass
        
    # Main logic to process job listing search and scraping
    def process_logic(self):
        isload, res = self.html_request(self.baseUrl)
        # Capture CSRF token from the cookies
        if 'JSESSIONID' in res.cookies.get_dict():
            self.getHeaders['csrf-token'] = res.cookies.get_dict()['JSESSIONID']
        key_locs =[{'location':'alabama',
                   'keyword':"software"}]
        for dic in key_locs:
            loc = dic['location']
            key = dic['keyword']
            numcount = 0
            try:
                time.sleep(2)
                ispage = True
                page = 0
                while ispage:
                    newurl = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={key.replace(" ", "+")}&location={loc.replace(" ", "+")},United%20States&geoId=&f_TPR=r86400&trk=public_jobs_jobs-search-bar_search-submit&start={page}'
                    print(newurl)
                    print(f'collecting page after {str(page)} {key}')
                    page += 10
                    isloaded, res = self.get_request(newurl)
                    csrf = self.session.cookies.get_dict()['JSESSIONID']
                    self.getHeaders['csrf-token'] = str(csrf)
                    if isloaded:
                        soup = BeautifulSoup(res.text, "lxml")
                        links = soup.find_all('a', {
                            'class': 'base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]'})
                        if links:
                            self.get_details(links)
                            #Scrap only two pages
                            if page>=20:
                                ispage =  False
                            numcount += len(links)
                            filename= 'linkedin_jobs.json'
                            self.save_to_json_file(filename)
                            self.allJobs = []
                        else:
                            print(res)
                            ispage = False
                    else:
                        print(res)
                        ispage = False
            except Exception as e:
                print(e)
                self.iserror = True
            


if __name__ == "__main__":
    scraper = CRAWLER()
    scraper.process_logic()
    print(len(scraper.allJobs))


