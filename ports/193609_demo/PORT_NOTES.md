# #193609 一根均线-趋势-Demo -> `fmz_193609_single_sma_reverse`

- Source: https://www.fmz.com/strategy/193609 (JavaScript, author 扁豆子, FMZ last modified
  2020-04-11 21:28:30). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Acts once per new bar on the forming bar; the port evaluates on completed bars. |
| 2 | PASS | Bar-count MA only. |
| 3 | PASS (screen: REVIEW) | BitMEX XBTUSD contract is the venue only. |
| 4 | DONE | Fixed `Amount`, ticker order prices -> `original_sizing.txt`. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same logic family as #42451 (long-only SMA slope) but a different rule (price vs MA, both sides). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ma_length` [10, 20, 30, 50, 100] = **5 trials**.

## Ambiguities resolved

- No bar size in the source: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`bar_size_pending`
