import threading


# if main thread, keep the global variable
if threading.current_thread() is threading.main_thread():
    current_ctxt = {}  # main context variable which will hold all the current context. Careful when modifying it
else:
    @context_dependencies('.policy.thread.copy_context')
    def resolve_context():
        thread_local = threading.local()
        # only time when the global current context is accessed from another thread
        thread_local.current_ctxt = current_ctxt['policy']['thread']['copy_context'](current_ctxt)
        return thread_local.current_ctxt
    current_ctxt = resolve_context()
