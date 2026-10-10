"""Resumable local 4-lane Gemini translator. No key material is logged or saved.

Runs on user PC; configured keys are loaded privately at process runtime from
the existing two local JSON AI Translator installations. Up to four lanes
are serviced by available distinct keys. All results stay local.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime,timedelta
from pathlib import Path
from threading import Lock
import argparse,hashlib,json,os,sys,time,re,traceback
ROOT=Path(__file__).resolve().parents[1]
APP=Path(r"D:\translation\json-ai-translator")
sys.path.insert(0,str(APP))
from app import OpenAICompatibleTranslator
BASE=Path(r"D:\Codex_Trans\비바 뉴 베가스\뉴클리어 선셋\미번역_번역작업_20261010\11_Gemini_JSON_번역대기")
MANIFEST=BASE/"00_manifest.json"
PROMPT=BASE/"00_NuclearSunset_user_prompt.txt"
RUN=BASE/"03_API_실행상태"
MODEL="gemini-3.1-flash-lite"
MAX_DAILY_PER_KEY=220
COOLDOWN_SECS=12
API_KEY_CONFIGS=[
 Path(r"D:\translation\json-ai-translator\config.json"),
 Path(r"D:\translation\JsonAiTranslator\config.json"),
]
_lock=Lock()
state={}
def atomic(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(path)
def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def secret_configs():
    secrets=[]
    for p in API_KEY_CONFIGS:
        if p.is_file():
            data=load(p)
            secret=data.get("api_key","").strip()
            if secret and secret not in secrets:secrets.append(secret)
    # Optional user-owned environment variables; never print/read into files.
    for i in range(1,5):
        secret=os.getenv(f"GEMINI_API_KEY_{i}","").strip()
        if secret and secret not in secrets:secrets.append(secret)
    return secrets[:4]
def set_status(event,**fields):
    with _lock:
        state.update({"event":event,"updated_at":datetime.now().isoformat(timespec="seconds"),**fields})
        atomic(RUN/"status.json",state)
def load_budget():
    p=RUN/"quota_attempts.json"
    return load(p) if p.is_file() else {}
def quota_wait(label,ledger):
    # Simple conservative calendar-day budget, plus pacing per key.
    while True:
        today=date.today().isoformat()
        with _lock:
            count=ledger.get(label,{}).get(today,0)
        if count<MAX_DAILY_PER_KEY:break
        set_status("DAY_QUOTA_PAUSE",last_lane=label,next_check="next local day")
        time.sleep(60)
    # Account all attempted requests, including failed/429, before network call.
    with _lock:
        today=date.today().isoformat()
        ledger.setdefault(label,{})
        ledger[label][today]=ledger[label].get(today,0)+1
        atomic(RUN/"quota_attempts.json",ledger)
    time.sleep(COOLDOWN_SECS)
def make_prompt(prompt,job):
    meta=load(BASE/job["index_file"])["entries"]
    lines=[]
    for i,item in enumerate(meta.values(),1):
        lines.append(f"{i}: {item['signature']}:{item['field']} (original master: {item['origin_master']})")
    return prompt+"\n\n## Input batch context\n"+f"Plugin: {job['plugin']}\n"+"Item types in input order:\n"+"\n".join(lines)
def translate_one(job,secret,label,ledger,prompt):
    rel=Path(job["source_file"])
    src=BASE/rel
    dest=BASE/"results"/rel.parent/(rel.stem+".translated.json")
    if dest.is_file():
        obj=load(dest)
        original=load(src)
        if isinstance(obj,dict) and list(obj)==list(original) and all(isinstance(v,str) for v in obj.values()):
            return "already_saved",0
        return "invalid_saved_output",0
    original=load(src)
    assert len(original)==job["rows"] and all(isinstance(v,str) for v in original.values())
    translator=OpenAICompatibleTranslator(
        api_key=secret,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        model=MODEL,
        prompt_text=make_prompt(prompt,job),
        target_language="Korean")
    vals=list(original.values())
    # Split large batches only on parse/output failure. Every attempt counts in quota.
    calls=0
    def invoke(chunk,depth=0):
        nonlocal calls
        if depth>5:raise ValueError("MAX_SPLIT_DEPTH")
        for attempt in range(2):
            quota_wait(label,ledger)
            calls+=1
            try:
                return translator.translate_batch(chunk)
            except Exception as exc:
                error_text=str(exc).lower()
                if any(t in error_text for t in ("401","403","unauthorized","invalid api key","permission denied")):
                    raise RuntimeError("AUTH_ERROR") from None
                if any(t in error_text for t in ("429","resource_exhausted","quota", "rate limit")):
                    raise RuntimeError("RATE_LIMIT_REACHED") from None
                if any(t in error_text for t in ("404","model not found", "model is not supported")):
                    raise RuntimeError("MODEL_NOT_AVAILABLE") from None
                if attempt==0:
                    time.sleep(6)
        if len(chunk)==1:raise RuntimeError("SINGLE_ITEM_PARSE_FAILED")
        half=len(chunk)//2
        return invoke(chunk[:half],depth+1)+invoke(chunk[half:],depth+1)
    result=invoke(vals)
    if len(result)!=len(original):raise RuntimeError("INCORRECT_BATCH_LENGTH")
    document=dict(zip(original,result))
    atomic(dest,document)
    return "saved",calls
def lane_worker(key_number,secret,jobs,prompt,ledger,stop_on_limit=False):
    label=f"key_slot_{key_number+1}"
    counts={"saved":0,"skipped":0,"failed":0}
    for job in jobs:
        name=job["source_file"]
        while True:
            set_status("RUNNING",last_lane=label,last_batch=name)
            try:
                outcome,calls=translate_one(job,secret,label,ledger,prompt)
                if outcome=="saved":counts["saved"]+=1
                elif outcome=="already_saved":counts["skipped"]+=1
                else:
                    counts["failed"]+=1
                    atomic(RUN/"problems"/(Path(name).stem+".json"),{"batch":name,"reason":outcome})
                break
            except Exception as exc:
                tag=str(exc)[:60]
                if tag=="RATE_LIMIT_REACHED":
                    # Google API daily quota or exhaustion. Stop requests
                    # from this key until the next local calendar day.
                    with _lock:
                        today=date.today().isoformat()
                        ledger.setdefault(label,{})[today]=MAX_DAILY_PER_KEY
                        atomic(RUN/"quota_attempts.json",ledger)
                    set_status("WAITING_FOR_QUOTA_RESET",last_lane=label,last_batch=name)
                    if stop_on_limit:return counts
                    time.sleep(60)
                    continue
                atomic(RUN/"problems"/(Path(name).stem+".json"),{"batch":name,"reason":tag})
                counts["failed"]+=1
                if tag in ("AUTH_ERROR","MODEL_NOT_AVAILABLE"):
                    set_status("CREDENTIAL_OR_MODEL_ERROR",last_lane=label,last_batch=name)
                    return counts
                break
            finally:
                with _lock:
                    state.setdefault("key_progress",{})[label]=dict(counts)
                    atomic(RUN/"status.json",state)
    return counts
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--dry-run",action="store_true")
    opts=parser.parse_args()
    if not MANIFEST.is_file() or not PROMPT.is_file():raise RuntimeError("Missing work inputs")
    manifest=load(MANIFEST)
    prompt=PROMPT.read_text(encoding="utf-8")
    if manifest.get("records")!=42021 or len(manifest["files"])!=859:
        raise RuntimeError("Unexpected source count")
    keys=secret_configs()
    if not keys:raise RuntimeError("No locally configured Gemini API credentials")
    RUN.mkdir(parents=True,exist_ok=True)
    ledger=load_budget()
    # preserve last success and ensure separate key slots: 4 lanes -> 2 or 4 distinct keys
    groups=[[] for _ in keys]
    for job in manifest["files"]:
        lane=int(job["project_lane"])-1
        groups[lane%len(keys)].append(job)
    if opts.smoke:
        # Only one request to validate credentials, model and parser.
        first=groups[0][0]
        set_status("SMOKE_TEST",configured_key_slots=len(keys),batch=first["source_file"])
        outcome,calls=translate_one(first,keys[0],"key_slot_1",ledger,prompt)
        print(json.dumps({"smoke_outcome":outcome,"api_calls":calls,"key_slots":len(keys)}))
        return
    if opts.dry_run:
        print(json.dumps({"keys":len(keys),"lane_batches":[len(g) for g in groups],"model":MODEL,"daily_attempt_cap_per_key":MAX_DAILY_PER_KEY}))
        return
    set_status("STARTED",model=MODEL,configured_key_slots=len(keys),
               total_batches=manifest["batches"],total_source_rows=manifest["records"],
               lane_batches=[len(g) for g in groups],key_progress={})
    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        tasks=[pool.submit(lane_worker,i,keys[i],groups[i],prompt,ledger,False)
               for i in range(len(keys))]
        result=[t.result() for t in tasks]
    completed=sum(len(list((BASE/"results"/f"project_{i}").glob("*.translated.json"))) for i in range(1,5))
    set_status("FINISHED" if completed==manifest["batches"] else "FINISHED_WITH_PENDING",completed_batches=completed,
               pending_batches=manifest["batches"]-completed,worker_results=result)
    print(json.dumps({"completed_batches":completed,"pending_batches":manifest["batches"]-completed,
                      "worker_results":result,"note":"Pending batches can resume with same command."},ensure_ascii=False))
if __name__=="__main__":main()
