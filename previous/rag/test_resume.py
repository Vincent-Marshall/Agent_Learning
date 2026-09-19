# resume_extractor.py
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

client = instructor.from_openai(
    OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
    )
)


class WorkExperience(BaseModel):
    company: str
    title: str
    start: str = Field(description="开始时间，格式 YYYY-MM，未知填 unknown")
    end: str = Field(description="结束时间，格式 YYYY-MM 或 present")
    highlights: list[str] = Field(max_length=5, description="最多 5 条核心成就")


class Resume(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    summary: str = Field(max_length=300, description="对候选人的一句话总结")
    skills: list[str] = Field(max_length=15)
    experience: list[WorkExperience]
    years_of_experience: int = Field(ge=0)


def extract(resume_text: str) -> Resume:
    return client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个简历信息抽取器，从给定文本提取结构化字段。"},
            {"role": "user", "content": resume_text},
        ],
        response_model=Resume,
        max_retries=3,
    )


if __name__ == "__main__":
    sample = """
    张三，5 年 Python 后端经验，邮箱 zhangsan@example.com
    2021.03 - 至今 字节跳动 后端工程师
      - 主导广告投放系统重构，QPS 从 5k 提升到 20k
      - 设计并落地基于 Kafka 的事件总线
    2019.07 - 2021.02 美团 高级开发工程师
      - 负责订单履约系统的高可用改造
    技能：Python、Django、FastAPI、PostgreSQL、Kafka、Redis、Docker
    """
    resume = extract(sample)
    print(resume.model_dump_json(indent=2, ensure_ascii=False))
