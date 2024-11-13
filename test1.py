from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time


def fetch_webpage_with_selenium(url):
    """
    使用 Selenium 模拟浏览器抓取动态网页内容（无头模式）。
    """
    # 配置无头模式
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # 禁用 GPU 渲染
    options.add_argument("window-size=1920x1080")  # 设置窗口大小以适应网页

    # 启动 ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # 等待页面完全加载
    time.sleep(5)  # 根据实际情况调整等待时间

    try:
        # 获取页面源代码
        page_content = driver.page_source
        return page_content
    except Exception as e:
        print(f"Selenium 抓取失败: {e}")
        return ""
    finally:
        driver.quit()  # 确保浏览器退出


def query_ollama_for_main_content(model_name, webpage_html):
    """
    调用 Ollama 模型 API，分析网页 HTML，提取主要内容和图片描述。
    """
    api_url = "http://127.0.0.1:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    prompt = f"""
    以下是一个网页的 HTML 内容，请分析并提取该网页中的主要文章内容和图片的描述。
    请忽略以下内容：脚本代码（如 `<script>` 标签）、广告、导航、页脚等不相关的部分。
    只提取以下内容：
    1. **标题**：提取文章的标题（如果有）。
    2. **段落内容**：提取与该网页相关的主要正文内容。
    3. **图片信息**：提取图片的链接（`src`）以及描述（`alt`）属性。

    请确保提取的内容简洁明了，重点突出，包含所有与主题相关的核心信息。

    网页 HTML:
    {webpage_html}

    请以易于阅读的格式返回。
    """

    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        # 向 Ollama API 发送请求
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        # 尝试将响应内容解析为 JSON
        try:
            response_data = response.json()
            return response_data.get("response", "未返回有效数据")
        except ValueError:
            print("响应内容不是有效的 JSON 格式，将直接返回原始文本内容。")
            return response.text
    except requests.RequestException as e:
        print(f"Ollama 请求失败: {e}")
        return ""

def save_to_file(filename, content):
    """
    将内容保存到指定的文件中。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"结果已保存到文件: {filename}")
    except Exception as e:
        print(f"保存文件失败: {e}")


if __name__ == "__main__":
    # 网页链接
    url = "https://www.trellix.com/blogs/research/new-stealer-uses-invalid-cert-to-compromise-systems/"

    # 1. 抓取网页内容
    print("正在抓取网页内容（无头模式）...")
    page_content = fetch_webpage_with_selenium(url)

    # 2. 检查抓取结果
    if not page_content:
        print("未能成功抓取网页内容。")
    else:
        print("网页内容抓取成功。")

        # 3. 使用 Ollama 模型提取主要内容和图片信息
        model_name = "qwen2.5:latest"
        print("正在调用 Ollama 提取网页主要内容和图片信息...")
        response = query_ollama_for_main_content(model_name, page_content)

        # 4. 保存提取的主要内容到文件
        if response:
            save_to_file("ollama_extracted_main_content.txt", response)
        else:
            print("未能获取有效的主要内容。")
