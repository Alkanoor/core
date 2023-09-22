from ...core30_context.context import current_ctxt

from functools import wraps


def init_policy(init_func):
    @wraps(init_func)
    def sub():
        return init_func(current_ctxt)
    return sub
