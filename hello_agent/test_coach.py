# test_coach.py
import ai
from prompt_loader import load_prompt
from schema.coach_schema import CoachResp

# 加载prompt模板
template = load_prompt("football_coach")
system_content = template.format(
    role="足球领域的专家",
    task="列举并研究10位欧洲著名的足球教练（如穆里尼奥、瓜迪奥拉、曼奇尼等），提取字段信息",
    user_input="请输出10位欧洲著名足球教练的JSON数据"
)

messages = [
    {"role": "system", "content": system_content},
]

# ===================== 核心改造：使用instructor结构化调用 =====================
try:
    # 直接传入Pydantic模型，自动完成校验+重试纠错
    coach_result: CoachResp = ai.chat_struct(
        messages=messages,
        response_model=CoachResp,
        max_retries=3
    )
    # 直接读取对象属性，无需解析JSON
    print("✅ 结构化校验通过，教练数据：")
    for idx, coach in enumerate(coach_result.coach_list, 1):
        print(f"\n【第{idx}位教练】")
        print(f"姓名：{coach.name}")
        print(f"国籍：{coach.nationality}")
        print(f"执教年限：{coach.manage_range}")
        print(f"当前俱乐部：{coach.current_club if coach.current_club else '赋闲'}")
        print(f"荣誉列表：{coach.honors}")
        print(f"执教俱乐部：{coach.represent_clubs}")

except Exception as e:
    # 捕获Pydantic校验异常、接口异常，精准定位问题
    print(f"❌ 结构化调用失败：{str(e)}")