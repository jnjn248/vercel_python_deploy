from flask import Flask, request, Response, render_template
from openai import OpenAI
import os
import json

app = Flask(__name__)

# 配置OpenAI客户端
client = OpenAI(
    api_key=os.getenv("API_KEY", 'sk-IOl994QEkmV6MyOIAbEd91C3729043De986e6a160a3f2362'),
    base_url=os.getenv("API_BASE", "http://maas-api.cn-huabei-1.xf-yun.com/v1")
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    def generate():
        try:
            response = client.chat.completions.create(
                model="xdeepseekr1",
                messages=[{"role": "user", "content": data['message']}],
                stream=True,
                temperature=0.7,
                max_tokens=4096,
                extra_headers={"lora_id": "0"},
                stream_options={"include_usage": True}
            )

            for chunk in response:
                content = ""
                
                if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                    content += chunk.choices[0].delta.reasoning_content or ""
                
                if hasattr(chunk.choices[0].delta, 'content'):
                    content += chunk.choices[0].delta.content or ""
                
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# Vercel 需要导出一个名为 app 的实例
if __name__ == '__main__':
    app.run(debug=True)
