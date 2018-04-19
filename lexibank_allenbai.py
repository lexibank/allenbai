# coding=utf-8
from __future__ import unicode_literals, print_function

import lingpy
import attr

from clldutils.path import Path
from pylexibank.dataset import Metadata, Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.lingpy_util import getEvoBibAsBibtex, clean_string
from pylexibank.util import pb


@attr.s
class BaidialConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    concept_class = BaidialConcept

    def clean_form(self, row, form):
        form = form.strip()
        if form not in '---':
            return form

    def get_tokenizer(self):
        return lambda row, string: clean_string(string)[0].split()

    def cmd_download(self, **kw):
        self.raw.write('sources.bib', getEvoBibAsBibtex('Allen2007', **kw))

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix('Bai-Dialect-Survey.tsv'))
        gcode = {x['NAME']: x['GLOTTOCODE'] for x in self.languages}

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())
            for k in pb(wl, desc='wl-to-cldf'):
                if wl[k, 'value']:
                    ds.add_language(
                        ID=wl[k, 'doculect'],
                        Name=wl[k, 'doculect'],
                        Glottocode=gcode[wl[k, 'doculect']])
                    ds.add_concept(
                        ID=wl[k, 'concepticon_id'],
                        Name=wl[k, 'concept'],
                        Concepticon_ID=wl[k, 'concepticon_id'],
                        Chinese_Gloss=wl[k, 'chinese'])
                    ds.add_lexemes(
                        Language_ID=wl[k, 'doculect'],
                        Parameter_ID=wl[k, 'concepticon_id'],
                        Value=wl[k, 'value'],
                        Source='Allen2007')

