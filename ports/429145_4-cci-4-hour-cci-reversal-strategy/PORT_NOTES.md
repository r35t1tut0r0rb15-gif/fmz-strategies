# #429145 4小时CCI反转策略4-Hour-CCI-Reversal-Strategy -> `fmz_429145_cci_high_low_reversal`

- FMZ source id: 429145 (lineage).
- Source: https://www.fmz.com/strategy/429145 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-13 15:29:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | Tick distances -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The bracket is ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.000003, 1.0] x `sl_atr` [0.0000015, 0.5]: **4 trials** (the first values are the source's); CCI 11 and -150 / +150 fixed.

## Ambiguities resolved

- The unused KAMA (15-minute security) dropped. Near-zero bracket as written plus a wider declared pair.
- REVERSAL INTENDED. Mark coarse_bar_stop. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`coarse_bar_stop`
