from core.core31_policy.exception.strictness import raise_exception, ExceptionLevel
from core.core31_policy.exception.format import ExceptionFormat
from core.core11_config.config import update_fixed


if __name__ == '__main__':
    import logging

    ctxt = {
        'config': {
            'exception': {
                'level': ExceptionLevel.LAX,
                'format': ExceptionFormat.DEFAULT
            },
            'log': {
                'log_level': logging.DEBUG
            }
        },
    }

    from core.core30_context.context import current_ctxt
    current_ctxt().update(ctxt)
    raise_exception('test')

    current_ctxt()['config'].update({'log': {'log_level': logging.INFO}})
    update_fixed('.log.log_level')
    raise_exception('test2')

    ctxt['config']['exception']['level'] = ExceptionLevel.STRICT
    raise_exception('test3')
