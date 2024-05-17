from pathlib import Path
from openai import OpenAI
from jinja2 import Template

#Kimi API


class KimiBot:
    def __init__(self):
        self.client = OpenAI(
            api_key = "sk-iIZgUGHpHl6xSsb8QOq9OZhdpQmUXPNxkzOVZQVDUdq8dfFf",
            base_url = "https://api.moonshot.cn/v1",
        )

        self.role = '''
          #ROLE#
          你是一位资深的营销文案写作专家，深谙人性特点，擅长通过文笔吸引目标客户的目光
          '''
       
        self.model = 'moonshot-v1-8k'
    
    #kwargs为字典类型的prompt
    def get_messages(self,**kwargs):
        template_string = """
          # 上下文 #
          {{context}}
          # 写作目标#
          {{goal}}
          # 文字风格 #
          {{style}}
          # 表达语气 #
          {{tone}}
          # 读者画像 #
          {{audience}}
          # 输出要求 #
          {{output}}
         """
        template = Template(template_string)
        rendered_template = template.render(**kwargs)
        
        messages = [
           {
            "role": "system",
            "content":self.role,
            },

             {
            "role": "user",
            "content": rendered_template
           },
       ]
        
        return messages

    def response(self,**kwargs):
        messages = self.get_messages(**kwargs)
        completion = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = 0.7,
        )
        print(completion)
        res = completion.choices[0].message.content


        return res


#调动文件
'''
file_object = client.files.create(file=Path("/Users/wangjohnson/downloads/WechatIMG1445.jpg"), purpose="file-extract")

file_content = client.files.content(file_id=file_object.id).text
'''


if __name__ == '__main__':
     kimi_bot = KimiBot()
     kimi_bot.response()
