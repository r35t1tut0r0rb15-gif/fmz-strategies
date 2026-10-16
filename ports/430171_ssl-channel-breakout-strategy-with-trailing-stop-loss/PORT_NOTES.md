# #430171 SSL Channel Breakout Strategy with Trailing Stop Loss -> `fmz_430171_ssl_channel_flip`

- FMZ source id: 430171 (lineage).
- Source: https://www.fmz.com/strategy/430171 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-25 17:40:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the inert exits stated. |
| 2 | PASS | Moving averages of highs and lows. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20, 40]: **3 trials**.

## Ambiguities resolved

- The stop closes use ids that match no entry: inert, as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`none`
