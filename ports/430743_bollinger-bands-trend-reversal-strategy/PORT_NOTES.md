# #430743 Bollinger Bands Trend Reversal Strategy -> `fmz_430743_bb_trend_touch_reversal`

- FMZ source id: 430743 (lineage).
- Source: https://www.fmz.com/strategy/430743 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 11:29:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving target fixed at entry (rule 2). |
| 2 | PASS | Bollinger bands, an EMA and a reward ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out cash order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `riskreward` [1.5, 1.0]: **4 trials**; 2 sd and EMA 200 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the target follows the opposite band every bar; fixed at the signal bar here.
- Flat follows the house bracket on bars. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
