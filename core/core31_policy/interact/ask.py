from logging import Logger

from core.core30_context.context_dependency_graph import context_producer, context_dependencies
from core.core11_config.config import register_config_default, config_dependencies, Config
from core.core30_context.context import Context

from typing import Callable, Any
from functools import partial
from enum import Enum


class BadAnswerPolicy(Enum):
    REPEAT_UNTIL_GOOD = 1
    RAISE = 2
    RETRY_AND_EXIT = 3
    RETRY_AND_RAISE = 4
    ASK_RETRY_OR_STOP_OR_DEFAULT = 5
    RANDOM = 6
    DEFAULT_VALUE = 7


register_config_default('.interactor.bad_answer', BadAnswerPolicy, BadAnswerPolicy.REPEAT_UNTIL_GOOD)
register_config_default('.interactor.bad_answer_retry_count', int, 3)


@config_dependencies(('.interactor.bad_answer', BadAnswerPolicy), ('.interactor.bad_answer_retry_count', int))
@context_dependencies(('.log.main_logger', Logger))
def cli_bad_answer(ctxt: Context, config: Config, provided_answer, transformed_answer,
                   call_question_again, transform_input_if_call_question_again, accepted_answers,
                   *question_args, **question_argv):
    if config['interactor']['bad_answer'] == BadAnswerPolicy.REPEAT_UNTIL_GOOD:
        return call_question_again(transform_input_if_call_question_again, accepted_answers,
                                   *question_args, *question_argv)
    elif config['interactor']['bad_answer'] == BadAnswerPolicy.RAISE:
        raise Exception(f"Unexpected answer provided: {provided_answer} -> transformed to {transformed_answer}, "
                        f"expecting one of {list(accepted_answers.keys())}")
    elif config['interactor']['bad_answer'] == BadAnswerPolicy.RETRY_AND_EXIT or \
            config['interactor']['bad_answer'] == BadAnswerPolicy.RETRY_AND_RAISE:
        if 'retry_count' in question_argv and \
                question_argv['retry_count'] >= config['interactor']['bad_answer_retry_count']:
            ctxt['log']['main_logger'].warning(
                f"Retry count {config['interactor']['bad_answer_retry_count']} exceeded, "
                f"{'raising' if config['interactor']['bad_answer'] != BadAnswerPolicy.RETRY_AND_EXIT else 'exiting'}")
            if config['interactor']['bad_answer'] == BadAnswerPolicy.RETRY_AND_EXIT:
                exit(1)
            else:
                raise Exception(f"Too much failures answering for {question_args}, {question_argv}: expecting one "
                                f"of {list(accepted_answers.keys())}")
        question_argv.setdefault('retry_count', 0)
        question_argv['retry_count'] += 1
        return call_question_again(transform_input_if_call_question_again, accepted_answers,
                                   *question_args, **question_argv)
    else:
        raise NotImplementedError


@context_producer(('.interactor.bad_answer', Callable[[...], Any]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))  # dynamically generated
def policy_bad_answer(ctxt: Context):
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor']['bad_answer'] = cli_bad_answer
    else:
        raise NotImplementedError


def default_ask_cli(*args, **argv):
    print(args, argv)
    out = input()
    return out


def default_ask_cli_transform_and_check(transform_input, accepted_answers_and_transform, *args, **argv):
    print(args, argv)
    out = input()
    transformed = transform_input(out)
    if transformed in accepted_answers_and_transform:
        return accepted_answers_and_transform[transformed](out, transformed)
    else:
        return cli_bad_answer(out, transformed, default_ask_cli_transform_and_check,
                              transform_input, accepted_answers_and_transform, *args, **argv)


@context_producer(('.interactor.ask', Callable[[...], str]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))  # dynamically generated
def ask_to_interactor(ctxt: Context):
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor']['ask'] = default_ask_cli
    else:
        raise NotImplementedError


@context_producer(('.interactor.ask_boolean', Callable[[...], bool]))
@context_dependencies(('.interactor.local', bool, False), ('.interactor.cli', bool, False))
def ask_boolean_to_interactor(ctxt: Context):
    if ctxt['interactor']['local'] and ctxt['interactor']['type'] == 'cli':
        ctxt['interactor']['ask_boolean'] = partial(default_ask_cli_transform_and_check,
                                                    transform_input=lambda x: x.lower(),
                                                    accepted_answers_and_transform={
                                                        'y': (lambda *args: True),
                                                        'n': (lambda *args: False),
                                                    })
    else:
        raise NotImplementedError
