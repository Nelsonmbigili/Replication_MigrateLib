def a():
    b()
    c()


def b():
    c()


def c():
    pass


a()
