from .introspection_mixin import IntrospectionMixin
from .session_mixin import SessionMixin

import enum


class JoinBehavior(enum.Enum):
    EAGER_ALL = enum.auto()   # eagerly load all children
    MAX_DEPTH = enum.auto()   # defined according to the maximum recursion depth
    IN_CONTEXT = enum.auto()  # defined according to context, config, policy
    CUSTOM = enum.auto()      # defined within the class
    NO_LOAD = enum.auto()     # this should almost never be used, as it does not allow to load anything recursively


class EagerloadMixin(SessionMixin, IntrospectionMixin):
    __abstract__ = True

    @classmethod
    def get_joined(cls, **attrs):
        if hasattr(cls, '__joinable__'):
            return cls.join(cls.query).filter_by(**attrs)
        return cls.query.filter_by(**attrs)
