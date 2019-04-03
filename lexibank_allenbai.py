# coding=utf-8
from __future__ import unicode_literals, print_function

import lingpy
from lingpy.sequence.sound_classes import clean_string, syllabify
import attr

from clldutils.path import Path
from clldutils.misc import lazyproperty
from pylexibank.dataset import Metadata, Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb, getEvoBibAsBibtex


@attr.s
class BaidialConcept(Concept):
    Chinese = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = 'allenbai'
    concept_class = BaidialConcept

    def clean_form(self, row, form):
        form = self.lexemes.get(form.strip(), form.strip())

        if form not in '---':
            return form

    @lazyproperty
    def tokenizer(self):
        return lambda row, string: syllabify(clean_string(
                string,
                preparse=[
                    ('‹', ''), 
                    ('›', ''),
                    ('ɴ̣', 'ɴ̩'),
                    ],
                )[0].split())

    def cmd_download(self, **kw):
        self.raw.write('sources.bib', getEvoBibAsBibtex('Allen2007', **kw))

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix('Bai-Dialect-Survey.tsv'))

        with self.cldf as ds:
            ds.add_concepts(id_factory=lambda c: c.concepticon_id)
            ds.add_languages(id_factory=lambda l: l['Name'])
            ds.add_sources()
            for k in pb(wl, desc='wl-to-cldf'):
                if wl[k, 'value']:
                    # fix the concepticon_id, if needed (later changes
                    # to concepticon)
                    if int(wl[k, 'concepticon_id']) == 430:
                        parameter_id = 3236
                    else:
                        parameter_id = wl[k, 'concepticon_id']

                    # add the lexeme
                    ds.add_lexemes(
                        Language_ID=wl[k, 'doculect'],
                        Parameter_ID=parameter_id,
                        Value=wl[k, 'value'],
                        Source='Allen2007')

