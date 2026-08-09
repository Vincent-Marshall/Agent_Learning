# '''
# 在Python中有两种类型的变量
# 1. 可变类型 list,dict,set,自定义的类型 ，尽管数据相同，但是占用不同的内存空间
# 2. 不可变类型 int, bool, str, double, tuple,相同的数据在内存中只存储1份数据
# a = 1
# b = 1
# 可以理解为a和b存储的都是1的地址
# 当a = 2 的时候，a指向的就是2的地址
# '''
a = 1
b = 1
a = 2

list_a = [1,2,3]
list_b = [1,2,3]
list_a.append(4)
print(list_a)
print(list_b)

# '''
# 因为Python中赋值和定义具有二义性
# Python不同于C++， 
# C++语法
# int a = 100;  a = 200;
# Python中
# 定义和赋值弄到一起
# a = 100
# a = 200
# 如果a = 200在函数内， a = 100在函数外
# 两个a 不是同一个a， 函数内的a = 200会被认为定义了一个新的变量a
# '''

num = 10
def func():
    global num  # 声明使用全局的num
    num = 20
    print(f"函数内num:{num}, id(num): {id(num)}")
func()
print(f"函数外num:{num}, id(num): {id(num)}")
# 内外id一致，全局num被修改为20