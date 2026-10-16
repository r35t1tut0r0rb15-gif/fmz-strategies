# #428704 Adaptive Trailing Stop Strategy -> `fmz_428704_ut_bot_atr_line`

- FMZ source id: 428704 (lineage).
- Source: https://www.fmz.com/strategy/428704 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 15:06:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428704. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_period` [10, 20]: **4 trials**; close as source fixed.

## Ambiguities resolved

- Before the ATR exists the line is na (as Pine's max/min with na) and then restarts from 0.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
