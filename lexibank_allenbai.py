import attr
import lingpy
from clldutils.misc import lazyproperty
from clldutils.path import Path
from lingpy.sequence.sound_classes import clean_string, syllabify
from pylexibank.dataset import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb, getEvoBibAsBibtex


@attr.s
class BaidialConcept(Concept):
    Chinese = attr.ib(default=None)

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

    def clean_form(self, row, form):
        form = self.lexemes.get(form.strip(), form.strip())

        if form not in ["---"]:
            return form

    def cmd_download(self, **kw):
        self.raw.write("sources.bib", getEvoBibAsBibtex("Allen2007", **kw))

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix("Bai-Dialect-Survey.tsv"))

        with self.cldf as ds:
            ds.add_concepts(id_factory=lambda c: c.number)
            concept2id = {c.english: c.number for c in self.conceptlist.concepts.values()}
            ds.add_languages(id_factory=lambda l: l["Name"])

            langs = {k['Name']: k['ID'] for k in self.languages}
            ds.add_languages()

            ds.add_sources()
            for k in pb(wl, desc="wl-to-cldf"):
                if wl[k, "value"]:
                    ds.add_lexemes(
                        Language_ID=langs[wl[k, "doculect"]],
                        Parameter_ID=concept2id[wl[k, "concept"]],
                        Value=wl[k, "value"],
                        Source="Allen2007",
                    )
