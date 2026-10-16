# #430749 Dual Moving Average Bollinger Bands Trend Following Strategy -> `fmz_430749_augmented_bb_dip_long`

- FMZ source id: 430749 (lineage).
- Source: https://www.fmz.com/strategy/430749 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 14:15:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving target fixed at entry (rule 2). |
| 2 | ADAPT | The inert price-unit spread cap dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Round(equity / close) per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [20, 50] x `stop_loss` [3.0, 5.0]: **4 trials**; 2 sd fixed.

## Ambiguities resolved

- Pending (not emitted as written): the target follows the EMA 20 every bar; fixed at the signal bar here.
- The inert spread cap dropped. Flat follows the house bracket on bars. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
