# #440443 真实相对运动MA均线策略True-Relative-Movement-Moving-Average-Strategy -> `fmz_440443_tsi_rsi_trm_long`

- FMZ source id: 440443 (lineage).
- Source: https://www.fmz.com/strategy/440443 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 16:04:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TSI and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tsi_short` [5, 13] x `rsi_len` [5, 14]: **4 trials**; TSI long 25 and signal 14 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
