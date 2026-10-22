# #440103 Key Reversal Backtest Strategy -> `fmz_440103_key_reversal_up_state`

- FMZ source id: 440103 (lineage).
- Source: https://www.fmz.com/strategy/440103 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 16:11:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

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

- Price amounts as fractions of the signal close; close-tested state. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
