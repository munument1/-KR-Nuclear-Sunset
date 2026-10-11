"""One bounded corrective pass with smaller inputs and protected-token masking."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
import re
import sys
from threading import Event, Lock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import nskr
import run_gemini_nuclear_unattended as existing
from tools.residual_translation_validation import EXTRA, normalize_boundary_whitespace
from nskr_xedit import FORMAT
from tools.run_remaining_translation import PROMPT

MASK = re.compile(FORMAT.pattern + '|' + EXTRA.pattern + r'|\r\n|\r|\n', FORMAT.flags)
MARKER = re.compile(r'__NSKR_KEEP_\d{4}__')


def mask(text):
    saved = {}
    def replace(match):
        key = f'__NSKR_KEEP_{len(saved):04d}__'
        saved[key] = match[0]
        return key
    return MASK.sub(replace, text), saved


def main():
    work = Path(sys.argv[1]).resolve()
    batches = nskr.read_json(work / 'repair_manifest.json')['batches']
    keys = existing.secret_configs()
    if not keys:
        raise RuntimeError('No existing configured credentials')
    directory = work / 'repair_results'
    directory.mkdir(exist_ok=True)
    ledger = existing.load_budget()
    manual = nskr.read_json(ROOT / 'data/remaining_final_manual_mappings.json')
    ledger_path = existing.RUN / 'quota_attempts.json'
    lock, stop = Lock(), Event()
    done = 0

    def lane(number, secret):
        nonlocal done
        translator = existing.OpenAICompatibleTranslator(
            api_key=secret, base_url='https://generativelanguage.googleapis.com/v1beta/openai',
            model=existing.MODEL, prompt_text=PROMPT, target_language='Korean')
        for job in batches[number::len(keys)]:
            if stop.is_set():
                return
            target = directory / job['file']
            if target.exists():
                raise ValueError('Corrective pass already attempted; refusing automatic repetition')
            source = work / 'repair_inputs' / job['file']
            if nskr.sha256(source) != job['source_sha256']:
                raise ValueError('Corrective input changed')
            rows = nskr.read_json(source)
            requested = [row for row in rows if row['source'] not in manual]
            masked = [mask(row['source']) for row in requested]
            if stop.wait(existing.COOLDOWN_SECS):
                return
            with lock:
                day, label = date.today().isoformat(), f'key_slot_{number + 1}'
                count = ledger.get(label, {}).get(day, 0)
                if count >= existing.MAX_DAILY_PER_KEY:
                    stop.set()
                    raise RuntimeError('Existing daily-attempt cap reached')
                ledger.setdefault(label, {})[day] = count + 1
                existing.atomic(ledger_path, ledger)
            translator.prompt_text = PROMPT + """
이번 입력은 검증 실패 문구의 교정이다. __NSKR_KEEP_0000__ 같은 표식은 글자 그대로 유지한다.
표식은 태그·변수·줄바꿈이므로 추가·삭제·재배열하지 않는다.
문맥상 실제 이름과 문장은 한국어로 번역한다. 내부 식별자와 탄약 규격·코드는 원문 그대로 유지한다.
알림 문구는 짧고 명확하게 번역한다. 반환 배열의 항목 수와 순서를 정확히 유지한다.
"""
            try:
                values = translator.translate_batch([text for text, saved in masked])
                results = []
                for row, value, (text, tokens) in zip(requested, values, masked):
                    if sorted(MARKER.findall(value)) != sorted(tokens):
                        results.append({**row, 'dest': value, 'repair_mask_error': True})
                        continue
                    for marker, original in tokens.items():
                        value = value.replace(marker, original)
                    results.append({**row, 'dest': normalize_boundary_whitespace(row['source'], value),
                                    'origin': 'gemini_corrective_candidate'})
                results.extend({**row, 'dest': manual[row['source']],
                                'origin': 'manual_ui_correction'}
                               for row in rows if row['source'] in manual)
                nskr.write_json(target, results)
            except Exception as error:
                message = str(error)
                for key in keys:
                    message = message.replace(key, '<redacted>')
                nskr.write_json(target.with_suffix('.error.json'), {'error': message[:1800]})
                stop.set()
                raise RuntimeError(message[:250]) from None
            with lock:
                done += 1
                if done % 10 == 0:
                    print('CORRECTIVE_BATCHES', done, '/', len(batches), flush=True)

    print('CORRECTIVE_PASS', len(batches), 'BATCHES', flush=True)
    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        tasks = [pool.submit(lane, number, key) for number, key in enumerate(keys)]
        for task in tasks:
            task.result()
    combined = []
    for job in batches:
        combined.extend(nskr.read_json(directory / job['file']))
    nskr.write_json(work / 'corrective_translations.json', combined)
    print('CORRECTIVE_PASS_COMPLETE', len(combined), 'ROWS', flush=True)


if __name__ == '__main__':
    main()
