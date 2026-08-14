# 示例：判断是否成年
age = int(input("请输入你的年龄："))
if age >= 18:
    print("你已成年，可观看此电影")
else:
    print("你未成年，需由监护人陪同")

# 示例：成绩评级
score = float(input("请输入你的考试成绩："))
if score >= 90:
    print("成绩评级：优秀")
elif score >= 80:
    print("成绩评级：良好")
elif score >= 70:
    print("成绩评级：中等")
elif score >= 60:
    print("成绩评级：及格")
else:
    print("成绩评级：不及格，需要补考")