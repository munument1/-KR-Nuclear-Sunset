"""Exact SCDA/SCTX identities of the verified v1.0.7 CP949 display outputs.

These hashes allow byte-identical repeat installation; no unknown script or
partial edit is accepted. Bytecode itself is not distributed here.
"""
import hashlib
FINALIZED = {'ChallengeWaterSCRIPT': ('f592d5dddfc18656b966d60b4a23c99fe6d2f459679ad645214ee32e35437ace',
                          '884a917a35c7c0aa8bca7467dae9f7bf51d0ae0d01ece62d97bf2e65625a9eab'),
 'SCPTFlawPromptAddictive': ('cc6b63f59a34b862e8a5530dff0828d113e414e42c482a1029d6cc788ecd24c3',
                             'e3be111a0e0c5177f20dd181de84b399774c4e337a8e00dd4ff33b378b44f6eb'),
 'SCPTFlawPromptBottomlessStomach': ('3a6efa4daefb4dd51bceb09063deafe9560b5bb6250ff4971c00f463bb2fc0b9',
                                     'f809301960b9f0a1f20878e94abeb8b0f7514afe652013d8b217d0de39915273'),
 'SCPTFlawPromptCongenitalHeartDefect': ('5848a201ba32c22386fce79564eb6631886f415d03fc51e527c5213bbedd4c00',
                                         '0a30c6d702b7d3dd5ddc379be68fa1c4a7cdc7a8e54ab65daf524a3248361fbb'),
 'SCPTFlawPromptHumanSieve': ('f592d5dddfc18656b966d60b4a23c99fe6d2f459679ad645214ee32e35437ace',
                              'e5a1037fa47931c12436169e03bc5863fa3758f615d68a4ade4694bb348c60ea'),
 'SCPTFlawPromptParanoid': ('8a2970c9e9d6d58493a153972eefb4d279599611143f561fad08fe12fef311da',
                            'fe8113855e1982daa77f3bea74b45938c837248227fb06328551ed4aba04acee'),
 'SCPTFlawPromptStubborn': ('ed9bf8cab83586bf3b803b7429549c9fd97b324c2f50ad074f96d25330fe7462',
                            'e7f83821ec285c8440206f3b64a35516950213e7a3931ee0618dd4472383f737'),
 'SCPTFlawPromptWhyDoTheyHunger': ('c3efff044b418df7c50cf9dca32c67a6b0cb06a427f0e7dccde42620e9af3c72',
                                   'dfbbfae271ed3acf162c533b7ce0318565e6ddd8caa988f281e28c9130cf88db'),
 'SCPTHomesickLatePrompt': ('ba44dcf3158c0470e4d1ba477f5ac529f7b1a963e7e9fba081e25207e6d22996',
                            '5e58a5b934642a0da62b07588e881ee82c8ea0cc96766e549f97b144b9129800'),
 'SCPTOnHitElysium': ('569d2deb62c19a02779c2313e7e9b2b20d650f5c09570fceae08bd27441afe53',
                      '6a28077497f3cfc65c8120ed57078683e52e156e4389690222aa95d7154bfa37'),
 'SCPTOnLoadedBasePerks': ('5b784171f789dc574c054cfde8be44105b19bdc195b3ae046518a1b7e121d9a4',
                           '3c2412c591f6b69e22bb8182bf46b0dae7eef5de8789d1a5bd62d3cf0f6df026'),
 'SCPTOnUseStealthBoy': ('2010867085026cfe70fa49dff0d45ec9d7804e21fe2690c487c79cd7bb8e4c87',
                         '1451d4079712bfccd57edec37014ba492736fd31c02254228d2093c7bebb3371'),
 'SCPTPatchForJBT': ('a123af728140aa7fe17d15852275b11af60341212bf9025f379cfeef83a01d7f',
                     'eb1de09eae792aba33b7f98fc5be8dd01a9d3578be973776a9284bf46e910165'),
 'SCPTVegasElysiumConstantRun': ('85ab0dd2d6eeeedbaeb558eef41a72c1d0b0cd56dfac8dde52a0d76d548e5f23',
                                 '1b1e0e0cd1bd55ecc969ff0877b8389e07489e319c9cdb47c0b793922b187bd1'),
 'sssSCPTIngestiblesStartup': ('24741b99a90d5b36722329d481f3087b7e486c8b69b0cdf7475026f3b5e9139b',
                               '8e0908cd0ba01d0783ffa5737df37864e06d893194d00e84028990651804ded3')}

def is_reviewed_finalized(edid,scda,sctx):
    return FINALIZED.get(edid)==(hashlib.sha256(scda).hexdigest(),hashlib.sha256(sctx).hexdigest())
