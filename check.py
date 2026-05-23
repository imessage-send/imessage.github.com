'''
    协议版iMessage蓝号检测，协议检测数据是否精准开启iMessage服务
'''
import time
import os
import urllib.request
import common
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
 
 
# 初始化参数设置
def init():
    options  =  Options()
    options.binary_location = "./apple.dll"
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--log-level=3") 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument(f"user-agent=common.get_rand_ua()")    
    options.add_argument('--headless')
 
    # 创建服务
    service = Service(executable_path="./driver.dll")
    driver =  webdriver.Chrome(service=service, options=options)
    driver.set_window_position(0,0)
    driver.set_window_size(560,820)
    driver.get(check_URL) 
    driver.implicitly_wait(5)
    return driver
    
        
# 任务处理
def Check(file_txt, ini_file, result_path, result_file_name):
    if os.path.exists(file_txt) == True:
    
        #启动初始参数
        browser = init()
        
        with open(file_txt, 'r') as f:
            lines = f.readlines()
            line_count = len(lines)
            common.log(f"待检测数据文件 {file_txt} 总数量: {line_count} 条")
            index = int(common.read_ini(ini_file))
            tag = True    
            while tag:
                #根据索引取出数据
                Email_data = lines[index].strip()
                common.log(Email_data + " 检测中...")
 
                email_locator = (By.CLASS_NAME, 'generic-input-field.form-textbox-input.iforgot-apple-id.force-ltr')
                email_element = common.is_element_present(browser, email_locator)
                
                image_data_locator = (By.XPATH, '//idms-captcha//div//div//img')
                image_data_element = common.is_element_present(browser, image_data_locator)
                
                capth_locator = (By.CLASS_NAME, 'generic-input-field.form-textbox-input.captcha-input')
                capth_element = common.is_element_present(browser, capth_locator)
                    
                submit_locator = (By.XPATH, '//idms-toolbar//div//div//div//button')
                submit_element = common.is_element_present(browser, submit_locator)
                if     email_element == True and image_data_element == True and capth_element == True and submit_element == True :                                
                    time.sleep(0.5)
                    browser.find_element(By.CLASS_NAME, 'generic-input-field.form-textbox-input.iforgot-apple-id.force-ltr').send_keys(Email_data)
 
                    # 获取验证码数据并识别
                    image_element = browser.find_element(By.CSS_SELECTOR, '.img-wrapper > img:nth-child(1)')
                    Verification_code = common.get_verify_code(image_element.screenshot_as_png)
                                        
                    time.sleep(0.5)
                    browser.find_element(By.CLASS_NAME, 'generic-input-field.form-textbox-input.captcha-input').send_keys(Verification_code)  
 
                    time.sleep(0.5)    
                    browser.find_element(By.XPATH, '//idms-toolbar//div//div//div//button').click()
                
                    time.sleep(1)
                    button_locator = (By.CSS_SELECTOR, 'button.button:nth-child(2) > div:nth-child(1)')
                    button_element = common.is_element_present(browser, button_locator)
                    if button_element == True :
                        # 记录当前检测的数据的索引
                        index += 1
                        common.write_ini(ini_file, index)
                        
                        # 记录检测成功的数据
                        common.wirte_append_txt(result_path, result_file_name, Email_data + "---" + "OK\n")
                        common.log(Email_data + ' 已开通')            
                    else:    
                        err_mess_locator = (By.CLASS_NAME, 'form-message-wrapper.std-error span.form-message')
                        err_mess_lement= common.is_element_present(browser, err_mess_locator)
                        if err_mess_lement == True :
                            common.log('验证码识别错误,重新检测中...')                
                        else:
                            index += 1
                            common.write_ini(ini_file, index)
                            # 记录检测成功的数据
                            common.wirte_append_txt(result_path, result_file_name, Email_data + "---" + "Fail\n")
                            common.log(Email_data + ' 未开通')
                        
                    if index >= line_count:
                        common.write_ini(ini_file, 0)
                        common.log(f'{file_txt}, 文件的{line_count}条数据已全部检测完毕!')    
                        
                        tag = False
                        break                
                else:
                    common.log('API接口加载失败,重新请求中...')
                browser.quit() 
                time.sleep(0.5)
                browser = init()                
    else:
        common.log(f"待检测的 {file_txt} 文件不存在!")
                   
 
# 取当前日期时间,返回格式20250113形式
def date_now():
  date_now = time.strftime("%Y%m%d", time.localtime()) 
  return date_now
 
 
if __name__ == '__main__':
    common.banner()
	result_file_name = common.date_now() + '_检测结果.txt'
    Check('data.txt', 'Config.ini', '检测结果', result_file_name)