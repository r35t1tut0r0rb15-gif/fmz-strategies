# #437044 BankNifty超级趋势交易策略BankNifty-Supertrend-Trading-Strategy -> `fmz_437044_supertrend_side_state_delay`

- FMZ source id: 437044 (lineage).
- Source: https://www.fmz.com/strategy/437044 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 17:09:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Supertrend side; the point stop is pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point stop and trail inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [50, 20] x `factor` [3.0, 2.0]: **4 trials**; delay 10 fixed; the stop is pending.

## Ambiguities resolved

- Session overridden; delay counts from the data start; every-bar point stop and trail pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
