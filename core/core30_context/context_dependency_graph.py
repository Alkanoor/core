from ..core99_misc.fakejq.utils import check_dict_against_attributes_string

from typing import List, Callable, Any, Tuple, Type
from functools import wraps
import networkx as nx
import threading
import copy


class ThreadSafeDependencyManager:

    _context_dependencies_graph = nx.Graph()
    _context_nodes = {}
    _context_producers = {}
    _context_consumers = {}

    _thread_local = threading.local()


    @classmethod
    def get_attr_or_copy_from_global(cls, attr_name):
        if threading.current_thread() is threading.main_thread():
            return getattr(cls, '_' + attr_name)
        else:
            if not hasattr(cls._thread_local, attr_name):
                # the first time in a thread the variable is asked, copy it from its global state
                setattr(cls._thread_local, attr_name,
                        getattr(cls, '_' + attr_name).copy() if attr_name == '_context_dependencies_graph' else
                        copy.deepcopy(getattr(cls, '_' + attr_name)))
            return getattr(cls._thread_local, attr_name)

    def __init__(self):
        self.context_dependencies_graph = ThreadSafeDependencyManager.get_attr_or_copy_from_global('context_dependencies_graph')
        self.context_nodes = ThreadSafeDependencyManager.get_attr_or_copy_from_global('context_nodes')
        self.context_producers = ThreadSafeDependencyManager.get_attr_or_copy_from_global('context_producers')
        self.context_consumers = ThreadSafeDependencyManager.get_attr_or_copy_from_global('context_consumers')


    def add_node_if_not_existing(self, f: Callable[[...], Any]):
        key = f"{f.__module__}.{f.__name__}"
        # assert key not in context_nodes, f"Function node {key} already declared"
        if key not in self.context_nodes:
            self.context_nodes[key] = {'index': len(self.context_nodes)}  # no race condition as thread local
            self.context_dependencies_graph.add_node(self.context_nodes[key]['index'], name=key)
        return key, self.context_nodes[key]['index']

    # the function below aims at handling the dependencies graph (resolving when needed)
    def context_dependencies(self, *deps: List[Tuple[str, Type]]):
        def sub(f: Callable[[...], Any]):
            key, node_target_index = self.add_node_if_not_existing(f)

            assert 'dependencies' not in self.context_nodes[key], f"Dependencies for {key} already registered"
            self.context_nodes[key].update({
                'dependencies': {d_name: d_type
                                 for d_name, d_type in deps},  # dependencies are for checking type coherence
                'dependencies_ok': False,  # only these 2 variables are used below
                'dependencies_doing': False,  # this one intends to prevent cycles in dependencies graph
            })
            for dep_name, _ in deps:
                assert dep_name[0] == '.', f"Value to produce {dep_name} not starting with dot (pyjq like)"
                self.context_consumers.setdefault(dep_name, []).append(node_target_index)
                if dep_name in self.context_producers:
                    self.context_dependencies_graph.add_edge(self.context_producers[dep_name], node_target_index)

            @wraps(f)
            def f_with_deps_resolved(*args, **argv):
                if not self.context_nodes[key].get('dependencies_ok'):
                    assert not self.context_nodes[key]['dependencies_doing'], \
                        f"Cycle encountered at {key} for producing {self.context_nodes[key].get('products', '?')}"
                    self.context_nodes[key][
                        'dependencies_doing'] = True  # indicates we are walking on dependencies recursively
                    for attributes_string, expected_type in deps:
                        assert attributes_string in self.context_producers, f"No context producer registered to craft " \
                                                                            f"{attributes_string}, please register one"
                        producer_name = self.context_dependencies_graph.nodes[
                            self.context_producers[attributes_string]
                        ]['name']
                        producer_node = self.context_nodes[producer_name]
                        # check type coherence between producer and consumer
                        assert producer_node['products'][attributes_string] == expected_type, \
                            f"Incompatible types between expected dependency {expected_type} and produced " \
                            f"{producer_node['products'][attributes_string]}"

                        # this must have been registered from a known producer so the optional assert_types
                        # and assert_done are handled by it, but trust the production_ok variable to avoid recomputing
                        if not producer_node['production_ok']:
                            producer_node['produce_function']()
                    self.context_nodes[key]['dependencies_ok'] = True
                    self.context_nodes[key]['dependencies_doing'] = False
                # if the function is not both a consumer and a producer, we add the context (otherwise the producer will do)
                return f(current_ctxt(), *args, **argv) if not self.context_nodes[key].get('products') \
                    else f(*args, **argv)

            return f_with_deps_resolved

        return sub


    def context_producer(self, *products: List[Tuple[str, Type]], assert_done=True, assert_types=False):
        def sub(f: Callable[[...], Any]):
            key, node_source_index = self.add_node_if_not_existing(f)

            assert not any([product_name in self.context_producers for product_name, _ in products]), \
                f"Context producers {[pname for pname, _ in products if pname in self.context_producers]} already" \
                f" declared"
            assert 'products' not in self.context_nodes[key], f"Producer for {key} already registered"
            self.context_nodes[key].update({
                'products': {pname: ptype for pname, ptype in products},
                'production_ok': False,
            })
            for product_name, _ in products:
                assert product_name[0] == '.', f"Value to produce {product_name} not starting with dot (pyjq like)"
                self.context_producers[product_name] = node_source_index
                for context_consumer_index in self.context_consumers.get(product_name, []):
                    self.context_dependencies_graph.add_edge(node_source_index, context_consumer_index)

            @wraps(f)
            def f_producing_expected(*args, **argv):
                # in fact this should be f(context) as we have no clue of which arguments to provide recursively
                # in the graph to construct the right result
                result = f(current_ctxt(), *args, **argv)
                if not self.context_nodes[key]['production_ok']:
                    if assert_done or assert_types:
                        for attributes_string, expected_type in products:
                            success, value = check_dict_against_attributes_string(current_ctxt(), attributes_string)
                            assert success, f"Expected function to produce {attributes_string}, unable to reach {value}"
                            if assert_types:
                                # TODO: proper type validation, as types with [] not handled (raises exception)
                                assert isinstance(value, expected_type), f"Bad produced type {type(value)} instead of " \
                                                                         f"{expected_type}"
                    self.context_nodes[key]['production_ok'] = True
                return result

            # this way the caller can resolve dependency, and it follows the production checks
            self.context_nodes[key].update({'produce_function': f_producing_expected})

            return f_producing_expected

        return sub


    def try_resolve(self, *dep_names: List[str]):
        producers = {dep_name: self.context_nodes[self.context_dependencies_graph.nodes[
                            self.context_producers[dep_name]
                        ]['name']] for dep_name in dep_names}
        return {dep_name: producers[dep_name]['produce_function'] for dep_name in dep_names}


def context_dependencies(*deps: List[Tuple[str, Type]]):
    return ThreadSafeDependencyManager().context_dependencies(*deps)

def context_producer(*products: List[Tuple[str, Type]], assert_done=True, assert_types=False):
    return ThreadSafeDependencyManager().context_producer(*products, assert_done=assert_done, assert_types=assert_types)

def try_resolve(*dep_names: List[str]):
    return ThreadSafeDependencyManager().try_resolve(*dep_names)


from .context import current_ctxt
