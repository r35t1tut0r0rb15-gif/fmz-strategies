# #361827 吕神简易波动率策略Pine语言版本 -> `fmz_361827_log_return_ma_range_breakout`

- Source: https://www.fmz.com/strategy/361827 (PineScript, author 发明者量化, FMZ last
  modified 2022-05-29 20:51:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | `log(C)/log(C[N-1]) - 1` -> `log(C/C[N-1])` (scale-free). |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | qty = equity / close -> `original_sizing.txt`. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Pine translation of #200131 (JS), with a different band (range of the MA, not of vix) and entries only from flat. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [25, 50, 100] = **3 trials**.

## Ambiguities resolved

- Criterion-2 change of the indicator as in #200131.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`none`
