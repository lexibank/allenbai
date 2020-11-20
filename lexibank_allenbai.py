import attr
from pathlib import Path

from pylexibank import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar, getEvoBibAsBibtex

from cldfbench import CLDFSpec
from csvw import Datatype
from pyclts import CLTS

import lingpy
from clldutils.misc import slug

from unicodedata import normalize

def nfc(string):
    return normalize('NFC', string)


@attr.s
class CustomConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)
    Number = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    DialectGroup = attr.ib(default=None)
    SubGroup = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "allenbai"
    concept_class = CustomConcept
    language_class = CustomLanguage

    def cmd_download(self, **kw):
        self.raw_dir.write("sources.bib", getEvoBibAsBibtex("Allen2007", **kw))

    def cldf_specs(self):
        return {
            None: BaseDataset.cldf_specs(self),
            'structure': CLDFSpec(
                module='StructureDataset',
                dir=self.cldf_dir,
                data_fnames={'ParameterTable': 'features.csv'}
            )
        }

    def cmd_makecldf(self, args):
        with self.cldf_writer(args) as writer:
            wl = lingpy.Wordlist(self.raw_dir.joinpath("Bai-Dialect-Survey.tsv").as_posix())
            writer.add_sources()

            # TODO: add concepts with `add_concepts`
            concept_lookup = {}
            for concept in self.conceptlists[0].concepts.values():
                idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
                writer.add_concept(
                    ID=idx,
                    Name=concept.english,
                    Chinese_Gloss=concept.attributes["chinese"],
                    Number=concept.number,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                )
                concept_lookup[concept.english] = idx
            language_lookup = writer.add_languages(lookup_factory="Name")

            for k in progressbar(wl, desc="wl-to-cldf"):
                if wl[k, "value"]:
                    writer.add_lexemes(
                        Language_ID=language_lookup[wl[k, "doculect"]],
                        Parameter_ID=concept_lookup[wl[k, "concept"]],
                        Value=wl[k, "value"],
                        Source="Allen2007",
                    )
            language_table = writer.cldf['LanguageTable']

        with self.cldf_writer(args, cldf_spec='structure', clean=False) as writer:
            # We share the language table across both CLDF datasets:
            writer.cldf.add_component(language_table)
            writer.objects['LanguageTable'] = self.languages
            inventories = self.raw_dir.read_csv(
                'inventories.tsv', delimiter='\t', dicts=True)

            writer.cldf.add_columns(
                    'ParameterTable',
                    {'name': 'CLTS_BIPA', 'datatype': 'string'},
                    {'name': 'CLTS_Name', 'datatype': 'string'},
                    {
                        'name': 'Lexibank_BIPA',
                        'datatype': 'string',
                        'separator': ' '
                    },
                    {'name': 'Prosody', 'datatype': 'string'},
                    )
            writer.cldf.add_columns(
                    'ValueTable',
                    {'name': 'Allophone', 'datatype': 'string'},
                    {'name': 'Context', 'datatype': 'string'}
                    )

            clts = CLTS(args.clts.dir)
            bipa = clts.transcriptionsystem_dict['bipa']
            ab = clts.transcriptiondata_dict['allenbai']
            pids, visited = {}, set()
            for row in inventories:
                pidx = '-'.join([
                    str(hex(ord(s)))[2:].rjust(4, '0') for s in row['Value']])
                pidx += '_'+'-'.join(row['Prosody'].split())
                name = ' - '.join([
                    bipa[s].name for s in row['BIPA'].split(' ')])
                if not row['Value'] in pids:
                    writer.objects['ParameterTable'].append({
                        'ID': pidx,
                        'Name': row['Value'],
                        'Description': name,
                        'CLTS_BIPA': ab.grapheme_map[nfc(row['Value'])],
                        'CLTS_Name': bipa[ab.grapheme_map[nfc(row['Value'])]] or '',
                        'Lexibank_BIPA': row['BIPA'],
                        'Prosody': row['Prosody'],
                        })
                    pids[row['Value']] = pidx
                if row['Language_ID']+'-'+pidx not in visited:
                    writer.objects['ValueTable'].append({
                        'ID': row['Language_ID']+'_'+pidx,
                        'Language_ID': row['Language_ID'],
                        'Parameter_ID': pidx,
                        'Value': row['Value'],
                        'AllophoneFrom': row['Language_ID']+'_'+pids[row['Value']],
                        'Context': row['Context'],
                        'Source': ['Allen2007'],
                        })
                    visited.add(row['Language_ID']+'-'+pidx)

