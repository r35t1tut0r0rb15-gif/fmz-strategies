# #438022 Buy Low Volatility VS Buy High Volatility Strategy -> `fmz_438022_low_volatility_buy_timed_exit`

- FMZ source id: 438022 (lineage).
- Source: https://www.fmz.com/strategy/438022 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 11:33:58). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the limit at the close read as a close at the next open |
| 2 | PASS | ATR ratio and a bar count |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target_ratio` [1.0, 0.8] x `hold_bars` [5, 10]: **4 trials**; ATR 14 and the 70-bar average fixed; mode low volatility.

## Ambiguities resolved

- Limit at the close read as a next-open close. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
