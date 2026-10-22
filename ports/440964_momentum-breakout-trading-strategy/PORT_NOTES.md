# #440964 Momentum Breakout Trading Strategy -> `fmz_440964_ut_bot_zlsma_adx_profit_guard`

- FMZ source id: 440964 (lineage).
- Source: https://www.fmz.com/strategy/440964 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 10:55:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested exits |
| 2 | PASS | ATR trail, ZLSMA and ADX |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [3.0, 2.0] x `adx_min` [14, 20]: **4 trials**; the exit ratios fixed.

## Ambiguities resolved

- Close-tested exits; short profit price as written. Entries only from flat. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
