from .introspection_mixin import IntrospectionMixin

from sqlalchemy import inspect


class ReprMixin(IntrospectionMixin):
    __abstract__ = True

    __repr_attrs__ = []
    __repr_max_length__ = 15

    @classmethod
    def class_to_json(cls, max_nesting=-1, cur_nesting=0):
        return {
            'classname': cls.__name__,
            'tablename': cls.__tablename__,
            'attrs': {
                **{
                    k: getattr(cls, k) for k in cls.columns()
                },
                **{
                    k: '[...]' if cur_nesting >= max_nesting >= 0 else
                    (getattr(cls, k).class_to_json(max_nesting, cur_nesting + 1)
                     if hasattr(getattr(cls, k), 'class_to_json')
                     else getattr(cls, k)) for k in cls.relations()
                }
            }
        }

    def self_to_json(self, max_nesting=-1, cur_nesting=0):
        return {
            'id': self._id_str,
            'classname': self.__class__.__name__,
            'tablename': self.__class__.__tablename__,
            'attrs': {
                **{
                    k: getattr(self, k) for k in self.columns()
                },
                **{
                    k: '[...]' if cur_nesting >= max_nesting >= 0 else
                    (getattr(self, k).self_to_json(max_nesting, cur_nesting + 1)
                     if hasattr(getattr(self, k), 'self_to_json')
                     else getattr(self, k)) for k in self.relations()
                }
            }
        }

    @property
    def _id_str(self):
        ids = inspect(self).identity
        if ids:
            return '-'.join([str(x) for x in ids]) if len(ids) > 1 \
                else str(ids[0])
        else:
            return 'None'

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError("{} has incorrect attribute '{}' in "
                               "__repr__attrs__".format(self.__class__, key))
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + '...'

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return ' '.join(values)

    def __repr__(self):
        return f"[{self.__class__.__tablename__} #{self._id_str} {self._repr_attrs_str}]"
