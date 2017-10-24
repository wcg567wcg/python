#coding=utf-8

# install chromedriver
# https://sites.google.com/a/chromium.org/chromedriver/
#
# unzip chromedriver and add the path to ~/.bashrc
#

from selenium import webdriver
import time

url_dict = {
    'iReader Plus 黑' 
        : 'https://detail.tmall.com/item.htm?spm=a1z10.5-b-s.w4011-14439296382.49.s2cXT1&id=530386199851&sku_properties=5919063:6536025',
    'iReader 青春版' 
        : 'https://detail.tmall.com/item.htm?spm=a230r.1.14.6.JsOheI&id=550673734838',
    'Kindle 基本款' 
        : 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-16522198144.3.35TBaC&id=534274368086&sku_properties=5919063:6536025',
    'Kindle PaperWhite 3' 
        : 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.1.2Jz0PN&id=522680881881',
    'Kindle Voyage' 
        : 'https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-16522198144.54.35TBaC&id=522686700744',
    '当当电子书' 
        : 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.6.I6lT6O&id=527714448328',
    'QQ阅读电子书' 
        : 'https://detail.tmall.com/item.htm?spm=a1z10.3-b.w4011-16636505510.42.149d0431jHy7rB&id=555910053652&rn=4679eb02347d211f5686ec4d13cc9867&abbucket=4&sku_properties=1627207:28341',
}

class BrowserData:
    def __init__(self, browser, url):
        self.browser = browser
        self.browser.get(url)

    def count(self):
        count = 0
        try:
            count = browser.find_element_by_xpath(".//*[@id='J_DetailMeta']/div[1]/div[1]/div/ul/li[1]/div/span[2]").text.encode('utf-8')
        except Exception as err:
            print(err)
            count = -1
        finally:
            return count

def output_sales(browser, info, url):
    data = BrowserData(browser, url)
    print '{0}        当日月销量为: {1}\n'.format(info, data.count())

def log_date():
    print time.strftime('%Y-%m-%d',time.localtime(time.time()))

if __name__ == '__main__':
    log_date()

    browser = webdriver.Chrome()
    browser.set_window_size(1,1)

    for (info, url) in url_dict.items():
        output_sales(browser, info, url)

    #exit
    browser.quit()
