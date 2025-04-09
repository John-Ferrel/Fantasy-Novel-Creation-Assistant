import requests

# 替换为实际的 API 端点
api_url = "http://localhost:3001/api/v1/workspace/new"

# 身份验证，设置请求头
headers = {
    "accept": "application/json",
    "Authorization": "Bearer GMHM9V4-GZJM737-NYRK3KS-77K9TNK",  #注意，替换apikey一定要保留Bearer 
    "Content-Type": "application/json"
}

# 准备创建工作区所需的数据
workspace_data = {   
    "name": "novel-test", #我这里创建的 ddj，替换成你的工作空间
    "similarityThreshold": 0.7,    
    "openAiTemp": 0.7,  
    "openAiHistory": 20, 
    "openAiPrompt": "Custom prompt for responses",    
    "queryRefusalResponse": "Custom refusal message",    
    "chatMode": "chat",   
    "topN": 4
}

try:
    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=workspace_data)

    # 检查响应状态码
    if response.status_code == 200:  # 200 表示创建成功
        result = response.json()
        print("工作区创建成功：", result)
    else:
        print(f"工作区创建失败，状态码：{response.status_code}，错误信息：{response.text}")
except requests.RequestException as e:
    print(f"请求发生错误：{e}")

