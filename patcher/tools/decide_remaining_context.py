"""Resolve the residual ambiguity using record/editor context, without forcing identifier changes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import json
from pathlib import Path
import sys
from threading import Lock, Event
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import nskr
import run_gemini_nuclear_unattended as existing
from tools.repair_remaining_translation import mask, MARKER
from tools.residual_translation_validation import normalize_boundary_whitespace

PROMPT = """Fallout New Vegas + Fallout 3 TTW 번역의 마지막 문맥 판정이다.
입력 문자열 각각은 source, signature, field, edid, context 등을 가진 JSON이다.
source만 판정한다. metadata 자체를 번역하거나 반환하지 않는다.
각 결과 문자열은 다음 둘 중 하나여야 한다.
TEXT|한국어 번역문
KEEP|원문을 유지해야 하는 구체적 이유
실제 화면 설명·대사·지명·인물명·장비명은 TEXT로 번역한다. 실제 인물·지명은 적절히 한글 음역한다.
내부 식별자, 테스트/오디오 템플릿 객체, 개발용 주석, 단위·탄약 규격, 암호,
원래 의도적으로 깨진 데이터, 표준 키보드 표기, 모드명·약어는 KEEP으로 유지한다.
코드처럼 보인다는 이유로 정상적인 영어 문장이나 UI 메시지를 KEEP하지 않는다.
TEXT에서는 __NSKR_KEEP_0000__ 표식을 정확히 그대로 유지한다. 표식은 변수·태그·줄바꿈이다.
KEEP에서는 표식을 반환할 필요가 없으며 이유만 쓴다.
반환은 입력과 같은 길이·순서의 JSON 문자열 배열이어야 한다.
"""


def main():
    work = Path(sys.argv[1]).resolve()
    rows = nskr.read_json(work / 'qa_held.json')
    keys = existing.secret_configs()
    if not keys:
        raise RuntimeError('No existing configured credentials')
    directory = work / 'context_decisions'
    directory.mkdir()
    batches = [rows[i:i + 20] for i in range(0, len(rows), 20)]
    ledger, lock, stop = existing.load_budget(), Lock(), Event()
    def lane(number, secret):
        translator = existing.OpenAICompatibleTranslator(
            secret, 'https://generativelanguage.googleapis.com/v1beta/openai',
            existing.MODEL, PROMPT, 'Korean decisions using the required TEXT| or KEEP| format')
        for index in range(number, len(batches), len(keys)):
            if stop.is_set():
                return
            batch = batches[index]
            inputs, saved = [], []
            for row in batch:
                text, tokens = mask(row['source'])
                location = row['locations'][0]
                inputs.append(json.dumps({
                    'source': text, 'signature': row['signature'], 'field': row['field'],
                    'edid': location.get('edid', ''), 'path': location.get('path', ''),
                    'context': location.get('context', ''),
                    'previous_issue': row['repair_reasons']}, ensure_ascii=False))
                saved.append(tokens)
            if stop.wait(existing.COOLDOWN_SECS):
                return
            with lock:
                label, day = f'key_slot_{number + 1}', date.today().isoformat()
                count = ledger.get(label, {}).get(day, 0)
                if count >= existing.MAX_DAILY_PER_KEY:
                    raise RuntimeError('Existing daily-attempt cap reached')
                ledger.setdefault(label, {})[day] = count + 1
                existing.atomic(existing.RUN / 'quota_attempts.json', ledger)
            try:
                values = translator.translate_batch(inputs)
            except Exception as error:
                stop.set()
                message = str(error)
                for secret_key in keys:
                    message = message.replace(secret_key, '<redacted>')
                raise RuntimeError(message[:500]) from None
            results = []
            for row, value, tokens in zip(batch, values, saved):
                if value.startswith('KEEP|'):
                    results.append({**row, 'dest': row['source'],
                                    'origin': 'contextual_retention_candidate',
                                    'preserve_reason': value[5:]})
                elif value.startswith('TEXT|'):
                    text = value[5:]
                    bad_mask = sorted(MARKER.findall(text)) != sorted(tokens)
                    if not bad_mask:
                        for key, token in tokens.items():
                            text = text.replace(key, token)
                    results.append({**row, 'dest': normalize_boundary_whitespace(row['source'], text),
                                    'origin': 'contextual_translation_candidate',
                                    'repair_mask_error': bad_mask})
                else:
                    raise ValueError('Context response lacks required decision prefix')
            nskr.write_json(directory / f'batch_{index+1:04d}.json', results)
            print('CONTEXT_DECISION_BATCH', index + 1, '/', len(batches), flush=True)
    print('CONTEXT_DECISIONS', len(rows), 'ROWS', len(batches), 'BATCHES', flush=True)
    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        tasks = [pool.submit(lane, number, secret) for number, secret in enumerate(keys)]
        for task in tasks:
            task.result()
    combined = {(r['signature'], r['field'], r['source']): r
                for r in nskr.read_json(work / 'corrective_translations.json')}
    for index in range(len(batches)):
        for row in nskr.read_json(directory / f'batch_{index+1:04d}.json'):
            combined[(row['signature'], row['field'], row['source'])] = row
    nskr.write_json(work / 'all_corrective_decisions.json', list(combined.values()))
    print('CONTEXT_DECISIONS_COMPLETE', len(rows), flush=True)


if __name__ == '__main__':
    main()
