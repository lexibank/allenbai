import attr
import lingpy
from clldutils.misc import lazyproperty
from clldutils.path import Path
from lingpy.sequence.sound_classes import clean_string, syllabify
from pylexibank.dataset import Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb, getEvoBibAsBibtex


@attr.s
class BaidialConcept(Concept):
    Chinese = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "allenbai"
    concept_class = BaidialConcept

    def clean_form(self, row, form):
        form = self.lexemes.get(form.strip(), form.strip())

        if form not in "---":
            return form

    @lazyproperty
    def tokenizer(self):
        return lambda row, string: syllabify(
            clean_string(string, preparse=[("‹", ""), ("›", ""), ("ɴ̣", "ɴ̩")])[0].split()
        )

    def cmd_download(self, **kw):
        self.raw.write("sources.bib", getEvoBibAsBibtex("Allen2007", **kw))

    def cmd_install(self, **kw):
        wl = lingpy.Wordlist(self.raw.posix("Bai-Dialect-Survey.tsv"))

        with self.cldf as ds:
            ds.add_concepts(id_factory=lambda c: c.number)
            concept2id = {c.english: c.number for c in self.conceptlist.concepts.values()}
            ds.add_languages(id_factory=lambda l: l["Name"])
            ds.add_sources()
            for k in pb(wl, desc="wl-to-cldf"):
                if wl[k, "value"]:
                    ds.add_lexemes(
                        Language_ID=wl[k, "doculect"],
                        Parameter_ID=concept2id[wl[k, "concept"]],
                        Value=wl[k, "value"],
                        Source="Allen2007",
                    )
