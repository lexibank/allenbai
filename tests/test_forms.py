# coding: utf-8
from __future__ import unicode_literals, print_function


def test_contains(cldf_dataset, log):
    assert cldf_dataset.validate(log=log)
    assert any(f['Form'] == 'mi³⁵zɔ²¹' for f in cldf_dataset['FormTable'])
    assert len(list(cldf_dataset['FormTable'])) == 4546

