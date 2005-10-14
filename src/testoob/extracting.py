# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 Ori Peleg, Barak Schiller, and Misha Seltzer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"Extracting tests from a test suite"
from __future__ import generators # Python 2.2 compatibility

try:
    from itertools import ifilter as _ifilter
except ImportError:
    from compatibility.itertools import ifilter as _ifilter

# David Eppstein's breadth_first
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/231503
def _breadth_first(tree,children=iter):
    """Traverse the nodes of a tree in breadth-first order.
    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.
    """
    yield tree
    last = tree
    for node in _breadth_first(tree,children):
        for child in children(node):
            yield child
            last = child
        if last == node:
            return

def suite_iter(suite):
    """suite_iter(suite) -> an iterator on its direct sub-suites.
    For compatibility with Python versions before 2.4"""
    try:
        return iter(suite)
    except TypeError:
        return iter(suite._tests) # Before 2.4, test suites weren't iterable

def full_extractor(suite, recursive_iterator=_breadth_first):
    """Extract the text fixtures from a suite.
    Descends recursively into sub-suites."""
    import unittest
    def test_children(node):
        if isinstance(node, unittest.TestSuite): return suite_iter(node)
        return []

    return _ifilter(lambda test: isinstance(test, unittest.TestCase),
                    recursive_iterator(suite, children=test_children))

def predicate_extractor(pred):
    return lambda suite: _ifilter(pred, full_extractor(suite))

def regex_extractor(regex):
    """Filter tests based on matching a regex to their id.
    Matching is performed with re.search"""
    import re
    compiled = re.compile(regex)
    def pred(test):return compiled.search(test.id())
    return predicate_extractor(pred)

def glob_extractor(pattern):
    """Filter tests based on a matching glob pattern to their id.
    Matching is performed with fnmatch.fnmatchcase"""
    import fnmatch
    def pred(test): return fnmatch.fnmatchcase(test.id(), pattern)
    return predicate_extractor(pred)
