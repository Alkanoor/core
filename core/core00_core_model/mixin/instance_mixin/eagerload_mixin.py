from ...policy.default_join import default_check_joinable, SQLJoinBehavior, default_sql_join_policy
from .introspection_mixin import IntrospectionMixin
from .session_mixin import SessionMixin

from sqlalchemy.orm import Query, joinedload
from typing import Callable, List, Tuple


class EagerloadMixin(SessionMixin, IntrospectionMixin):

    __abstract__ = True

    @classmethod
    def _default_join_internal(cls, walked_classes: List[type], max_depth: int, current_depth: int,
                               join_path: List[type] | None = None, join_on: List[str] | None = None) \
            -> Tuple[Callable[[Query], Query], List[type]]:
        if current_depth < 0:  # no eager loading
            return lambda x: x, []
        if current_depth >= max_depth > 0:  # max depth reached
            return lambda x: x, []

        walked_classes.append(cls)
        join_path_copy = [] if not join_path else [cl for cl in join_path]
        relation_keys = cls.relations if not join_on else join_on
        additional_to_query = []
        joined_load_list = []
        children_resolved = []
        for key in relation_keys:
            if key[:2] != '__':  # otherwise these are indicative backref that would lead to infinite back & forth
                column_path = getattr(cls, key)
                next_join_path = join_path_copy + [column_path]
                print("PUSHING JOINEDLOAD ", next_join_path)
                joined_load_list.append(joinedload(*next_join_path))
                print(column_path, dir(column_path))
                print(column_path.prop.argument)
                if not default_check_joinable() or hasattr(column_path.prop.argument, 'join'):
                    resolved, more_to_query = column_path.prop.argument.join(max_depth, current_depth+1,
                                                                             walked_classes, next_join_path)
                    additional_to_query.extend(more_to_query)
                    children_resolved.append(resolved)

        def resolve_query(initial_query):
            print(f"resolve query normal : {str(initial_query)}, outer joining {cls.__tablename__}")
            resolved = initial_query.outerjoin(cls)
            #print(str(resolved))
            #resolved = initial_query
            for joined_load in joined_load_list:
                resolved = resolved.options(joined_load)
                print(f"Resolved in normal: {str(resolved)}")
            for child in children_resolved:
                resolved = child(resolved)
                print(str(resolved))
            return resolved

        return resolve_query, additional_to_query

    @classmethod
    def join(cls, walked_classes: List[type], max_depth: int = -1, current_depth: int = 0,
             join_path: List[type] | None = None):
        joinable_obj = getattr(cls, '__joinable__', {})
        if not joinable_obj:
            behavior, *args = default_sql_join_policy()
            if args:
                joinable_obj['argument'] = args[0]
            joinable_obj['behavior'] = behavior

        print("JOIN OBJ ", cls, joinable_obj)
        def join_dispatch(joinable_obj):
            match joinable_obj['behavior']:
                case SQLJoinBehavior.EAGER_ALL:
                    return cls._default_join_internal(walked_classes, max_depth, current_depth, join_path,
                                                      joinable_obj.get('join_on', None))
                case SQLJoinBehavior.MAX_DEPTH:
                    if max_depth < 0 or joinable_obj['argument'] < max_depth:
                        new_max_depth = joinable_obj['argument']  # reduce max depth of subtree if inferior to current
                    return cls._default_join_internal(walked_classes, new_max_depth, current_depth, join_path,
                                                      joinable_obj.get('join_on', None))
                case SQLJoinBehavior.IN_CONTEXT:
                    new_behavior, *new_args = default_sql_join_policy()
                    assert behavior != SQLJoinBehavior.IN_CONTEXT, \
                        f"Should not happen in join_dispatch, assert to avoid infinite loop, check the " \
                        f"default_sql_join_policy function to ensure it does not return SQLJoinBehavior.IN_CONTEXT"
                    new_joinable_obj = {
                        'behavior': new_behavior,
                        'argument': new_args[0]
                    }
                    return join_dispatch(new_joinable_obj)
                case SQLJoinBehavior.CUSTOM:
                    return getattr(cls, joinable_obj['argument'])(walked_classes, max_depth, current_depth, join_path)
                case SQLJoinBehavior.NO_LOAD:
                    return cls._default_join_internal(walked_classes, max_depth, -1, join_path,
                                                      joinable_obj.get('join_on', None))
                case _:
                    raise NotImplementedError

        return join_dispatch(joinable_obj)

    @classmethod
    def get_join(cls, **attrs):
        to_outerjoin = []
        query_func, all_objs = cls.join(to_outerjoin)
        all_objs = all_objs if not hasattr(cls, '__tablename__') else [cls] + all_objs
        print("ALL OBJS ", [x.__tablename__ for x in all_objs])
        print("ALL to_outerjoin  ", [x.__tablename__ for x in to_outerjoin])
        initial_query = cls.session.query(*all_objs).filter_by(**attrs)
        #for obj in to_outerjoin:
        #    initial_query = initial_query.outerjoin(obj)
        print("very iniital ", str(initial_query))
        #print(f"and after query func: {query_func(initial_query)}")
        return query_func(initial_query).all()
