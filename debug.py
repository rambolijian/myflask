# 装饰器的演示

def func1(func):
    def wrapped():
        return "<a>" + func() + "</a>"

    return wrapped

def func2(func):
    def wrapped():
        return "<b>" + func() + "</b>"

    return wrapped

@func2
@func1
def test1():
    return "Hello Wrapper"

@func1
@func2
def test2():
    return "Hello Wrapper"

print(test1())
print(test2())