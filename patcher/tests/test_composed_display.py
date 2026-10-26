import hashlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import nskr_composed_display as c
from nskr_compiled_scpt import _walk, _slots, _decode_record


def sub(key, value):
    return key + struct.pack('<H', len(value)) + value


def record(sig, body, form=0x800, compressed=False):
    payload = struct.pack('<I', len(body))+zlib.compress(body) if compressed else body
    return sig+struct.pack('<5I', len(payload), 0x40000 if compressed else 0, form, 0, 0)+payload


def group(label, kind, body):
    return b'GRUP'+struct.pack('<III', len(body)+24, label, kind)+b'\0'*8+body


def plugin(body, masters=()):
    return record(b'TES4', sub(b'HEDR', b'\0'*12)+b''.join(
        sub(b'MAST', m.encode()+b'\0')+sub(b'DATA', b'\0'*8) for m in masters), 0)+body


class CompositionTests(unittest.TestCase):
    def test_reported_failure_prompt_composes_with_skill_and_preserves_scripts(self):
        prompt='이봐. 감옥도 그렇게 나쁘진 않아.'
        # Same master-owned AVSpeech as Long15Reloaded.esm INFO xx00C2FF.
        untouched=(sub(b'KNAM', struct.pack('<I', 0x4BB))+
                   sub(b'CTDA', bytes(range(28)))+sub(b'SCDA', b'\x15\x00opcode')+
                   sub(b'SCTX', b'Set Quest.stage to 1')+
                   sub(b'NAM1', '[실패] 감옥엔 안 가.'.encode()+b'\0'))
        raw=plugin(record(b'INFO', untouched+sub(b'RNAM', prompt.encode()+b'\0')))
        before='[화술] '.encode('cp949')+prompt.encode()
        with self.assertRaises(UnicodeDecodeError):before.decode('utf-8')
        out, changes, issues=c.patch_bytes(raw, 'Long15Reloaded.esm')
        self.assertEqual(len(changes), 1)
        self.assertFalse(issues)
        self.assertIn(untouched, out)
        self.assertIn(prompt.encode('cp949')+b'\0', out)
        self.assertEqual(('[화술] '.encode('cp949')+prompt.encode('cp949')).decode('cp949'), '[화술] '+prompt)
        self.assertEqual(c.patch_bytes(out, 'Long15Reloaded.esm'), (out, [], []))

    def test_general_dialogue_null_challenge_and_unrelated_fields_unchanged(self):
        body=sub(b'RNAM', '일반 선택지'.encode()+b'\0')+sub(b'NAM1', 'NPC 자막'.encode()+b'\0')
        for suffix in (b'', sub(b'KNAM', b'\0'*4)):
            raw=plugin(record(b'INFO', body+suffix))
            self.assertEqual(c.patch_bytes(raw, 'Example.esp'), (raw, [], []))

    def test_shared_topic_fallback_resolves_master_ownership_across_plugins(self):
        topic=0x800
        base=plugin(record(b'DIAL', sub(b'FULL', '공유 선택지'.encode()+b'\0'), topic))
        # The patch owns no DIAL but adds a challenge INFO under the base DIAL.
        info=record(b'INFO', sub(b'KNAM', struct.pack('<I', 0x4BB)), 0x01000801)
        override=plugin(group(topic, 7, info), ['Base.esm'])
        topics=c.challenge_topics(override, 'Override.esp')
        self.assertEqual(topics, {('base.esm', topic)})
        out, changes, issues=c.patch_bytes(base, 'Base.esm', topics)
        self.assertIn('공유 선택지'.encode('cp949')+b'\0', out)
        self.assertEqual(len(changes), 1)
        self.assertEqual(c.patch_bytes(base, 'Other.esm', topics), (base, [], []))
        self.assertEqual(c.patch_bytes(out, 'Base.esm', topics), (out, [], []))

    def test_chem_expiration_template_composes_with_cp949_item_name(self):
        template='%s 효과가 사라졌습니다.'
        raw=plugin(record(b'GMST', sub(b'EDID', b'sChemsWornOff\0')+
                          sub(b'DATA', template.encode()+b'\0')))
        out, changes, issues=c.patch_bytes(raw, 'NSKR UI Strings.esp')
        result=template.encode('cp949').replace(b'%s', '스팀팩'.encode('cp949'))
        self.assertEqual(result.decode('cp949'), '스팀팩 효과가 사라졌습니다.')
        self.assertIn(template.encode('cp949')+b'\0', out)
        self.assertEqual(changes[0]['from_encoding'], 'utf-8')
        self.assertEqual(changes[0]['to_encoding'], 'cp949')
        self.assertFalse(issues)
        self.assertEqual(c.patch_bytes(out, 'NSKR UI Strings.esp'), (out, [], []))

    def test_addiction_withdrawal_and_hacking_keep_substitution_tokens(self):
        cases=[('sChemsAddicted','%s 에 중독되었습니다.'),
               ('sChemsWithdrawal','%s 금단 증상을 겪고 있습니다.'),
               ('sHackIneligible','이 단말기를 해킹하려면 %s 스킬이 %d 이상이어야 합니다.')]
        for edid,text in cases:
            with self.subTest(edid=edid):
                raw=plugin(record(b'GMST',sub(b'EDID',edid.encode()+b'\0')+sub(b'DATA',text.encode()+b'\0')))
                out,changes,issues=c.patch_bytes(raw,'NSKR UI Strings.esp')
                self.assertIn(text.encode('cp949')+b'\0',out)
                self.assertEqual(len(changes),1)
                self.assertFalse(issues)
                self.assertEqual(c.patch_bytes(out,'NSKR UI Strings.esp'),(out,[],[]))

    def test_compressed_info_and_enclosing_group_lengths(self):
        info=record(b'INFO', sub(b'KNAM', struct.pack('<I', 0x4BB))+
                    sub(b'RNAM', '긴 한국어 선택지'.encode()+b'\0'), compressed=True)
        raw=plugin(group(0x800, 7, info))
        out, changes, issues=c.patch_bytes(raw, 'Base.esm')
        self.assertEqual(_walk(out, lambda h,d:d), out)
        seen=[]
        def visit(h,d):
            if h[:4]==b'INFO':seen.extend(_slots(_decode_record(h,d)))
            return d
        _walk(out, visit)
        self.assertIn('긴 한국어 선택지'.encode('cp949')+b'\0', [v for k,h,v in seen])
        self.assertEqual(len(changes), 1)
        self.assertFalse(issues)

    def test_unsupported_characters_are_preserved_and_reported(self):
        raw=plugin(record(b'INFO', sub(b'KNAM', struct.pack('<I', 0x4BB))+
                          sub(b'RNAM', '선택😀'.encode()+b'\0')))
        out, changes, issues=c.patch_bytes(raw, 'Base.esm')
        self.assertEqual(out, raw)
        self.assertFalse(changes)
        self.assertEqual(issues[0]['reason'], 'unsupported_cp949')

    def test_malformed_group_is_rejected(self):
        raw=plugin(group(0x800, 7, b'INFO'))
        with self.assertRaises(ValueError):c.patch_bytes(raw, 'Base.esm')

    def test_unrepresentable_prompt_is_visible_in_text_report(self):
        from nskr_output import format_plugin_report
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            raw=plugin(record(b'INFO', sub(b'KNAM', struct.pack('<I', 0x4BB))+
                              sub(b'RNAM', '선택😀'.encode()+b'\0')))
            (root/'Base.esm').write_bytes(raw)
            rows=[{'output_path':'Base.esm','status':'staged',
                   'output_sha256':hashlib.sha256(raw).hexdigest()}]
            c.finalize(root,rows)
            self.assertEqual((root/'Base.esm').read_bytes(),raw)
            text=format_plugin_report({'files':rows})
            self.assertIn('Base.esm',text)
            self.assertIn('unsupported_cp949',text)
            self.assertIn('INFO/RNAM 00000800',text)

    def test_finalizer_resolves_all_providers_and_updates_report_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=plugin(record(b'DIAL', sub(b'FULL', '선택지'.encode()+b'\0')))
            override=plugin(group(0x800, 7, record(b'INFO', sub(b'KNAM', struct.pack('<I', 0x4BB)), 0x01000801)), ['Base.esm'])
            rows=[]
            for name, raw in [('Base.esm', base), ('Override.esp', override)]:
                (root/name).write_bytes(raw)
                rows.append({'output_path':name, 'status':'staged', 'output_sha256':hashlib.sha256(raw).hexdigest()})
            c.finalize(root, rows)
            self.assertEqual(len(rows[0]['composition_display']), 1)
            self.assertEqual(rows[0]['output_sha256'], hashlib.sha256((root/'Base.esm').read_bytes()).hexdigest())
            self.assertEqual((root/'Override.esp').read_bytes(), override)
            snapshot=[(root/r['output_path']).read_bytes() for r in rows]
            c.finalize(root, rows)
            self.assertEqual(snapshot, [(root/r['output_path']).read_bytes() for r in rows])
