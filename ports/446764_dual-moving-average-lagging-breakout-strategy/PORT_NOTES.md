# #446764 Dual Moving Average Lagging Breakout Strategy -> `fmz_446764_close_sma14_cross_with_sma50_order_reversal`

- FMZ source id: 446764 (lineage).
- Source: https://www.fmz.com/strategy/446764 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-01 11:58:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket not ported (mark) |
| 2 | PASS | SMA crossings in the trend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the ATR bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [14, 20] x `len2` [50, 100]: **4 trials**.

## Ambiguities resolved

- Re-sent bracket pending. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
