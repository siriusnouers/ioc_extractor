import requests
import json


def filter_article_content(article_text, model_name="qwen2.5:latest"):
    """
    使用大语言模型来过滤文章中的无效信息，保留真正的内容。

    Parameters:
    - article_text (str): 需要过滤的文章全文。
    - model_name (str): 要调用的大模型名称。

    Returns:
    - filtered_content (str): 经过过滤后的文章内容。
    """
    # Define API endpoint and headers
    api_url = "http://127.0.0.1:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    # Define the prompt to filter out irrelevant information
    prompt = f"""你是一个智能助手，你的任务是从以下文章中找到主要内容，去除无效的新闻、宣传以及不相关的部分：
    \n文章内容：\n{article_text}\n
    请返回这篇文章中真正与主题相关的内容。"""

    # Construct request payload
    data = {
        "model": model_name,
        "prompt": prompt,
        "temperature": 0.7,  # Adjust this to control randomness
    }

    try:
        # Send POST request to the API
        response = requests.post(api_url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        # Collect the streamed response and concatenate it into a final result
        filtered_content = ""
        for line in response.iter_lines():
            if line:
                # Parse each line as JSON
                try:
                    json_line = json.loads(line)
                    if "response" in json_line:
                        filtered_content += json_line["response"]
                except json.JSONDecodeError:
                    print("解析流式响应失败:", line)

        return filtered_content
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return ""


# Example usage
if __name__ == "__main__":
    # Placeholder for article text to be filtered
    article_text = """
    [一些无关的新闻信息...]
    本文将介绍一个最新的恶意软件，它通过伪造证书来窃取用户数据。
    [一些宣传性内容...]
    恶意软件名为 Fickle Stealer，基于 Rust 编写，并通过钓鱼邮件等方式传播。
    [更多无关的信息...]
    """

    filtered_content = filter_article_content(article_text)
    if filtered_content:
        print("过滤后的内容：")
        print(filtered_content)
    else:
        print("未能获取有效的过滤结果。")
