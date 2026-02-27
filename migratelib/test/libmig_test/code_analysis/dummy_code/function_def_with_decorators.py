def my_decorator(func):
    def wrapper():
        func()

    return wrapper


@my_decorator
def a():
    pass


a()
