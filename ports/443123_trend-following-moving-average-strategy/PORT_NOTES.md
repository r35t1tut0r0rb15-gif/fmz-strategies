# #443123 Trend Following Moving Average Strategy -> `fmz_443123_close_vs_prior_channel_mid_reversal_stock`

- FMZ source id: 443123 (lineage).
- Source: https://www.fmz.com/strategy/443123 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-29 14:00:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs channel mid-line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and per-contract commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427308. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50]: **2 trials**.

## Ambiguities resolved

- Same rules as #442842. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
