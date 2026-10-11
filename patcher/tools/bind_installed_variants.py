"""Bind reviewed installed-variant text to exact physical sources, not profiles."""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nskr
from tools.tes4_text_scan import masters, plugin_records, field_occurrences


REVIEWED_IDS = {
    'YUPTTW.esm': {'010c23', '152b53'},
    'AutumnLeaves.esp': {
        '075e43', '06dacf', '06c0c5', '06c0c4', '066b3a', '05ba24', '05ba1e',
        '04e31e', '0429af', '041878', '03ae31', '0325ff', '0292b2', '0289b4',
        '0289a9', '0289a3', '024cd3', '02470d', '02470b', '024709', '022fa2',
        '021e16', '021e10', '021b13', '021825', '021821', '01e09f', '01e09d',
        '01e09b', '01e095', '01dda6', '01dac1', '01d7e1', '01d4f0', '01baa1',
        '01ac2e', '01ac28', '01ac22', '01ac20', '01ac1c', '018c4c', '01868f',
    },
    'LumenSkinnedTTW.esp': {'00e55b', '00e55a', '00e559'},
}
CORRECTIONS = {
    ('YUPTTW.esm', '152b53'): '계속 까불어 봐라, 인간...',
    ('AutumnLeaves.esp', '06c0c4'): '우린 이제 다시는 만나거나 대화할 수 없을 거야. 너랑 나, 너무 이목을 끌었어.',
    ('AutumnLeaves.esp', '041878'): '[화술 > 50] 너무 과소평가하는 거 아니야? 어쨌든 이것들이 상징이라고 말한 건 너잖아.',
    ('AutumnLeaves.esp', '01e09d'): '코는 어찌나 골던지. 사방에 피를 쏟아놓고는 낫는 데만 꼬박 6개월이 걸렸어. 주인님한테 헛소리나 늘어놓으며 잔소리를 해대더니, 결국엔 가버렸지.',
}


def identity(row):
    return (row['owner'].casefold(), row['id'].lower(), row['signature'],
            row['field'], row['path'], row.get('field_occurrence', 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    catalog = nskr.read_json(args.catalog / 'catalog.json')
    report = nskr.read_json(args.report)
    installation = nskr.Installation(Path(report['mo2_root']), all_installed=True)
    rebound = 0
    for result in report['files']:
        if not result.get('unmatched'):
            continue
        source = nskr.contained(installation.mods, f"{result['provider']}/{result['path']}")
        assert nskr.sha256(source) == result['source_sha256']
        owners = [name.casefold() for name in masters(source)] + [source.name.casefold()]
        missing = result['unmatched_entries']
        ids = {int(row['id'], 16) | owners.index(row['owner'].casefold()) << 24 for row in missing}
        records = {fid: (sig, fields) for fid, sig, fields in plugin_records(source, selected_ids=ids)}
        template = next(e for e in catalog['files']
                        if e['path'].casefold() == result['path'].casefold() and not e.get('optional'))
        entry = deepcopy(template)
        entry.update(optional=True, provider=result['provider'], baseline_sha256=result['source_sha256'])
        entry.pop('verified_delta', None)
        replacements = {}
        for row in missing:
            fid = int(row['id'], 16) | owners.index(row['owner'].casefold()) << 24
            signature, fields = records[fid]
            assert signature == row['signature']
            raw = next(raw.rstrip(b'\0') for field, occurrence, raw in field_occurrences(fields)
                       if field == row['field'] and occurrence == row.get('field_occurrence', 0))
            try:
                text = raw.decode('utf-8')
                encoding = 'utf-8'
            except UnicodeError:
                text = raw.decode('cp1252')
                encoding = 'cp1252'
            assert text.strip() == row['source'].strip() or row['id'] in REVIEWED_IDS.get(result['path'], set())
            replacement = {**row, 'source': text, 'source_encoding': encoding}
            replacement.pop('reason', None)
            replacement.pop('mappingOrigin', None)
            replacement['dest'] = CORRECTIONS.get((result['path'], row['id']), row['dest'])
            if result['path'] == 'AutumnLeaves.esp' and row['id'] in {'075e43', '01e095'}:
                replacement['dest'] = replacement['dest'].replace('바로 여기 있지', '바로 저기 있지')
            replacements[identity(row)] = replacement
        entry['mappings'] = [replacements.get(identity(row), row) for row in entry['mappings']]
        assert len(replacements) == len(missing)
        catalog['files'].append(entry)
        rebound += len(replacements)
    args.destination.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='NSKR-All-Installed-Catalog-', dir=args.destination))
    shutil.copytree(args.catalog, work / 'TranslationData')
    nskr.write_json(work / 'TranslationData/catalog.json', catalog)
    print({'catalog': str(work / 'TranslationData'), 'variant_strings_rebound': rebound})


if __name__ == '__main__':
    main()
