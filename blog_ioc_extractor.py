from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
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
        soup = BeautifulSoup(page_content, "html.parser")
        content = soup.get_text(separator="\n", strip=True)  # 提取纯文本
        return content
    except Exception as e:
        print(f"Selenium 抓取失败: {e}")
        return ""
    finally:
        driver.quit()  # 确保浏览器退出

def save_webpage_content(filename, content):
    """
    将网页内容保存到指定的文件中。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"网页内容已保存到文件: {filename}")
    except Exception as e:
        print(f"保存网页内容失败: {e}")

def query_ollama(model_name, prompt):
    """
    调用 Ollama 模型 API，发送抓取的网页内容。
    """
    api_url = "http://127.0.0.1:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    try:
        # 向 Ollama API 发送请求
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        # 打印原始响应内容以调试
        print("原始响应内容：")
        print(response.text)

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
    webpage_content = fetch_webpage_with_selenium(url)

    # 2. 检查抓取结果
    if not webpage_content:
        print("未能成功抓取网页内容。")
    else:
        print("网页内容抓取成功。")

        # 3. 保存抓取的网页内容到文件
        save_webpage_content("webpage_content.txt", webpage_content)

        # 4. 构造 Prompt 并调用 Ollama
        model_name = "qwen2.5:latest"
        prompt = f"""
        Analyze the following cybersecurity blog content and extract Indicators of Compromise (IoCs). 
        Present the extracted information in JSON format with the following fields:
        1. `source`: "{url}"
        2. `extracted_time`: Current timestamp in ISO 8601 format.
        3. `ioc`: A nested object containing the extracted IoCs categorized as:
           - `file_hashes`: List of file hashes (e.g., MD5, SHA256).
           - `domains`: List of malicious domains.
           - `ip_addresses`: List of IP addresses.
           - `urls`: List of malicious URLs.
           - `email_addresses`: List of malicious or phishing-related email addresses.
           - `file_names`: List of filenames associated with the attack.
           - `registry_keys`: List of relevant registry keys.
           - `mutexes`: List of mutex names.
           - `commands`: List of commands executed during the attack.
           - `processes`: List of process names.
        4. `context`: A nested object with:
           - `related_actors`: Known threat actors associated with the IoCs.
           - `malware_families`: Malware families mentioned in the content.
           - `attack_tactics`: Techniques or tactics (e.g., phishing, exploitation).
           - `detection_recommendations`: Security measures mentioned.

        Blog Content:
        {webpage_content}
        """
        print("正在向 Ollama 发送请求...")
        response = query_ollama(model_name, prompt)

        # 5. 保存返回结果到文件
        if response:
            save_to_file("ollama_analysis_result.txt", response)
        else:
            print("未能获取有效的分析结果。")
