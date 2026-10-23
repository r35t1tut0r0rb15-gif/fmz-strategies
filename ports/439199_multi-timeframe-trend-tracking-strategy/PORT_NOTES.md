# #439199 Multi Timeframe Trend Tracking Strategy -> `fmz_439199_intellitrader_always_buy_tp1_sl3_engine_long_only`

- FMZ source id: 439199 (lineage).
- Source: https://www.fmz.com/strategy/439199 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-18 12:01:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits at the next open after a bar that reached the levels |
| 2 | PASS | Always-in long with signal-close take profit and stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.01, 0.02] x `sl` [0.03, 0.05]: **4 trials**; all filters off as written.

## Ambiguities resolved

- v3 local declarations leave every filter true: buy on every bar. Running high includes the signal bar. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "always_long_bracket"`.

## Marks

`none`
