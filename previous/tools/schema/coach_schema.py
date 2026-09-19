# schema/coach_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

# 单条教练结构体
class FootballCoachItem(BaseModel):
    name: str = Field(description="教练姓名")
    nationality: str = Field(description="国籍")
    honors: List[str] = Field(description="代表性获奖荣誉列表")
    manage_range: str = Field(pattern=r"^\d{4}~\d{4}$", description="执教区间格式必须为xxxx~xxxx")
    represent_clubs: List[str] = Field(description="代表性执教俱乐部列表")
    current_club: Optional[str] = Field(default=None, description="赋闲填null")

# 外层包裹模型（instructor不支持顶层数组，必须外层套对象）
class CoachResp(BaseModel):
    coach_list: List[FootballCoachItem] = Field(min_length=10, max_length=10, description="固定返回10位教练数据")