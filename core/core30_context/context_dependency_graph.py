from ..core99_misc.fakejq.utils import check_dict_against_attributes_string
from .context import current_ctxt

from typing import List, Callable, Any, Tuple, Type
from functools import wraps
import networkx as nx
import threading
import copy


context_dependencies_graph = None
context_nodes = None
context_producers = None
context_consumers = None

# if main thread, keep the global variable
if threading.current_thread() is threading.main_thread():
    context_dependencies_graph = nx.Graph()
    context_nodes = {}  # all the graph nodes, with their states (if they already produced or resolved deps)
    context_producers = {}  # map production key to a node index (which can produce the related data), one at most atm
    context_consumers = {}  # map dependency key to an array of known nodes depending on the key
else:  # speed up the graph construction, by copying the global one (and associated dicts) from the main thread
    thread_local = threading.local()
    thread_local.context_dependencies_graph = context_dependencies_graph.copy()
    thread_local.context_nodes = copy.deepcopy(context_nodes)
    thread_local.context_producers = copy.deepcopy(context_producers)
    thread_local.context_consumers = copy.deepcopy(context_consumers)
    context_dependencies_graph = thread_local.context_dependencies_graph
    context_nodes = thread_local.context_nodes
    context_producers = thread_local.context_producers
    context_consumers = thread_local.context_consumers


def add_node_if_not_existing(f: Callable[[...], Any]):
    key = f"{f.__module__}.{f.__name__}"
    # assert key not in context_nodes, f"Function node {key} already declared"
    if key not in context_nodes:
        context_nodes[key] = {'index': len(context_nodes)}  # no race condition as thread local
        context_dependencies_graph.add_node(context_nodes[key]['index'], name=key)
    return key, context_nodes[key]['index']


# the function below aims at handling the dependencies graph (resolving when needed)
def context_dependencies(*deps: List[Tuple[str, Type]]):
    def sub(f: Callable[[...], Any]):
        key, node_target_index = add_node_if_not_existing(f)

        assert 'dependencies' not in context_nodes[key], f"Dependencies for {key} already registered"
        context_nodes[key].update({
            'dependencies': {d_name: d_type for d_name, d_type in deps},  # dependencies are for checking type coherence
            'dependencies_ok': False,     # only these 2 variables are used below
            'dependencies_doing': False,  # this one intends to prevent cycles in dependencies graph
        })
        for dependency_name, _ in deps:
            context_consumers.setdefault(dependency_name, []).append(node_target_index)
            if dependency_name in context_producers:
                context_dependencies_graph.add_edge(context_producers[dependency_name], node_target_index)

        @wraps(f)
        def f_with_deps_resolved(*args, **argv):
            if not context_nodes[key].get('dependencies_ok'):
                assert not context_nodes[key]['dependencies_doing'], f"Cycle encountered at {key} for producing " \
                                                                     f"{context_nodes[key].get('products', '?')}"
                context_nodes[key]['dependencies_doing'] = True  # indicates we are walking on dependencies recursively
                for attributes_string, expected_type in deps:
                    assert attributes_string in context_producers, f"No context producer registered to craft " \
                                                                   f"{attributes_string}, please register one"
                    producer_name = context_dependencies_graph.nodes[context_producers[attributes_string]]['name']
                    producer_node = context_nodes[producer_name]
                    # check type coherence between producer and consumer
                    assert producer_node['products'][attributes_string] == expected_type, \
                        f"Incompatible types between expected dependency {expected_type} and produced " \
                        f"{producer_node['products'][attributes_string]}"

                    # this must have been registered from a known producer so the optional assert_types
                    # and assert_done are handled by it, but trust the production_ok variable to avoid recomputing
                    if not producer_node['production_ok']:
                        producer_node['produce_function']()
                context_nodes[key]['dependencies_ok'] = True
                context_nodes[key]['dependencies_doing'] = False
            # if the function is not both a consumer and a producer, we add the context (otherwise the producer will do)
            return f(current_ctxt, *args, **argv) if not context_nodes[key].get('products') else f(*args, **argv)

        return f_with_deps_resolved

    return sub


def context_producer(*products: List[Tuple[str, Type]], assert_done=True, assert_types=False):
    def sub(f: Callable[[...], Any]):
        key, node_source_index = add_node_if_not_existing(f)

        assert not any([product_name in context_producers for product_name, _ in products]), \
            f"Context producers {[pname for pname, _ in products if pname in context_producers]} already" \
            f" declared"
        assert 'products' not in context_nodes[key], f"Producer for {key} already registered"
        context_nodes[key].update({
            'products': {pname: ptype for pname, ptype in products},
            'production_ok': False,
        })
        for product_name, _ in products:
            context_producers[product_name] = node_source_index
            for context_consumer_index in context_consumers.get(product_name, []):
                context_dependencies_graph.add_edge(node_source_index, context_consumer_index)

        @wraps(f)
        def f_producing_expected(*args, **argv):
            # in fact this should be f(context) as we have no clue of which arguments to provide recursively
            # in the graph to construct the right result
            result = f(current_ctxt, *args, **argv)
            if not context_nodes[key]['production_ok']:
                if assert_done or assert_types:
                    for attributes_string, expected_type in products:
                        success, value = check_dict_against_attributes_string(current_ctxt, attributes_string)
                        assert success, f"Expected function to produce {attributes_string}, unable to reach {value}"
                        if assert_types:
                            # TODO: proper type validation, as types with [] not handled (raises exception)
                            assert isinstance(value, expected_type), f"Bad produced type {type(value)} instead of " \
                                                                     f"{expected_type}"
                context_nodes[key]['production_ok'] = True
            return result

        # this way the caller can resolve dependency, and it follows the production checks
        context_nodes[key].update({'produce_function': f_producing_expected})

        return f_producing_expected

    return sub
