from pathlib import Path
from openai import OpenAI
#Kimi API
client = OpenAI(
    api_key = "sk-iIZgUGHpHl6xSsb8QOq9OZhdpQmUXPNxkzOVZQVDUdq8dfFf",
    base_url = "https://api.moonshot.cn/v1",
)

'/Users/wangjohnson/downloads/WechatIMG1445.jpg'

file_object = client.files.create(file=Path("/Users/wangjohnson/downloads/WechatIMG1445.jpg"), purpose="file-extract")

file_content = client.files.content(file_id=file_object.id).text

role = '''
          #ROLE#
          你是一位资深的营销文案写作专家，深谙人性特点，擅长通过文笔吸引目标客户的目光
      '''
promt = '''
          # 上下文 #
          我想为我自己的新产品做广告。我公司的名字叫，产品叫宜肤肌密，是一种抗衰效果显著的精华护肤产品。
          # 写作目标#
          为我创建一个朋友圈帖子，旨在让人们点击产品链接进行购买。
          # 文字风格 #
          使用朋友间真诚交流的风格。
          # 表达语气 #
          平和、自然、接地气，但一定要有说服力的
          # 读者画像 #
          产品在朋友圈上的受众群通常是我的私人好友，以针对这些受众在护肤产品中通常想要的需求进行编写。
          # 输出要求 #
          朋友圈的帖子简洁而有影响力。
      '''

completion = client.chat.completions.create(
    model = "moonshot-v1-8k",
    messages = [
        {
            "role": "system",
            "content":role,
            },

             {
            "role": "user",
            "content": promt,
           },
    ],
    temperature = 0.7,
)



print(completion.choices[0].message.content)
