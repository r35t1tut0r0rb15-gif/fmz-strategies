# #439036 Key Reversal Backtest Strategy -> `fmz_439036_key_reversal_down_state`

- FMZ source id: 439036 (lineage).
- Source: https://www.fmz.com/strategy/439036 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 10:56:52). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested state |
| 2 | ADAPT | Price-unit target / stop -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND439036. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_frac` [0.00048, 0.02] x `sl_frac` [0.00024, 0.01]: **4 trials**; look-back 1 fixed.

## Ambiguities resolved

- Price-unit target / stop -> fractions; same-bar state reset as written. Short only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
