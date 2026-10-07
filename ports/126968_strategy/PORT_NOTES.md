# #126968 麦语言海龟策略体验 -> `fmz_126968_turtle_20_55_breakout`

- Source: https://www.fmz.com/strategy/126968 (MyLanguage, author Zero, FMZ last modified
  2021-10-27 12:32:17). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Bar rules on daily bars. MULTSIG makes the original intrabar; the port evaluates on completed bars. |
| 2 | PASS | Channels in bars, stop and add distances already in ATR. |
| 3 | PASS | Binance spot in the backtest header only. |
| 4 | DONE | Lot = 1 % equity / ATR, 4-unit cap, pyramid adds, TRADE_AGAIN/MULTSIG -> `original_sizing.txt`. The add rule is kept only as the stop reference (see module). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No screen group (`DG`), no 0.65-0.80 group (`ND`). Related by name only to #132298 (also a turtle demo, different rules: no 55-bar entry, no skip filter). |
| 7 | IGNORED | No claim used. |

## Declared grid (criterion 5)

`short_period` [10, 20, 30] x `long_period` [40, 55, 80] x `stop_atr` [1.5, 2, 3] = **27 trials**.
Fixed: `exit_period` 10, `atr_period` 20, `add_atr` 0.5, `max_units` 4 (the original's values).

## Ambiguities resolved

- `HV/LV` exclude the current bar (MyLanguage rule), so `CROSSUP(C,HV(H,20))` is a close
  above the prior 20-bar high.
- `ISLASTFAILURE` starts at 1, becomes 1 after a stop exit and 0 after a 10-bar-channel exit;
  if both fire on one bar it is 1 (as written: `IF(NEEDSTOP OR NEEDLEAVE, NEEDSTOP, ...)`).
- An exit and an add on the same bar: the exit wins (the position is closed either way).
- `FREQ = "1D"` broker days from the backtest header `period: 1d`.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`: entries on breaks of prior-N-bar highs/lows, exits on a shorter
opposite channel. Proposed for all turtle/Donchian ports.

## Marks (2026-10-07)

`none`
