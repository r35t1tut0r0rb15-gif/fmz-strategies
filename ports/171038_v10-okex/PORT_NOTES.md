# #171038 牛熊小卖部策略V10_OKex合约 -> `fmz_171038_m30_vs_daily_range_regime`

- Source: https://www.fmz.com/strategy/171038 (JavaScript, author 区班量化, FMZ last modified
  2019-10-24 13:44:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | The regime uses bar records only; polled every 10 s, evaluated per completed 30-min bar in the port. Tick price is used only for order prices and for the adds (sizing). |
| 2 | ADAPT | The +/-3 % centre test -> `center_atr` x daily ATR(14). |
| 3 | PASS (screen: REVIEW) | OKEx quarterly contract and 5x leverage are venue set-up only; the signal needs no funding, order book or swap mechanics. |
| 4 | DONE | Position cap (half the account), 20 %/30 % adds, order cancelling, the alternating status that re-buys every other loop -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author's #170557 and #177631 (rejected) are different (inventory ladders). |
| 7 | IGNORED | The name's "年化" style claims are not used. |

## Declared grid (criterion 5)

`mnum` [10, 20, 40] x `dnum` [3, 5, 10] x `center_atr` [0.5, 1, 1.5] = **27 trials**.

## Ambiguities resolved

- Both channels exclude the forming bar (the author's comments). For the daily channel the
  forming bar is today's broker day, so the dnum days before it are used.
- The status variable toggles 20/21 on consecutive loops; that only decides whether the
  "initial" buy repeats, i.e. sizing. The signal is the regime.
- Neutral ("monkey") does nothing: its body is commented out.
- `FREQ = "30min"` from the code's `GetRecords(PERIOD_M30)` (the backtest header's `1d` is the
  backtest's base period, not the bars the code reads).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_breakout_regime"`: a lower-timeframe channel breaking a
higher-timeframe range sets a directional regime.

## Marks (2026-10-07)

`none`
