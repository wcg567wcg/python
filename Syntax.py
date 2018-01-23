#!/usr/bin/env python
#! encoding=utf-8
#
# Python Version: Python 3.4.3
#

import math
import string
from string import Template
import bisect
import array
from collections import OrderedDict
import os
import sys
import inspect
from functools import partial

print('Hello Python!')

# if & while & for
x = 8
if (5 < x <= 10):
    print('haha!')

while x > 0:
    x -= 1
else:
    print('over')

for i in range(3):
    print(i)
else:
    print('over')

d = ((1, ["a", "b"]), (2, ["x", "y"]))
# 多层展开
for i, (c1, c2) in d:
    print(i, c1, c2)

for i, c in enumerate("abc"):
    print("s[{0}] = {1}".format(i, c))

# input/output
# input 会将输入入的字符串进行行 eval 处理,raw_input 直接返回用用户输入入的原始字符串

print('------------Input/Output----------------')
enableInputOutput = False
if enableInputOutput:
    user = raw_input('Enter your name:\n')
    print('Your name is %s' % user)

    ageStr = raw_input('Enter your age:\n')
    print('Your age is %d' % int(ageStr))

    result = input("$ ")
    print('result is {0}'.format(result))

# operator
print('\n------------Operator----------------')
powerValue = 3 ** 2
print(powerValue)

value1 = 1 / 2
value2 = 1.0 / 2.0

# floor devision
value3 = 1 // 2
value4 = 1.0 // 2.0

print('Value1: ', value1, ', Value2: ', value2)
print('Value3: ', value3, ', Value4: ', value4)

# list
print('\n------------List----------------')
aList = [4, 1, 3, 2]
print(aList)

aList.append(5)
print(aList)

print(aList[0])
print(aList[:3])
print(aList[3:])

print('4 is in list: ', (4 in aList))
print('0 is not in list: ', (0 not in aList))

# BIF(build-in-functions)
print('max in list :', max(aList))
print('min in list :', min(aList))
print('sum in list :', sum(aList))
print('sum in list :', sum(aList, 10))
print('sort list :', sorted(aList))
print('reverse list :', reversed(aList))

list1 = [1, 2, 3]
list2 = ['A', 'B', 'C']
list3 = list1 + list2
print(list3)

list4 = list2 * 3
print(list4)

print('\n------------List sort----------------')
l = ["a", "d", "c", "e"]
l.sort()
print(l)

bisect.insort(l, "b")
print(l)

# clear
list1[:] = []

# tuple
print('\n------------tuple----------------')
aTuple = ('A string', 77, 80.0, 'Another string', 'A', 123)
print(aTuple)

print(aTuple[0])
print(aTuple[:3])
print(aTuple[3:])

s = tuple("abcadef")
print(s)
print(s.count("a"))      # 元素统计
print(s.index("d"))      # 查找元素,返回序号

# dictionary
print('\n------------Dictionary----------------')
aDict = {'host': 'luozhaohui.github.io'}
aDict['port'] = 80
print(aDict)

for key in aDict.keys():
    print(key, ':', aDict[key])

for key in aDict:
    print(key, ':', aDict[key])

for k, v in aDict.items():
    print(k, v)

d = [x for x in range(10) if x % 2]
print(d)

d = {c: ord(c) for c in "abc"}
print(d)

d = dict.fromkeys("abc", 1)     # 用用序列做 key,并提供默认 value
print(d)
d = dict(zip("ab", range(2)))
print(d)
del d["b"]                      # 删除 k/v
print(d)
d.update({"c": 3})              # 合并 dict
print(d)
d.pop("a")                      # 弹出 value
print(d)
v = d.get("c", 123)             # 如果没有对应 key,返回缺省值
print(v)
d.setdefault("a", 100)          # key 存在,直接返回 value;key 不存在,先设置,后返回

# view
d1 = dict(a=1, b=2)
d2 = dict(b=2, c=3)
v1 = d1.items()
v2 = d2.items()

print(v1 & v2)                 # 交集
print(v1 | v2)                 # 并集
print(v1 - v2)                 # 差集 (仅 v1 有,v2 没有的)
print(v1 ^ v2)                 # 对称差集 (不会同时出现在 v1 和 v2 中)

# 如果希望按照元素添加顺序输出结果,可以用用 OrderedDict
od = OrderedDict(a=1, c=3, b=2)
print(od)                        # 按添加顺序输出

# sort by value
od = OrderedDict(sorted(d.items(),
                        key=lambda t: t[1],
                        reverse=False))
print(od)

# range
print('\n------------Range----------------')
print(range(0, 10, 2))

for num in range(4):
    print(num)

abc = 'abc'
for ch in abc:
    print(ch)

for i, ch in enumerate(abc):
    print('index', i, ':', ch)

# array
print('\n------------array----------------')
a = array.array("l", range(10))     # 用用其他序列类型初始化数组
print(a)
print(a.tolist())

a = array.array("b")                # 创建特定类型数组。
a.fromstring("abc")
print(a)
print(a.tolist())

# list
print('\n------------List parse----------------')
squared = [x ** 2 for x in range(4)]
for i in squared:
    print(i)

print([i for i in range(8) if i % 2 == 0])

# set
print('\n------------Set----------------')
s = set("abc")
print(s)
s.add("d")
s.remove("b")
s.discard("a")                      # 如果存在,就移除
s.update(set("abcd"))               # 合并集合

print(set("abc") == set("abc"))
print(set("abcd") >= set("ab"))     # 超集判断 (issuperset)
print(set("bc") < set("abcd"))      # 子子集判断 (issubset)
print(set("abcd") | set("cdef"))    # 并集 (union)
print(set("abcd").isdisjoint("ab"))  # 判断是否没有交集

s = set("abx")
s -= set("abcdy")                   # 差集 (difference_update)
s &= set("cdef")                    # 交集 (intersection_update)
s ^= set("aby")                     # 对称差集 (symmetric_difference_update)

# file
print('\n------------File----------------')
enablePrintFile = False
# r-read, w-write, a-append, +-read and write, b-binary
handle = open('Syntax.py', 'r')
for eachLine in handle:
    if enablePrintFile:
        print(eachLine)
handle.close()


def walk(rootDir):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for d in dirs:
            path = os.path.join(root, d)
            print(path)
            walk(path)
        for f in files:
            print(os.path.join(root, f))


def listdir(rootDir):
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)
        print(path)
        if os.path.isdir(path):
            listdir(path)


def readLine(filepath):
    with open(filepath) as f:
        for line in f.readlines():
            print(line)

# functions
print('\n------------Functions----------------')
a = 123
b = [1, 2, 3]
print('id of a is', id(a))
print('type of a is', type(a))
print('length of b is', len(b))
print('str(a):', str(a))
print('ord(\'a\'):', ord('a'))
print('chr(97):', chr(97))
print('abs(-10.0): ', abs(-10.0))
print('return divisor and remainder:', divmod(10, 3))
print('pow(2, 3, 3) is pow(2, 3) % 3 :', pow(2, 3, 3))
print('int(3.9):', int(3.9))
print('round(3.9):', round(3.9))
print('math.floor(3.9):', math.floor(3.9))
print('hex(28):', hex(28), ', oct(28):', oct(28))
s, t = 'foa', 'obr'
print(zip(s, t))

# string
print('\n------------String----------------')
aStr = 'ab34'
print(aStr, 'length :', len(aStr))
print('aStr[-1] :', aStr[-1], ', aStr[-len(aStr)] :', aStr[-len(aStr)])
print('aStr[-1 : -4] :', aStr[-4:-1])

print(string.ascii_lowercase)
print(string.ascii_uppercase)
print(string.punctuation)
print(string.digits)

nums = string.digits

# 类型转换
print('\n------------type converter----------------')
print(str(123), int('123'))                            # int
print(bin(17), int('0b10001', 2))
print(oct(20), int('024', 8))
print(hex(22), int('0x16', 16))

print(str(0.9), float("0.9"))

print(ord('a'), chr(97), chr(97))                   # char
print(str([0, 1, 2]), eval("[0, 1, 2]"))               # list
print(str((0, 1, 2)), eval("(0, 1, 2)"))               # tuple
print(str({"a": 1, "b": 2}), eval("{'a': 1, 'b': 2}"))   # dict
print(str({1, 2, 3}), eval("{1, 2, 3}"))               # set

# 常用函数
print('\n------------常用函数----------------')

# exit
# exit([status]) 调用用所有退出函数后终止止进程,并返回 ExitCode
#    忽略或 status = None,表示示正常退出, ExitCode = 0。
#    status = <number>,表示示 ExiCode = <number>
#    返回非非数字对象表示示失败,参数会被显示示, ExitCode = 1
# sys.exit() 和 exit() 完全相同。os._exit() 直接终止止进程,不调用用退出函数,且退出码必须是数字


def clean():
    print('clean...')


def register():
    atexit.register(clean)
    exit("Failure!")

# vars
# 获取 locals 或指定对象的名字空间
print(vars() is locals())
print(vars(sys) is sys.__dict__)

# dir
# 获取 locals 名字空间中的所有名字,或指定对象所有可访问成员 (包括基类)
print(set(locals().keys()) == set(dir()))

# default parameter
print('\n------------默认值函数----------------')
# 默认值对象在创建函数时生生成,所有调用用都使用用同一一对象。
# 如果该默认值是可变类型,那么就如同 C 静态局部变量。

# 用用 *args 收集 "多余" 的位置参数,**kwargs 收集 "额外" 的命名参数。
# 这两个名字只是惯例,可自自由命名,变参只能放在所有参数定义的尾部,且 **kwargs 必须是最后一一个


def test(a, b, *args, **kwargs):
    print(a, b)
    print(args)
    print(kwargs)

test(1, 2, "a", "b", "c", x=100, y=200)

# 可 "展开" 序列类型和字典,将全部元素当做多个实参使用用。如不展开的话,那仅是单个实参对象
# 单个 "*" 展开序列类型,或者仅是字典的主键列表。"**" 展开字典键值对
test(*range(1, 5), **{"x": "Hello", "y": "World"})


def printIsAlphaOrNum(testStr='a+1'):
    for ch in testStr:
        if ch.isalpha():
            print(ch, 'is a alpha.')
        elif ch in nums:
            print(ch, 'is a digit.')
        else:
            print(ch, 'is not a alpha or a digit.')

printIsAlphaOrNum()
printIsAlphaOrNum(aStr)


def test(x, ints=[]):
    ints.append(x)
    return ints

print(test(2))
print(test(1, []))
print(test(3))

s = Template('There are ${howmany} ${lang} Quotation Symbols.')
aStr = s.substitute(lang='Python', howmany=3)
print(aStr)

print('raw str:', '\n', r'\n')

# 名字查找顺序: locals -> enclosing function -> globals -> __builtins__
# 如果函数中包含 exec 语句,编译器生生成的名字指令会依照 LEGB 规则搜索
x = 'abc'


def test():
    print(x)
    exec("x = 10")
    print(x)

test()

print('\n------------堆栈----------------')
# 可使用用 sys._getframe(0) 或 inspect.currentframe() 获取当前堆栈帧。
# 其中 _getframe() 深度参数为 0 表示示当前函数,1 表示示调用用堆栈的上个函数。


def save():
    f = _getframe(1)
    if not f.f_code.co_name.endswith("_logic"):  # 检查 Caller 名字,限制调用用者身身份
        raise Exception("Error!")
    print('ok')


def test():
    save()


def test_logic():
    save()

# 通过调用用堆栈,我们可以隐式向整个执行行流程传递上下文文对象。
# inspect.stack 比 frame.f_back更方便一一些。
# sys._current_frames 返回所有线程的当前堆栈帧对象


def get_context():
    for f in inspect.stack():                       # 循环调用用堆栈列表
        context = f[0].f_locals.get("context")      # 查看该堆栈帧名字空间中是否有⺫目目标
        if context:
            return context                          # 找到了就返回,并终止止查找循环


def controller():
    context = "ContextObject"
    model()


def model():
    print(get_context())

controller()

# 用 functools.partial() 可以将函数包装成更简洁的版本


def test(a, b, c):
    print(a, b, c)

f = partial(test, b=2, c=3)                     # 为后续参数提供命名默认值
f(1)

f = partial(test, 1, c=3)                         # 为前面面的位置参数和后面面的命名参数提供默认值。
f(2)


# class
print('\n------------Class----------------')


class FooClass:
    """my very first class: FooClass"""
    version = 0.1  # class (data) attribute.
    name = ''

    def __eq__(self, o):
        if not o or not isinstance(o, FooClass):
            return False
        return self.name == o.name

    def __init__(self, nm='kesalin'):
        """constructor"""
        self.name = nm  # class instance (data) attribute
        print('Created a class instance for', nm)

    def showName(self):
        """display instance attribute and class name"""
        print('Your name is', self.name)
        print('My name is', self.__class__.__name__)

    def showVersion(self):
        """display class attribute"""
        print(self.version)  # references FooClass.version

    def addMe2Me(self, x):  # does not use 'self'
        """apply + operation to argument"""
        return x + x

foo = FooClass()
print(type(foo))
print('foo isinstance FooClass: ', isinstance(foo, FooClass))

foo.showName()
foo.showVersion()
print(foo.addMe2Me(10))
print(foo.addMe2Me('abc'))

a, b = FooClass("tom"), FooClass("tom")
print(a is b)                    # is 总是判断指针是否相同
print(a == b)                    # 通过 __eq__ 进行行判断
