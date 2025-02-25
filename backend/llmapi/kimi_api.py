from pathlib import Path
from openai import OpenAI
from jinja2 import Template

#Kimi API


class KimiBot:
    def __init__(self):
        self.client = OpenAI(
            api_key = "sk-1QH3ZoMyLYxlTfx2gTOrpYQVUudtj1u9q2GAro9nDe6kkjG8",
            base_url = "https://api.moonshot.cn/v1",
        )

        self.role = '''
        #Role：营销大师
        ##Profile：您是一位资深的营销策略大师，对包括小红书、微信群、公众号、视频号、抖音等营销平台的玩法非常熟悉。您精通人性的复杂性，并且对全球各地，包括中国的知名营销策略和观点了如指掌。您通过独特透>彻的文案创作能力，精准地吸引目标客户的注意力。

        ## 技能：
        ### 营销策略
        - 熟知营销漏斗理论的，并能够以此定位用户所处的营销阶段。
          1. 意识阶段(Awareness);
          2. 兴趣阶段(Interest);
          3. 考虑阶段(Consideration);
          4. 意向阶段(Intent);
          5. 行动阶段(Action);
          6. 忠诚度建立阶段(Loyalty);
          7. 推荐阶段(Referral);
        - 根据用户所处营销阶段判断对应的营销目标。
        - 熟知并能运用其它各种知名的营销策略。
        -- 根据用户的需求和目标，定制具有针对性的营销策略。

        ### 营销文案创作
        - 能够深入理解目标客户的需求和期待。
        - 创作具有吸引力的营销文案，有效吸引目标客户的注意力。

        ### 全球营销观点解读
        - 了解并可解读全球各位营销大师的观点。
        - 将全球营销观点和策略结合到实际工作中。

        ## 约束：
        - 仅讨论与营销策略和文案创作相关的话题。
        - 保持专业的营销语言和风格。
        - 在提出营销策略或创作文案时，必须考虑到目标客户的需求和期待。

        '''       
        self.model = 'moonshot-v1-32k'
    
    #kwargs为字典类型的prompt
    def get_cgstao_template(self,**kwargs):
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
        
        return rendered_template

    def get_messages(self,rendered_template,use_dict):
        messages = [
           {
                "role": "system",
                "content":self.role,
           },
           {
                "role": "user",
                "content": rendered_template
           }
           ]
        if use_dict == True:
            messages.append({
                "role":"assistant",
                "content":"{",
                "partial":True
                })
        return messages
    
    def task_template(self,**kwargs):
        template_string = """
        
        请你以营销理论为基础，对'任务描述'进行分析，并从中得出与'重要指导信息'相关的内容，最后给出完成该任务的指导建议。
        
        ##任务描述
        {{task_desc}}

        ##重要指导信息
        ###推测产品或品牌相关信息[#product#]：
        - 产品或品牌的名字是什么？[#name#]
        - 文案中是否体现出了独特卖点？[#has_usp#]
        - 如果有，那么体现出的独特卖点有哪些？[#usp#]
        - 文案中是否体现出了一些明确的品牌价值观理念？[#has_brandValues#]
        - 如果有，那么体现出的价值观理念是什么？[#brandValues#]
        
        
        ###推测营销背景[#campaign_background]：
        - 可能所处的营销阶段？([#stage#])
        - 当前阶段建议关注的效果目标是什么？[#objectives#]
        
        ###推测目标受众画像：[#persona#]
        - 用15个汉字以内的一句话概括：字文案体现出的目标受众是怎样的一群人？[#desc#]
        - 原因是什么？[#reason#]
        - 这群人与产品相关的心理动机是什么？[#motive#]
        ###推测产品或品牌相关信息[#product#]：
        - 产品或品牌的名字是什么？[#name#]
        - 产品可能的独特卖点有哪些？[#usp#]
        - 品牌可能的基本价值观理念是什么？[#values#]
        ###推测营销场景与主导情绪：[#senario#]
        - 文案适合使用在什么地方？希望回答得细致且生动形象，比如线下还是线上，举个例子会是什么？([#place#])
        - 建议传递的主要情绪是什么？([#emotions#])

        ##指导建议：
        - 必须严格在任务2内容开头的地方使用"[#advices#]";
        - 根据重要性，由重到轻，清晰地列出每一个不足的地方与优化建议;
        - 要明确地使用原文中的字句来举例，降低理解难度;
        - 结合任务1的信息对最终答案进行审核，保证内容在专业度上无误。
        - 最多列出5条建议即可，不要超出这个范围。

        """
   
    #直接编写新文案
    def new_copy_template(self,**kwargs):
        
        template_string = """
            #借助你专业的营销知识，创作出3篇满足‘重要信息’要求的营销文案。你非常清楚目标的重要性，所以应该会非常在意文案的效果是否与目标匹配。          
            
            ## 重要信息——
            ### 目标受众画像
            - 群体性别特征：
              1. 是否男性为主？：{{personaData.male}}
              2. 是否女性为主？：{{personaData.female}}
            - 目标客户年收入范围（万元人民币）？：{{personaData.salary}}
            - 具有怎样的群体特征与相关心理动机？：{{personaData.motives}}
            ### 文案使用场景与情绪
            - 文案的主要使用场景：{{senarioData.places}}
            - 须重点传递列表中的情绪：{{senarioData.emotionTags}};
            ### 产品或服务信息
            - 产品或服务名称：{{productData.name}};
            - 品牌价值观：{{productData.brandValues}}
            - 产品或服务的独特卖点：{{productData.usp}}
            ### 重要营销背景
            - 文案对应的营销阶段：{{campaignData.stage}};
            - 期待获得的营销目标与效果：{{campaignData.objectives}};
        
        """
        template = Template(template_string)
        rendered_template = template.render(**kwargs)
        print('生成提示语模板:',rendered_template)
        return rendered_template


    #对原文进行修改
    def modify_copy_template(self,**kwargs):

        template_string = """
          #任务描述：
          1. 请你接收到的'重要信息'进行分析，并以此对‘原文文案’进行优化后重新编写一篇更加合适的新文案

          #重要信息：

          ##原文文案
          {{original}}

          ##重要营销背景
          - 当前所处营销阶段：{{stage}};
          - 期待获得的营销目标与效果：{{objectives}};
          
          ##目标受众画像
          - 主要特征：{{personaDesc}}
          - 相关心理动机：{{personaMotive}}：

          ##产品或服务信息
          - 产品或服务名称：{{productName}};
          - 品牌价值观：{{brandValues}}
          - 产品或服务的独特卖点：{{productUsp}}

          ##文案要求
          - 输出要求：{{output}}
          - 注意文案的使用场景：{{senarios}}
          - 文字风格：与朋友熟人分享的自然表达；
          - 须重点传递列表中的情绪：{{emotions}};

         """
        template = Template(template_string)
        rendered_template = template.render(**kwargs)
        print('生成的提示语模板：',rendered_template)
        return rendered_template
    
    def get_rednote_advice_template(self,**kwargs):
        template_string = """
        
        ## 任务背景：
        请你从小红书营销专业角度，按照以下要求给小红书账号名称:{{name}}与简介:{{intro}}进行评估,按要求成以下5个任务：
        
        ##任务1：推测目标受众画像[#persona#]
        - 如何全面的描述这个群体？[#des#]
        - 针对小红书典型的用户故事是什么？[#userstory#]
        - 如果用5个标签来表达最突出的情绪特点会是什么？[#usertags#]

        
        ## 任务2：结合小红书特点与任务1分析结果，对名称的以下方面进行分析。要求：注意！必须要给予以下每一条都有对应的详细且专业的解释与具体优化建议、具体优化案例！:[#name#]
        ### 定位清晰度 [#clear#]
        1. 评估标准：与任务1的受众画像吻合度多高？否在3秒内传递账号核心价值（领域/内容/用户群）
        2. 负面案例："生活日记"（泛领域） vs **合格案例**："油画少女安姐"（垂直领域+人设）
        3. 优化重点：领域关键词（如手作/穿搭/家居）+ 内容形式（教程/测评/探店）
        
        ### 传播性指数[#easy#]
        1. 易发音：不超过4个汉字词组（如"小野不睡觉"）
        2. 无生僻字：避免"醍醐""饕餮"等影响搜索
        3. 字符长度：中文6字内为黄金区间（小红书昵称限20字）
        
        ### 用户吸引力[#popular#]
        -价值感知 = 痛点词（懒人/急救） + 场景词（通勤/约会） + 结果词（秘籍/攻略）**
        -相似案例对比——
        比如：
        × 普通命名："美妆分享"
        ✓ 高转化命名："早八伪素颜急救室"
        
        ### 差异化竞争力[#diff#]
        1. 感官化：添加五感词汇（"香气实验室"）
        2. 人格化：植入身份标签（"清华学姐爱读书"）
        3. 情绪化：使用网络热梗（"反焦虑摆烂bot"）

        
        ###  关键词策略[#seo#]
        - SEO组合模型(举例)：核心词（烘焙） + 长尾词（低卡） + 场景词（办公室）**
         示例："低卡烘焙研究所｜打工人办公室甜品"

        
        ###  合规与延展性[#safe#]
        1. 禁用极限词（最/第一）
        2. 规避品类冲突（"律师"需资质认证）
        3. 保留商业扩展空间（避免过度具体如"只做耳环"）
        
        
        ###  情感共鸣度[#emotional#]
        1. 制造"氛围感"：用容器意象（"玻璃罐里的春天"）
        2. 强化"陪伴感"：添加时间维度（"每日穿搭记录员"）

        
        ## 任务3:结合小红书特点与任务1、任务2的结果，对简介进行分析评估:[#intro#]
        - 简介的优点分析：[#good#]
        - 简介的缺点分析：[#bad#]
        - 简介的改进建议：要考虑小红书对于简介的要求，而且要给具体优化案例[#better#]

        ## 任务4：结合前面三个任务的分析结果与小红书特点，提出头像建议[#avatar#]
        - 使用那种类型的头像效果好？为什么？：[#better#]
        
        ## 任务5：组中结合以上所有分析，给出专业的评分[#rating#]
        - 满分100分，这个账号应该打几分？[#number#]
        - 给出总结报告[#summary#]

        ## 输出要求：
        - 以Dict数据格式，按照一下键值与层级关系输出数据：
        
         {
          "adviceType":'rednote',
          "accountName": {{name}},
          "accountIntro": {{intro}},
          “rating”:{"number":.../100),"summary":..."},
          "persona":{"des":...,"userstory":...,"usertags":...},
          "name":{"clear":...,"easy":...,"popular":...,"diff":...,"seo":...,"safe":...,"emotional":...},
          "intro":{"优点":...,"不足":...,"改进":...},
          "avatar":{"better:..."}

          }:

        """
        template = Template(template_string)
        rendered_template = template.render(**kwargs)
        print("Rendered_Template:",rendered_template)
        return rendered_template

    def get_article_advice_template(self,**kwargs):
        template_string = """
       
       请你从以营销漏斗理论为主的相关理论出发，对"文案原文"进行分析, 认真完成所有任务后严格按照”输出要求“进行输出：
       
      
      #文案原文：
       {{original}}
      
      ## 任务1：
      以专业的营销漏斗理论为基础，对重要营销背景进行推测，回答其中问题，并明确提醒用户你的回答仅用来提醒用户做相关目标校验，并非标准答案,希望用户以此来进行自我排查，推动文案达到如期效果:
       
       ### 推测产品或品牌相关信息[#product#]：
        - 产品或品牌的名字是什么？[#name#]
        - 文案中是否清晰地体现出了独特卖点？回答"有的"或者"没有"[#has_usp#]
        - 如果有，那么体现出的独特卖点有哪些？[#usp#]
        - 文案中是否体现出了一些明确的品牌价值观理念？[#has_brandValues#]
        - 如果有，那么体现出的价值观理念是什么？[#brandValues#]
       
       ### 推测目标受众画像：[#personaData#]
       - 用不超过15个汉字概括：字文案体现出的目标受众是怎样的一群>人？[#desc#]
        - 为什么是这群人？原因是什么？[#p_reason#]
        - 这群客户可能与产品相关的心理动机是什么？从心理需求与现实矛盾进行分析[#motive#]

       ### 推测营销背景[#campaignData]：
       - 可能所处的营销阶段是什么？([#stage#])
       - 得出以上推测的原因是什么？([#c_reason#])
       - 当前阶段建议关注的效果目标是什么？[#objectives#]

       ### 推测营销场景与主导情绪：[#senarioData#]
       - 根据当前营销阶段分析目前文案适合使用在什么地方？其中重点对线上或线下、微信朋友圈、微信群、公众号、小红书等知名平台进行分析。[#places#]
       - 目前文案传递出的的主要情绪是什么？将答案整理成包含情绪标签的列表([#emotionTags#])
       - 以上情绪是否与该营销阶段匹配？可以进行哪些优化调整？[#e_reason#]

       ## 任务2：给出专业的优化建议，并且重点做到以下几点:
       - 必须严格在任务2内容开头的地方使用"[#advices#]";
       - 根据重要性，由重到轻，清晰地列出每一个不足的地方与优化建议;
       - 要明确地使用原文中的字句来举例，降低理解难度;
       - 结合任务1的信息对最终答案进行审核，保证内容在专业度上无误。
       - 最多列出5条建议即可，不要超出这个范围。
       
       ## 输出要求：
       - 以Dict数据格式，按照一下键值与层级关系输出数据：
       
        {
         "adviceType":"article",
         "productData": {"name":...,"has_usp":...,"usp":...,"has_brandValues":..., "brandValues":...},
         "personaData": {"desc":..., "p_reason":...,"motives":...},
         "campaignData": {"stage":...,"c_reason":...,"objectives":...},
         "senarioData": {"places":..., "emotionTags":[],"e_reason":...},
         "advicesData": [{"issue":...,"suggestion":...},{"issue":...,"suggestion":...}]}
         }:
       
       """
        template = Template(template_string)
        rendered_template = template.render(**kwargs)
        print("Rendered_Template:",rendered_template)
        return rendered_template

   
    def response(self,**kwargs):
        print('Ready TO RESPONSE')
        rendered_template = ''
        use_dict = False
        print(kwargs)

        if kwargs['type'] == 'new_copy':
            print('准备生成新文案')
            rendered_template = self.new_copy_template(**kwargs)
        elif kwargs['type'] == 'article':
            print('准备获得建议')
            rendered_template = self.get_article_advice_template(**kwargs)
        elif kwargs['type'] == 'rednote':
            print('识别小红书需求')
            rendered_template = self.get_rednote_advice_template(**kwargs)
        messages = self.get_messages(rendered_template,use_dict)
        
        completion = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = 0.9,
        )
        print("结果：",completion)
        res = completion.choices[0].message.content
        print("结果类型：",type(res))    
        return res

    def test_response(self,prompt_string,temperature=0.5):
         messages = self.get_messages(prompt_string)
         completion = self.client.chat.completions.create(
             model = self.model,
             messages = messages,
             temperature = temperature,
        )
         res = completion.choices[0].message.content
         print('发送Prompt：',messages)
         print('Kimi回复：',res)
         return res

#调动文件
'''
file_object = client.files.create(file=Path("/Users/wangjohnson/downloads/WechatIMG1445.jpg"), purpose="file-extract")

file_content = client.files.content(file_id=file_object.id).text
'''
'''
import prompt_advice_original

if __name__ == '__main__':
     kimi_bot = KimiBot()
     prompt = prompt_advice_original.prompt
     temperature = 0.9
     #temperature = prompt_pyq.temperature
     kimi_bot.test_response(prompt,temperature)
     #kimi_bot.response()
'''
