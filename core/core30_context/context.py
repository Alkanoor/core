# from ..core99_misc.fakejq.utils import check_dict_against_attributes_string
from ..core31_policy.thread.copy import default_thread_context_copy
# from .context_dependency_graph import try_resolve

import threading

_global_current_ctxt = {}  # this is only to be modified in the main thread, calling the context() function
_thread_local = threading.local()


def current_ctxt():
    # if main thread, keep the global variable
    if threading.current_thread() is threading.main_thread():
        return _global_current_ctxt  # main context variable which will hold all the current context. Careful when modifying it
    else:
        if not hasattr(_thread_local, 'current_ctxt'):
            _thread_local.current_ctxt = default_thread_context_copy(_global_current_ctxt)
            ###### below is a gas factory
            ## only time when the global current context is accessed from another thread
            # indict, callback = check_dict_against_attributes_string(_global_current_ctxt, '.policy.thread.copy_context')
            # if not indict:
            #     if not hasattr(_thread_local, 'getting_current_ctxt'):
            #         _thread_local.getting_current_ctxt = True
            #         try_resolve('.policy.thread.copy_context')['.policy.thread.copy_context']()
            #         return current_ctxt()
            #     else:  # avoid infinite loop
            #         return _global_current_ctxt
            # _thread_local.current_ctxt = callback(_global_current_ctxt)
        return _thread_local.current_ctxt


from .imports import *
