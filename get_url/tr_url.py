from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
# trellix_research的url提取
desired_count = 50  # 设定要提取的文章链接数量
# 设置无头模式
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 启动浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 打开网页
url = "https://www.trellix.com/blogs/research/"
driver.get(url)
driver.implicitly_wait(10)

# 初始化提取的链接列表
extracted_links = []


while len(extracted_links) < desired_count:
    # 查找“Show More”按钮并点击
    try:
        show_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show More')]")
        # 替换 show_more_button.click() 为以下代码
        driver.execute_script("arguments[0].click();", show_more_button)

        time.sleep(2)  # 等待内容加载
    except Exception as e:
        print("无法找到 'Show More' 按钮，可能已经加载完所有内容:", e)
        break

    # 获取当前页面中的文章链接
    articles = driver.find_elements(By.CSS_SELECTOR, "#searchResultAndPagination .row.small-post.topiclisting a")
    for article in articles:
        link = article.get_attribute("href")
        if link not in extracted_links:
            extracted_links.append(link)
        # 检查是否达到了所需的链接数量
        if len(extracted_links) >= desired_count:
            break

# 将链接保存到文件
with open("article_urls.txt", "w", encoding="utf-8") as file:
    for link in extracted_links:
        file.write(f"{link}\n")

# 关闭浏览器
driver.quit()

print(f"已成功从trellix_research提取 {len(extracted_links)} 个链接。")
