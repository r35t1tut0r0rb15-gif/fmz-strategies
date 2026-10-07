# #132298 M-Language-Turtle-Trading-strategy-implementationsV-10 -> `fmz_132298_turtle_20_breakout_v10`

- Source: https://www.fmz.com/strategy/132298 (MyLanguage, author 发明者量化-小小梦, FMZ last
  modified 2019-01-28 11:16:10). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model on daily bars. |
| 2 | PASS | Channels in bars; stop/add distances in ATR. |
| 3 | PASS | BitMEX XBTUSD in the header only. |
| 4 | DONE | Lot formula, 4-unit cap, adds, TRADE_AGAIN -> `original_sizing.txt`; the add rule is kept only as the stop reference. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same family as #126968 (different rules: one channel, no skip filter). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`entry_period` [10, 20, 30] x `exit_period` [5, 10, 15] x `stop_atr` [1.5, 2, 3] = **27 trials**.
ATR 26, add step 0.5 ATR, 4 units fixed.

## Ambiguities resolved

- Source order puts the add lines before the exits, and there is one signal per bar, so an add
  bar postpones the exit checks to the next bar (as on FMZ).
- `FREQ = "1D"` broker days from the backtest header `period: 1d`.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
