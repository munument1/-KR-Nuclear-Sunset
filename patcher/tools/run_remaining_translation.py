"""Translate the complete residual queue with the existing configured Gemini route.

Uses the existing user's credential loader and shared daily-attempt ledger.
No credential is printed or copied. Authentication/quota refusals stop all lanes.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import json
from pathlib import Path
import sys
from threading import Event, Lock
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import nskr
import run_gemini_nuclear_unattended as existing
from tools.loose_translation import TOKEN

PROMPT = """Fallout: New Vegas / Fallout 3 / Tale of Two Wastelands / Nuclear Sunset 한국어 번역.
모든 입력의 실제 표시 문구를 한국어로 번역한다. 이름은 세계관과 기존 한국어 번역에 맞춘다.
이미 한국어가 섞인 항목은 한국어 부분을 유지하고 남은 영어 표시 문구만 번역한다.
변수, HTML 태그, %s/%d/%r/%% 등 모든 서식 토큰과 줄바꿈 개수를 그대로 보존한다.
제어문자, 경로, 리소스 이름, ID, 코드처럼 번역하면 안 되는 요소는 바꾸지 않는다.
내용을 추가하거나 생략하지 않는다. 원문에 없는 괄호 영어 병기나 해설을 넣지 않는다.
MESG DESC는 알림창 본문이다. 원문 UTF-8이 1023바이트 이하이면 번역도 1023바이트 이하로 간결하게 쓴다.
JSON 배열의 항목 수와 순서를 반드시 그대로 유지한다.
"""


def validate(source, destination):
    reasons = []
    if not destination.strip():
        reasons.append('empty_translation')
    if Counter(TOKEN.findall(source)) != Counter(TOKEN.findall(destination)):
        reasons.append('protected_token_mismatch')
    if source.replace('\r\n', '\n').count('\n') != destination.replace('\r\n', '\n').count('\n'):
        reasons.append('newline_count_mismatch')
    if '\ufffd' in destination or '\0' in destination:
        reasons.append('invalid_output_character')
    return reasons


def main():
    work = Path(sys.argv[1]).resolve()
    manifest = nskr.read_json(work / 'manifest.json')
    keys = existing.secret_configs()
    if not keys:
        raise RuntimeError('No existing configured Gemini credentials')
    (work / 'results').mkdir(exist_ok=True)
    (work / 'problems').mkdir(exist_ok=True)
    lock = Lock()
    stop = Event()
    progress = {'total_batches': len(manifest['batches']), 'completed_batches': 0,
                'accepted_rows': 0, 'held_rows': 0, 'failed_batches': 0}
    ledger_path = existing.RUN / 'quota_attempts.json'
    ledger = existing.load_budget()
    jobs = [manifest['batches'][lane::len(keys)] for lane in range(len(keys))]

    def status():
        nskr.write_json(work / 'status.json', progress)

    def lane(number, secret):
        label = f'key_slot_{number + 1}'
        translator = existing.OpenAICompatibleTranslator(
            api_key=secret, base_url='https://generativelanguage.googleapis.com/v1beta/openai',
            model=existing.MODEL, prompt_text=PROMPT, target_language='Korean')
        for job in jobs[number]:
            if stop.is_set():
                return
            source_path = work / 'inputs' / job['file']
            if nskr.sha256(source_path) != job['source_sha256']:
                raise ValueError('Immutable translation input hash mismatch')
            result_path = work / 'results' / job['file']
            rows = nskr.read_json(source_path)
            if result_path.exists():
                saved = nskr.read_json(result_path)
                if [r['source'] for r in saved] != [r['source'] for r in rows]:
                    raise ValueError('Saved translation source mismatch')
            else:
                if stop.wait(existing.COOLDOWN_SECS):
                    return
                with lock:
                    day = date.today().isoformat()
                    count = ledger.get(label, {}).get(day, 0)
                    if count >= existing.MAX_DAILY_PER_KEY:
                        progress['blocker'] = 'configured_daily_attempt_cap'
                        stop.set()
                        status()
                        return
                    ledger.setdefault(label, {})[day] = count + 1
                    existing.atomic(ledger_path, ledger)
                context = '\n'.join(
                    f'{index+1}: {r["signature"]}:{r["field"]}'
                    for index, r in enumerate(rows))
                translator.prompt_text = PROMPT + '\n항목별 문맥:\n' + context
                try:
                    values = translator.translate_batch([r['source'] for r in rows])
                except Exception as error:
                    message = str(error)
                    for key in keys:
                        message = message.replace(key, '<redacted>')
                    nskr.write_json(work / 'problems' / job['file'],
                                    {'batch': job['file'], 'error': message[:1800]})
                    with lock:
                        progress['failed_batches'] += 1
                        progress['last_error'] = message[:250]
                        if any(word in message.lower() for word in (
                                'http 401', 'http 403', 'http 429', 'quota',
                                'resource_exhausted', 'permission denied', 'invalid api key',
                                'model not found', 'http 404')):
                            progress['blocker'] = 'service_or_quota_refusal'
                            stop.set()
                        status()
                    continue
                saved = []
                for row, value in zip(rows, values):
                    reasons = validate(row['source'], value)
                    if (row['signature'] == 'MESG' and row['field'] == 'DESC'
                            and len(row['source'].encode('utf-8')) <= 1023
                            and len(value.encode('utf-8')) > 1023):
                        reasons.append('message_byte_budget_exceeded')
                    saved.append({**row, 'dest': value,
                                  'validation_errors': reasons, 'origin': 'gemini_candidate'})
                nskr.write_json(result_path, saved)
            with lock:
                progress['completed_batches'] += 1
                progress['accepted_rows'] += sum(not r['validation_errors'] for r in saved)
                progress['held_rows'] += sum(bool(r['validation_errors']) for r in saved)
                progress['last_completed'] = job['file']
                status()
                if progress['completed_batches'] % 10 == 0:
                    print(json.dumps(progress, ensure_ascii=False), flush=True)

    print('TRANSLATING_ALL_REMAINING', manifest['inputs'], 'BATCHES', len(manifest['batches']),
          'EXISTING_KEY_SLOTS', len(keys), 'MODEL', existing.MODEL, flush=True)
    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        futures = [pool.submit(lane, number, key) for number, key in enumerate(keys)]
        for future in futures:
            future.result()
    with lock:
        progress['pending_batches'] = progress['total_batches'] - progress['completed_batches']
        status()
    print(json.dumps(progress, ensure_ascii=False), flush=True)
    if progress['pending_batches'] or progress['failed_batches']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
