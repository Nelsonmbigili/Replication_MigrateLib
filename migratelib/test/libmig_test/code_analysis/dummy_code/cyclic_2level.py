def a(val=3):
    if val > 0:
        b(val - 1)


def b(val):
    a(val - 1)


a()
