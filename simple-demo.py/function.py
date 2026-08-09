# # # 需求: 请帮我定义一个函数: computer 计算器函数, 要求给这个函数传入 2个参数, 在函数的内部完成  + - 计算, 并且将 + -的二个结果返回

# # # 定义函数:
# # def computer(a, b):
# #     # 编写函数功能的核心位置
# #     jia = a + b
# #     jian = a - b

# #     # 将加和减结果一并返回
# #     return jia, jian
# #     # return [jia, jian]
# #     # return {jia, jian}
# #     # return {'jia':jia,'jian':jian}


# # # 调用函数
# # # res = computer(3,5)
# # i,j = computer(3,5)  # 利用自动拆包思想

# # print(f'加法结果:{i},减法的结果:{j}')


# # 1 利用递归实现阶乘运算
# '''
# 递归: 一个函数自己调用自己，就是递归
# 必要条件： 要有结束条件
# '''
# def func_c(num:int):

#     if num <= 1:
#         return 1
#     return num * func_c(num-1)

# print(func_c(3))



# 需求：有一个小青蛙，每次可以跳1个台阶，或者跳2个台阶，总共10个台阶，问有多少种走法
# 思路：
# 1. 当仅有一个台阶，那么就是1中走法，fn(1) = 1
# 2. 当有两个台阶，那么有两种走法,f(2) = 2
# 3. 当有三个台阶， 那么有这些走法 f(3) = f(2) + f(1)
# 4. 如果有四级台阶， 那么走法为f(4) = f(3) + f(2)
# 5. 如果有n级台阶，那么走法为f(n) = f(n-1) + f(n-2)
# '''
# def fn_steps(n):
#     if n == 1:
#         return 1
#     if n == 2:
#         return 2
#     return fn_steps(n-1) + fn_steps(n-2)

# print(fn_steps(10))
# print(fn_steps(100))

# def fn_steps(n):
#     if n == 1:
#         return 1
#     if n == 2:
#         return 2
#     prev, curr = 1, 2
#     for _ in range(3, n+1):
#         prev, curr = curr, prev + curr
#     return curr

# print(fn_steps(10))
# print(fn_steps(100))



def hanuota(num, A,B,C):
    
    if num == 1:
        print(f'将第{num}个盘子从{A}移动到{C}')
        return
    
    # 将num-1个盘子从A借助C移动到B
    hanuota(num-1, A,C,B)

    # 将第num个盘子，从A移动到C
    print(f'将第{num}个盘子从{A}移动到{C}')

    # 将num-1个盘子从B借助A移动到C
    hanuota(num-1,B,A,C)

hanuota(3,'A','B','C')