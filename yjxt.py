import js2xml

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

EnumA = ['一', '二', '三', '四', '五', '六', '七',
         '八', '九', '十', '十一', '十二',
         '上午', '下午', '晚上']


def login(login_driver, username, password):
    login_driver.get('http://yjxt.bupt.edu.cn')
    username = login_driver.find_element(By.ID, 'username')
    username.send_keys(username)

    password = login_driver.find_element(By.ID, 'password')
    password.send_keys(password)

    button = login_driver.find_element_by_class_name('btn-lg')
    button.click()


def get_payload(get_payload_driver):
    # 课程表所在页面的url不是固定的，需要从js代码中提取
    get_payload_driver.switch_to.frame('MenuFrame')
    source = get_payload_driver.page_source

    soup = BeautifulSoup(source, 'html.parser')
    script = soup.select('body form script')[1].string

    # 使用js2xml格式化之后再使用xpath提取js代码中附加的url
    script_text = js2xml.parse(script, debug=False)

    for x in script_text.xpath("//object/property[@name = 'url']/string/text()"):
        if x[:21] == 'Course/StuCourseQuery':
            return x


def get_course_html(get_course_html_driver, payload):
    get_course_html_driver.get('http://yjxt.bupt.edu.cn/Gstudent/' + payload)
    return get_course_html_driver.page_source


def next_pic(pic, x, y):
    for i in range(x, 11):
        if i == x:
            for j in range(y, 9):
                if pic[i][j] == 0 and j != y:
                    return i, j
        else:
            for j in range(9):
                if pic[i][j] == 0:
                    return i, j


def analysis_html(html):
    # 解析html

    # 获取table
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(id='contentParent_dgData')

    # 解析table
    pic = [[0 for i in range(9)] for i in range(11)]
    row = 0
    column = 0

    for x in table.find_all('td'):
        if x.string != '\n':
            try:
                rowspan = int(x['rowspan'])
            except AttributeError as e:
                rowspan = 1

            for i in range(rowspan):
                pic[row + i][column] = 1

            if x.string.strip().encode('utf-8') in EnumA:
                row, column = next_pic(row, column)
                continue
            else:
                print(x.string.strip().encode('gbk'), '周'.decode('utf-8').encode('gbk'),
                      column, row + 1, '-', row + rowspan)
        else:
            row, column = next_pic(row, column)


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    login(driver, 'xxxxxxxx', 'xxxxx')
    payload = get_payload(driver)
    html = get_course_html(driver, payload)
    analysis_html(html)
    driver.quit()
