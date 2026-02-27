def a():
    b()
    c()


def b():
    c()
    d()


def c():
    pass


def d():
    e()


def e():
    f()
    g()


def f():
    pass


def g():
    pass


a()
