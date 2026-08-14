print("Hello, World!")

# 方法1：type()函数
age = 18
print(type(age))  # <class 'int'>

# 方法2：isinstance()函数（推荐）
print(isinstance(age, int))  # True
print(isinstance(age, str))  # False

name = "李四"
age = 20
score = 95.5
# 基础用法
print(f"姓名：{name}，年龄：{age}，成绩：{score}")
# 格式控制（保留2位小数）
print(f"成绩：{score:.2f}")
# 数字补零（6位宽度）
print(f"学号：{1:06d}")  # 输出：000001

print(f"姓名：{name}\t年龄：{age}\n成绩：{score:.3f}")