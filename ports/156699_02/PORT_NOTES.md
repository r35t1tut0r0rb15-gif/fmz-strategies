# #156699 均线策略范例02 -> `fmz_156699_ma_high_low_reverse`

- Source: https://www.fmz.com/strategy/156699 (MyLanguage, author 发明者量化-小小梦, FMZ last
  modified 2019-07-12 10:23:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | PASS | Bar-count MAs only. |
| 3 | PASS | No venue code. |
| 4 | DONE | No sizing code (one lot); `original_sizing.txt` records that. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [3, 5, 8, 13] = **4 trials** (the source uses 5 for all three averages).

## Ambiguities resolved

- One signal per bar in source order: the reversal lines come before the exits.
- No backtest header: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`: close breaking an envelope made of MAs of highs and lows.

## Marks (2026-10-07)

`bar_size_pending`
