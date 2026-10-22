# #440066 Linear Regression and Dual Moving Average Short Term Strategy -> `fmz_440066_lr_ssl_dema_short`

- FMZ source id: 440066 (lineage).
- Source: https://www.fmz.com/strategy/440066 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 12:33:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression channel crossings and a smoothed DEMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [89, 50] x `length` [200, 100]: **4 trials**.

## Ambiguities resolved

- Short only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
