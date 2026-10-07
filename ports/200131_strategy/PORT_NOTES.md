# #200131 吕神-简易波动率策略 -> `fmz_200131_log_return_range_breakout`

- Source: https://www.fmz.com/strategy/200131 (JavaScript, author 扁豆子, FMZ last modified
  2020-04-23 12:25:16). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Indicator updated once per new bar from the forming bar; the port uses completed bars. |
| 2 | ADAPT | `ln(C)/ln(C_{t-N+1}) - 1` depends on the price scale (sign flips below price 1, blows up near 1) -> the log return `ln(C_t/C_{t-N+1})`. |
| 3 | PASS (screen: REVIEW) | BitMEX XBTUSD contract is the venue only. |
| 4 | DONE | Fixed `Amount`, ticker order prices -> `original_sizing.txt`. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | The description's performance talk is not used. |

## Declared grid (criterion 5)

`n` [45, 90, 180] = **3 trials** (the same N sets the return horizon and the band windows).

## Ambiguities resolved

- The criterion-2 change of the indicator is the main deviation; it preserves the crosses for
  high-priced instruments and makes the rule usable for FX and indices. Flagged in the report.
- An exit and an opposite entry on the same bar are both emitted (the bot does that on two
  polls of the same bar).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`: an N-bar return breaking its own recent range.

## Marks (2026-10-07)

`none`
