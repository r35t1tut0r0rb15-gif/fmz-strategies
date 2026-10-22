# #440458 Dual Moving Average Confluence Strategy -> `fmz_440458_dual_ema_ribbons_long_trail`

- FMZ source id: 440458 (lineage).
- Source: https://www.fmz.com/strategy/440458 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-30 17:13:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-tested trail and target |
| 2 | PASS | EMA ribbon gaps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ts` [0.03, 0.05] x `tp` [0.03, 0.06]: **4 trials**; trailing profit 1 % and the ribbon lengths fixed.

## Ambiguities resolved

- Bodies for highs / lows (Renko option on); LongsOnly; bar-tested exits. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
