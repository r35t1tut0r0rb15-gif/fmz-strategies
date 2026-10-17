# #433126 3 Min Short Only Expert Advisor Strategy -> `fmz_433126_triple_red_short_t3`

- FMZ source id: 433126 (lineage).
- Source: https://www.fmz.com/strategy/433126 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 15:58:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions (ES reading) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The account / ticker / quantity alert fields stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.4, 1.0] x `t3_len` [150, 300]: **4 trials**; b 0.7, stop = 4 x target and ATR 14 fixed.

## Ambiguities resolved

- Short above the T3 as written; tick bracket as ATR (ES reading). Short only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
