def func1():
    pass


class ClassA:
    def func1(self):
        class ClassA:
            pass

    @staticmethod
    def func2(cls):
        def func1():
            pass


class ClassB:
    class ClassA:
        pass


def func2():
    def func21():
        pass
