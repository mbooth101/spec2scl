import itertools
import re

import pytest

from rpm2scl.decorators import matches
from rpm2scl.transformers.transformer import Transformer

from transformer_test_case import TransformerTestCase

class SpamTransformer(Transformer):
    """This is a testing class to test various Transformer methods"""
    def __init__(self, spec, options = None):
        self.original_spec = spec
        self.scl_spec = spec
        self.options = options or {}
        self.one_line_transformers, self.more_lines_transformers = self.collect_transformer_methods()

    @matches(r'spam')
    def handle_spam(self, pattern, text):
        return 'handled spam'

    @matches(r'spam\nspam', one_line = False)
    def handle_global_spam(self, pattern, text):
        return 'handled global\nspam'

    # test helper attributes/methods
    # it may be needed to alter these when something is changed in this class
    _transformers_one_line = set(['handle_spam'])
    _transformers_more_lines = set(['handle_global_spam'])
    _patterns_one_line = set([r'spam'])
    _patterns_more_lines = set([r'spam\nspam'])

class TestTransformer(TransformerTestCase):
    def setup_method(self, method):
        self.t = Transformer('', {})
        self.st = SpamTransformer('', {})

    # ========================= tests for methods that don't apply to Transformer subclasses

    @pytest.mark.parametrize(('spec', 'expected'), [
        ('nothing', 'TODO'),
        ('Name: foo', 'foo'),
        ('Name: foo', 'foo'),
        ('Name: %{spam}foo', '%{spam}foo'),
        ('Name: foo-_%{spam}', 'foo-_%{spam}'),
    ])
    def test_get_original_name(self, spec, expected):
        self.t.original_spec = spec
        self.t.scl_spec = 'Name: error if taken from here'
        assert self.t.get_original_name() == expected

    @pytest.mark.parametrize(('pattern', 'spec', 'expected'), [
        (re.compile(r'eat spam'), 'eat spam\neat eat spam', ['eat spam\n', 'eat eat spam']),
        (re.compile(r'eat spam'), 'spam eat\nand spam', []),
        (re.compile(r'eat spam'), 'eat spam \\\n and ham', ['eat spam \\\n and ham']),
        (re.compile(r'eat spam'), 'SPAM=SPAM eat spam', ['SPAM=SPAM eat spam']),
        (re.compile(r'eat spam'), 'SPAM=SPAM eat spam \\\n and ham', ['SPAM=SPAM eat spam \\\n and ham']),
    ])
    def test_find_whole_commands(self, pattern, spec, expected):
        assert self.t.find_whole_commands(pattern, spec) == expected

    # ========================= tests for methods that apply to Transformer subclasses

    def test_collect_transformer_methods(self):
        one_line, more_lines = self.st.collect_transformer_methods()
        # check methods
        assert set(map(lambda x: x.__name__, one_line.keys())) == self.st._transformers_one_line
        assert set(map(lambda x: x.__name__, more_lines.keys())) == self.st._transformers_more_lines
        # check patterns - the one_line.values() and more_lines.values() are list of lists -> use chain to flatten them
        # and then map them to their patterns
        assert set(map(lambda x: x.pattern, itertools.chain(*one_line.values()))) == self.st._patterns_one_line
        assert set(map(lambda x: x.pattern, itertools.chain(*more_lines.values()))) == self.st._patterns_more_lines
