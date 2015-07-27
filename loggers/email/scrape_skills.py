    
from bs4 import BeautifulSoup
from selenium import webdriver
import time

driver = webdriver.Firefox()
skills = set()
driver.get('https://www.itsyourskills.com/skills-profile')
time.sleep(5)
def getSkills(driver):
    global skills
    stop_text = ['Functional / Technical Skills', 'General Behavioral / Cognitive Skills', 'Click to expand' ] 
    html = driver.page_source
    old_driver = driver
    soup = BeautifulSoup(html)
    clss = ['','text-warning']
    #print soup.findAll("a", {'class':['','text-warning']})
    lis = soup.findAll("li", {"class": "iysTreeLi parent_li", "collapse": "open"})
    print len(lis)
    if(len(lis)>0):
        t =  lis[-1].findAll("a", {'class':['','text-warning']})
        print len(t)
        for tg in t:
            print 'tags-', tg.text
    #print type(lis.prettify())

    for tag in lis[-1].findAll("a", {'class':['','text-warning']}):
        if(len(dict(tag.attrs)["class"]) > 1):
            continue
        skills.add(tag.text)
        #print tag.text
        print ' '
        if tag.text.lstrip() in stop_text:
            continue
        link = driver.find_element_by_partial_link_text(tag.text.lstrip())
        link.click()
        time.sleep(5)
        getLabels(driver)
        getSkills(driver)
        print "done"
        print 'Testing', link.find_element_by_xpath('..').find_element_by_xpath('..')


def getLabels(driver):
    global skills
    flag = False
    stop_text = [ 'Skills ',  'Some sample job profiles', '']
    html = driver.page_source
    soup = BeautifulSoup(html)
    for tg in soup.findAll("label"):
        if tg.text.lstrip() in stop_text:
            continue
        skills.add(tg.text.lstrip())
        flag = True
        #print tg.text
    return flag


html = driver.page_source
soup = BeautifulSoup(html)
stop_text = ['Functional / Technical Skills', 'General Behavioral / Cognitive Skills', 'Click to expand' ] 
for tag in soup.findAll("a", {'class':['','text-warning']}):
    if(len(dict(tag.attrs)["class"]) > 1):
        continue
    skills.add(tag.text)
    #print tag.text
    print ' '
    if tag.text.lstrip() in stop_text:
        continue
    link = driver.find_element_by_partial_link_text(tag.text.lstrip())
    link.click()
    time.sleep(5)
    getSkills(driver)
    print "done"



