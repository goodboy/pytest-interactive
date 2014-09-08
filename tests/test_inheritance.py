# test set for inheritance bug
import pytest

# thanks to:
# http://stackoverflow.com/questions/11281698/python-dynamic-class-methods
class HookMeta(type):
    def __init__(cls, name, bases, dct):
        super(HookMeta, cls).__init__(name, bases, dct)

# from types import MethodType
    # def __getattr__(cls, attr):
        # print('getting!')
        # print(HookMeta.old_set)
        # if attr is '__setattr__':
        #     print('got setattr!')
        #     def set_hook(cls, key, value):
        #         ipdb.set_trace()
        #         # old_set(cls, key, value)
        #     # setattr(cls, attr, classmethod(set_hook))
        #     return MethodType(set_hook, cls, cls.__metaclass__)
        #     # return classmethod(set_hook)#getattr(cls, attr)
        # return super(HookMeta, cls).__getattribute__(attr)

    def __setattr__(cls, attr, value):
        print("attr: '{}', value: '{}'".format(attr, value))
        print("class: '{}'".format(cls))
        # ipdb.set_trace()
        return super(HookMeta, cls).__setattr__(attr, value)


class TestBase(object):
    __metaclass__ = HookMeta

    def test_cls(self):
        assert 1

@pytest.fixture
def doggy():
    return 'doggy'

@pytest.mark.usefixtures('doggy')
class TestChild(TestBase):
    pass

class TestSibling(TestBase):
    pass
