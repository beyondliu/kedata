



# class Data:
#     primary_key = None
#     fields = ()
#     #TODO: 
#     #extra_fields

#     def __setattr__(self, name, value):
#         if name == self.primary_key:
#             raise AttributeError(
#                 "Cannot set attribute {!r} on type {}".format(
#                     name, self.__class__.__name__))
#         super(Data, self).__setattr__(name, value)    


#     @classmethod
#     def get_fields(cls):
#         return tuple(list(cls.fields) + [cls.primary_key])



from weakref import WeakKeyDictionary
from functools import wraps

class Data(type):
  
    primary_key = None
    fields = ()    

    def __new__(meta, cname, bases=(), dctry={}, **kwargs):
        print('base __new__ called!')
        #TODO:
        #if not dctry:
            # doctry = {}
        def _setattr(self, name, value):
            print('field name:', name)
            print('self.primary_key:', self.primary_key)
            if  name == self.primary_key:
                print('name is the same as the primary_key')
                raise AttributeError(
                    "Cannot set attribute {!r} on type {}".format(
                        name, self.__class__.__name__))
            object.__setattr__(self, name, value)

        def override_setattr_after(fn):
            print('override_setattr_after called')
            @wraps(fn)
            def _wrapper(*args, **kwargs):
                cls.__setattr__ = object.__setattr__
                fn(*args, **kwargs)
                cls.__setattr__ = _setattr
            return _wrapper

        cls = type.__new__(meta, cname, bases, dctry)
        cls.__init__ = override_setattr_after(cls.__init__)
        return cls



class PrimaryKey:
    def __init__(self):
        self._values = WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None: return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if self._values[instance]:
            raise AttributeError("Can't set the id!")
        self._values[instance] = value




class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in clas_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
                
        cls = type.__new__(meta, name, bases, class_dict)
        return cls        


class Field:
    def __init__(self):
        self.name = None
        self.internal_name = None

        