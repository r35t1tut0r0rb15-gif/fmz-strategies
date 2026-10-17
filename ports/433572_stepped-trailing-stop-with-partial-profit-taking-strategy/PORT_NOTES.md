# #433572 Stepped Trailing Stop with Partial Profit Taking Strategy -> `fmz_433572_golden_cross_stepped_stop`

- FMZ source id: 433572 (lineage).
- Source: https://www.fmz.com/strategy/433572 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-28 16:05:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (the stop ladder pending) |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick ladder quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.4, 1.0] x `tp_atr` [1.2, 3.0]: **4 trials**; SMA 14 / 28 and ATR 14 fixed.

## Ambiguities resolved

- Tick distances as ATR fractions; the stop ladder is pending (trailing_stop_pending). Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
