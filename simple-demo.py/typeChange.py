# 输入商品信息
product_name = input("请输入商品名称：")
price_str = input("请输入商品单价：")
count_str = input("请输入购买数量：")

# 类型转换
price = float(price_str)
count = int(count_str)

# 计算总价
total = price * count

# 输出结果
print(f"您购买了{product_name}，单价：{price:.2f}元，数量：{count}件，总价：{total:.2f}元")