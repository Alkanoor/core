from core.core31_policy.exception.format import format_exception
from core.core31_policy.exception.strictness import raise_exception


if __name__ == '__main__':
    from core.core30_context.log.logger import get_logger
    import logging

    logger = get_logger('main')
    logger.setLevel(logging.DEBUG)
    ctxt = {
        'config': {'exception': {'level': 'lax', 'format': 'default'}},
        'policy': {
            'log': {
                'logger': get_logger('main'),
                'debug_logger': get_logger('main')
            },
            'exception': {
               'format': 1
            }
        },
    }
    ctxt['policy']['exception']['format'] = lambda x, y: format_exception(ctxt, x, y)
    raise_exception(ctxt, 'test')

    ctxt['config']['exception']['level'] = 'strict'
    raise_exception(ctxt, 'test')
