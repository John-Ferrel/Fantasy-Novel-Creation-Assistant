
import requests

def ask_anythingllm(question, workspace_name, api_key):    
    url = f"http://localhost:3001/api/v1/workspace/{workspace_name}/chat"    
    headers = {        
        "Authorization": f"Bearer {api_key}",        
        "Content-Type": "application/json",        
        "accept": "application/json"    
    }    
    data = {        
        "message": question,        
        "mode": "chat"  # 可选chat/query模式    
    }    
    response = requests.post(url, headers=headers, json=data)    
    if response.status_code == 200:        
        result = response.json()        
        # 提取有效回答（去除思考过程）        
        answer = result['textResponse'].split('</think>')[-1].strip()        
        sources = result.get('sources', [])        
        return answer, sources    
    else:        
        return f"Error: {response.text}", []
    # 示例调用
api_key = "GMHM9V4-GZJM737-NYRK3KS-77K9TNK"  #替换成你自己的apikey
workspace = "novel-test"  # 替换成你创建的工作空间名称
question = "《老子》讲的是什么，用200个字概括"
answer, sources = ask_anythingllm(question, workspace, api_key)
print("回答:", answer)
print("来源:", [src['title'] for src in sources])