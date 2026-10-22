# #440509 Bull Market Tracking System -> `fmz_440509_cowabunga_ema5_cross_atr_target`

- FMZ source id: 440509 (lineage).
- Source: https://www.fmz.com/strategy/440509 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-31 11:01:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_tp` [0.67, 2.0] x `len4` [162, 81]: **4 trials**; the other lengths and the hours fixed.

## Ambiguities resolved

- Tick target as an ATR multiple; offset-free trail places nothing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
