# coding: utf-8
from __future__ import unicode_literals


def test_contains(cldf_dataset):
    assert any(f['Form'] == 'mi³⁵zɔ²¹' for f in cldf_dataset['FormTable'])


def test_forms(forms_report):
    assert forms_report['valid']
    assert forms_report['tables'][0]['row-count'] == 4547

