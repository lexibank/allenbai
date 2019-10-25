import attr
from pathlib import Path

from pylexibank import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb, getEvoBibAsBibtex

import lingpy
from clldutils.misc import slug


@attr.s
class BaidialConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)
    Number = attr.ib(default=None)

@attr.s
class HLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default='Bai')
    Family = attr.ib(default='Sino-Tibetan')
    DialectGroup = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "allenbai"
    concept_class = BaidialConcept
    language_class = HLanguage


    def cmd_download(self, **kw):
        self.raw_dir.write("sources.bib", getEvoBibAsBibtex("Allen2007", **kw))

    def cmd_makecldf(self, args):
        wl = lingpy.Wordlist(self.raw_dir.joinpath("Bai-Dialect-Survey.tsv").as_posix())
        args.writer.add_sources()

        # TODO: add concepts with `add_concepts`
        concept_lookup = {}
        for concept in self.conceptlist.concepts.values():
            idx = concept.id.split('-')[-1]+'_'+slug(concept.english)
            args.writer.add_concept(
                    ID=idx,
                    Name=concept.gloss,
                    Chinese_Gloss=concept.attributes['chinese'],
                    Number=concept.number,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss
                    )
            concept_lookup[concept.english] = idx
        language_lookup = args.writer.add_languages(lookup_factory="Name")


        for k in pb(wl, desc="wl-to-cldf"):
            if wl[k, "value"]:
                args.writer.add_lexemes(
                    Language_ID=language_lookup[wl[k, "doculect"]],
                    Parameter_ID=concept_lookup[wl[k, "concept"]],
                    Value=wl[k, "value"],
                    Source="Allen2007",
                )
