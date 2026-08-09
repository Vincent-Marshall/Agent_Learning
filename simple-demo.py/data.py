# # # # # # # # T = 'True'
# # # # # # # # fruit_list = ['orange', 'grape', 20.6, T, False]
# # # # # # # # # list列表类型支持直接打印
# # # # # # # # print(fruit_list)

# # # # # # # # # 打印列表的数据类型
# # # # # # # # print(type(fruit_list))  # <class 'list'>

# # # # # # # # print(fruit_list[0])  # orange
# # # # # # # # print(fruit_list[1])  # grape
# # # # # # # # print(fruit_list[2])  # 20.6
# # # # # # # # print(fruit_list[3])  # True
# # # # # # # # print(fruit_list[4])  # False   

# # # # # # # # fruit_list[2] = 'Hello'

# # # # # # # # print(fruit_list)  # 修改列表中索引为2的元素


# # # # # # # # 演示列表的API
# # # # # # # name_list = ['小明', '小红', '小刚', '小丽', '小强', '小芳', '小亮', '小红']
# # # # # # # # 查询相关方法:
# # # # # # # # 1- index(): 查询指定数据所在位置的下标  如果不存在 直接报错
# # # # # # # index = name_list.index("小丽")
# # # # # # # print(index)  # 3

# # # # # # # # 2- count(): 统计数据在当前列表中出现的次数
# # # # # # # count = name_list.count("小红")
# # # # # # # print(count)  # 2

# # # # # # # # 3- in 和 not in 判断是否存在或不存在
# # # # # # # bool = "小刚" in name_list
# # # # # # # print(bool)
# # # # # # # bool = "小刚" not in name_list
# # # # # # # print(bool)

# # # # # # # # 增加函数
# # # # # # # # 1- append()  增加指定数据到列表中
# # # # # # # # 如果 小宇 不在列表中, 请增加到列表中
# # # # # # # if "小宇" not in name_list:
# # # # # # #     # 能进来, 说明 小宇 不在, 如果不在 添加到列表中
# # # # # # #     name_list.append("小宇")

# # # # # # # print(name_list)

# # # # # # # # 2- extend(): 将一个序列 追加到另一个序列中
# # # # # # # # 2.1 先定义一个新的序列
# # # # # # # name2_list = ['小浩', '小琪']

# # # # # # # # 2.2 将新列表中数据 增加 到 原有列表中
# # # # # # # name_list.extend(name2_list)

# # # # # # # # print(name_list)

# # # # # # # # 3- insert() 在指定位置新增数据
# # # # # # # name_list.insert(4, '小诺')

# # # # # # # # print(name_list)

# # # # # # # # 删除操作
# # # # # # # # 1- del 列表[索引]
# # # # # # # del name_list[-1]

# # # # # # # # print(name_list)

# # # # # # # # 2- pop() 删除指定下标的数据, 默认是删除最后一个 并且会返回删除的数据
# # # # # # # element = name_list.pop()
# # # # # # # # print(element)
# # # # # # # # print(name_list)

# # # # # # # element = name_list.pop(2)
# # # # # # # # print(element)
# # # # # # # # print(name_list)

# # # # # # # # # 3- remove() 移除列表中某个指定数据  如果不存在, 也不会报错 无效果
# # # # # # # name_list.remove("小诺")
# # # # # # # print(name_list)

# # # # # # # # # 修改操作
# # # # # # # # # 1-  修改某个索引的值
# # # # # # # name_list[0] = '大明'
# # # # # # # print(name_list)

# # # # # # # # # 2- reverse: 反转操作
# # # # # # # name_list.reverse()

# # # # # # # print(name_list)

# # # # # # # # # 3- 排序操作: reverse 设置 是否反转   True 反转(倒序)  False 不反转(正序)
# # # # # # # num_list = [3, 7, 10, 56, 2, 9, 4, 5]
# # # # # # # num_list.sort(reverse=True)
# # # # # # # print(num_list)

# # # # # # star_list = ['西施', '王昭君', '杨玉环']
# # # # # # print(len(star_list))  # 3

# # # # # # i = 0
# # # # # # while i < len(star_list):
# # # # # #     print(star_list[i])
# # # # # #     i += 1

# # # # # # for star in star_list:
# # # # # #     print(star)

# # # # # # 演示 列表嵌套
# # # # # # 说明: 容器内部嵌套容器方式
# # # # # # 需求: 有 三个班级, 分别为 前端1班 前端2班  后端1班, 每个班级分别有5位学生
# # # # # # 定义 班级列表
# # # # # front1_class = ['小明','小红','小刚','小丽','小强']
# # # # # front2_class = ['小芳','小亮','小宇','小浩','小琪']
# # # # # back1_class = ['小诺','小泽','小琳','小航','小彤']

# # # # # # 定义 学校列表, 学校列表中有三个班级
# # # # # school_list = [front1_class,front2_class,back1_class]

# # # # # # 以上内容 如果直接使用列表嵌套写法
# # # # # school_list = [
# # # # #     ['小明','小红','小刚','小丽','小强'],
# # # # #     ['小芳','小亮','小宇','小浩','小琪'],
# # # # #     ['小诺','小泽','小琳','小航','小彤']
# # # # # ]

# # # # # # 如何 获取里面的数据呢?  比如 我想获取到 小浩
# # # # # front2_class = school_list[1]
# # # # # name = front2_class[3]
# # # # # print(name)

# # # # # # # 可以简写
# # # # # name = school_list[1][3]
# # # # # print(name)

# # # # # # # 如何遍历打印每一个元素
# # # # # # for classes in school_list:
# # # # # #     for name in classes:
# # # # # #         print(name)
# # # # # #     print("-----------")

# # # # # 1- 如何定义元组
# # # # # 格式:
# # # # #   变量名称 = (元素1,元素2,元素3......)
# # # # #   变量名称 = (元素1,) : 如果元组中只有一个元素, 必须在后面添加一个逗号 否则编译器会自动转换为 数据的本身类型, 而不是元组类型
# # # # user_tuple = ('小明','小红','小刚',20,30,40,True,False)
# # # # print(user_tuple)
# # # # print(type(user_tuple))

# # # # tuple1 = ('小明',)
# # # # tuple2 = ('小明')
# # # # print(tuple1)
# # # # print(type(tuple1))
# # # # print(tuple2)
# # # # print(type(tuple2))

# # # # # # 2- 如何使用元组
# # # # # # 2.1 获取元组中某个元素:  与 列表 和 字符串 一致 都是通过索引的方式来获取
# # # # # print(user_tuple[0])
# # # # # print(user_tuple[1])
# # # # # print(user_tuple[2])

# # # # # # 2.2 遍历: 与 列表 一致
# # # # # for e in user_tuple:
# # # # #     print(e)

# # # # # # 2.3 获取某个元素在元组中索引值: index
# # # # print(user_tuple.index(True))

# # # # # # 2.4 获取某个元素在元组中出现了几次
# # # # print(user_tuple.count('小刚'))

# # # # # # 2.5 获取元组长度
# # # # print(len(user_tuple))



# # # # 1- 如何定义集合
# # # # 格式:
# # # #       格式一:  变量名称 = {元素1,元素2,元素3......}
# # # #       格式二:  变量名称 = set()   空集合
# # # # 特性: 无序 + 去重
# # # # 定义一个有内容的集合
# # # name_set = {'小明','小红','小刚','小明','小刚','小丽'}

# # # print(name_set) #  去重 和 无序  发现每次都是不一样的 所以是无序的
# # # print(type(name_set))
# # # # 定义 空集合
# # # set2 = {}  # 此种定义方法 并不是定义空集合, 而是空的字典
# # # empty_set = set()
# # # print(type(empty_set))
# # # print(type(set2))

# # # # # 获取数据: 遍历的方式
# # # # # for 循环
# # # for name in name_set:
# # #     print(name)


# # # 1- 演示: 如何定义字典
# # # 格式:
# # #   格式1:  变量名称 = {key1:value1,key2:value2,key3:value3.....}
# # #   格式2:  变量名称 = {}  或者 变量名称 = dict()   空字典

# # # 构建一个有内容的字典
# # person = {'name': '小明', 'age': 19, 'address': "上海市浦东新区张江镇", 'sex': '男', 'hobby': '篮球、足球、游泳'}
# # print(person)
# # # print(type(person))

# # # # 构建空字典
# # # dict1 = {}
# # # dict2 = dict()
# # # print(dict1)
# # # print(type(dict1))
# # # print(dict2)
# # # print(type(dict2))

# # # 遍历操作
# # for key in person:
# #     # print(key)
# #     print(person[key])



# # 字典的相关API:
# # 如何增加元素:
# # 需求: 为person 字典增加一个 birthday 属性 值为 2005-08-20
# person = {'name': '小明', 'age': 19, 'address': "上海市浦东新区张江镇", 'sex': '男', 'hobby': '篮球、足球、游泳'}
# person["birthday"] = '2005-08-20'

# # print(person)

# # 如何修改元素: 与添加一直, 如果key存在就是修改 如果不存在 就是添加
# # 需求: 修改性别为 女
# person['sex'] = "女"
# # print(person)

# # 如何删除元素
# # 删除某个元素:  根据key
# del person['birthday']
# print(person)
# # 清空字典
# # person.clear()
# # print(person)

# # 如何查询:
# # 1- 根据 key 直接获取value: 如果key 不存在 直接报错
# # 获取 address的值
# print(person['address'])

# # # 2- 获取所有的keys
# keys_list = person.keys()
# print(keys_list)
# # # 3- 获取所有的value
# values_list = person.values()
# print(values_list)
# # # 4- 获取字典中每一个 kv对
# # # 快速返回变量: ctrl + alt + v
# items = person.items()
# print(items)

# for kv in items:
#     print(kv)
#     print(f'{kv[0]},{kv[1]}')



"""
    给定一个字符串my_string，现在要求统计每个字符出现的次数: 形成结果: {'字符':出现次数,'字符2':次数}

    例如: 'abcdecf' ==> {'a':1,'b':1,'c':2,'d':1,'e':1,'f':1}
"""
# 1- 创建一个字符串
my_string = 'abcdecf'

# 2- 遍历字符串, 获取每一个字符
# 2.1 初始化一个用于保存结果的空字典
my_dict = {}
for e in my_string:

    # 2.2 判断 当前遍历的这个元素 是否在 字典中存在呢?
    if e in my_dict.keys():
        # 说明 当前遍历的元素 在 字典中是存在的
        my_dict[e] += 1
    else:
        # 说明 当前遍历的元素 在 字典中是不存在的
        my_dict[e] = 1

print(my_dict)