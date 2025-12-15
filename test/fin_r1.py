import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# 加载本地.env文件（本地调试用，云端用Streamlit Secrets）
load_dotenv()

class FinR1SentimentTester:
    def __init__(self):
        """初始化fin-r1测试客户端"""
        # 本地调试从.env读取密钥，云端从st.secrets读取
        self.api_key = os.getenv("GITEE_AI_API_KEY") or st.secrets.get("GITEE_AI_API_KEY", "")
        if not self.api_key:
            raise ValueError("请配置GITEE_AI_API_KEY（本地.env或云端Secrets）")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://ai.gitee.com/api/v1"
        )
        self.model = "fin-r1"
        print("✅ fin-r1测试客户端初始化完成")

    def test_single_text(self, test_text):
        """测试单条文本的舆情分析"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业金融舆情分析师，需严格按以下格式输出JSON：{\"sentiment\":\"正面/中性/负面\",\"confidence\":0-100,\"core_view\":\"核心观点\",\"risk_point\":\"风险点（无则填无）\"}，禁止多余内容"
                    },
                    {
                        "role": "user",
                        "content": f"分析这条金融文本的舆情：{test_text}"
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            # 解析结果
            result = json.loads(response.choices[0].message.content)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

# --------------------- 测试执行 ---------------------
if __name__ == "__main__":
    tester = FinR1SentimentTester()

    # 测试用例（覆盖不同舆情倾向）
    test_cases = [
        "【利好】某上市银行2024年净利润同比增长15%，不良贷款率降至1.2%，创三年新低",
        "某券商发布研报称，当前A股市场处于震荡整理阶段，建议投资者保持中性仓位",
        "【风险提示】某上市公司控股股东违规减持股份，被证监会立案调查，股价单日下跌8%"
    ]

    # 批量测试
    for idx, text in enumerate(test_cases, 1):
        print(f"\n===== 测试用例{idx} =====")
        print(f"待分析文本：{text}")
        result = tester.test_single_text(text)
        if result["status"] == "success":
            print("分析结果：")
            print(f"  舆情倾向：{result['data']['sentiment']}")
            print(f"  置信度：{result['data']['confidence']}%")
            print(f"  核心观点：{result['data']['core_view']}")
            print(f"  风险点：{result['data']['risk_point']}")
        else:
            print(f"测试失败：{result['error']}")