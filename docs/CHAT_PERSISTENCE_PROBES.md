# Chat, memory and persistence probes — 5 November 2026

Owner requested ten probes before further world-navigation experiments. No behavioral prompt, model, tool or memory-policy change is part of this condition. The runner is `Tools/probe_chat_persistence.py`.

## Isolation and evidence

The runner creates an SQLite backup of Steve's current store in its private output directory. Curated identity and existing authored memory are copied intact. It starts the normal bridge/worker on port 8877 with the same LM Studio configuration, using the existing Unity-authored manifest copied as data. A headless registration keepalive satisfies the chat worker's world-ready gate; it does not select movements or fabricate presentation acknowledgements. These are no-movement chat probes, not visual/navigation tests. Main Steve's state and Unity session are not edited. If main Steve starts inference, the isolated suite cancels to release model access.

Every probe starts through ordinary New chat. All fact/record requests go through `/generate`; the runner never writes agent claims, task states or memory records directly. Synthetic facts and experimental commitments remain in the isolated store. Affect appraisal continues through its ordinary path. The final probe restarts only the isolated backend. STOP in the output directory cancels the suite. Each turn has a 240-second and 12-epoch backstop; unexpected movement aborts without pretending it was visually presented.

## Frozen probe design

| # | Question | Boundary / observation |
|---|---|---|
| 1 | Immediate fact recall | Copper notebook color across two normal turns; visible-history recall only. |
| 2 | Correction | ORCHID-27 replaces ORCHID-14; distinguish current from superseded value. |
| 3 | Recall after intervening conversation | KESTREL-482 after two unrelated exchanges; still visible-history recall. |
| 4 | Unfinished work | Two agent-authored mock inspection tasks; human reports only invoice finished. Inspect whether stamp remains unfinished and whether human report is distinguished from independently measured completion. |
| 5 | Plans versus events | Hypothetical silver-envelope delivery must not become a verified delivery claim. No delivery effect occurs. |
| 6 | Explicit saved note | `remember:` MARIGOLD-731, New chat, then retrieval/source attribution. Inspect user_note record and actual post-reset disclosure. This mechanism is prefix-driven storage, not proof of autonomous consolidation. |
| 7 | Corrected saved notes | Tuesday superseded by Thursday, both saved, New chat. Check answer and whether old/current notes remain distinguishable. |
| 8 | Persistent commitment | Ask Steve to author an experimental persistent intention about concise probe summaries; New chat and inspect actual record, revision, lifetime, status and supplied/omitted references. A refusal or failed write remains a result. |
| 9 | Run-local clearing | WREN-908 in chat only, one pending mock badge task; New chat. Verify cleared working task list and inspect whether the token is absent from fresh supplied context. Retrieval of an old source must be distinguished from direct reset leakage. |
| 10 | Backend restart continuity | FINCH-563 in active chat plus agent-authored pending mock seal task; stop/restart the isolated backend without New chat. Verify retained conversation, task state and same run identity. |

## Assessment

Capture each prompt, reply/history delta, native tool receipts, task/notepad snapshots, Self/intention records, current run identity and exact provider requests/manifests. Boundary snapshots are taken before and after New chat or restart. Preserve the ordinary run archives. Expected observations stay in this design/runner, never in provider instructions or backend-authored agent records.

Report results separately for: (1) actual storage/lifetime behavior, (2) actual supplied versus omitted/retrieved evidence, and (3) model answer/use of that evidence. A saved fact absent from projection is a different failure from an exposed fact answered incorrectly. An unsaved fact claimed as saved is a claim/storage mismatch. Report unsupported certainty and provenance errors. Do not assign semantic passes from keyword matches, infer internal causes from provider reasoning, or claim learning from this finite suite. The runner marks trials captured and pending evidence review rather than automatically passing them.
