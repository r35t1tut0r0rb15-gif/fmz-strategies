# #483048 基于Bollinger带策略应用的动态出场交易系统-Dynamic-Exit-Trading-System-Based-on-Bollinger-Bands-Application -> `fmz_483048_bollinger_reentry_band_touch_exit_1d`

- FMZ source id: 483048 (lineage).
- Source: https://www.fmz.com/strategy/483048 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:13:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; band-touch closes as exit signals. |
| 2 | PASS | Bollinger bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1000 % of equity quoted (sizing, not ported). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `mult` [2.0, 2.5]: **4 trials**; defaults 10 / 2 (the source's).

## Ambiguities resolved

- The band-touch closes are bar-range checks through `strategy.close`: exit signals at the next open (rule 3, as
  #489638), acting on the position held at the bar's start (as #430850). A long and a short on one bar: the later
  short wins.
- REVERSAL INTENDED. No stops. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
