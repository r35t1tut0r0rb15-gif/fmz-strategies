# #446560 Moving Average Crossover Strategy -> `fmz_446560_sma10_30_cross_long_bracket_short_next_open_reversal`

- FMZ source id: 446560 (lineage).
- Source: https://www.fmz.com/strategy/446560 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-29 16:38:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close |
| 2 | PASS | SMA crossings with a long bracket |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 50]: **4 trials**; the 1 % / 3 % levels fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); shorts close at the next open after the fill. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
