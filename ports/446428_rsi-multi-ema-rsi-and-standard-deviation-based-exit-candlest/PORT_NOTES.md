# #446428 基于多重移动平均线RSI-和标准差出场的蜡烛线高度突破交易策略Multi-EMA-RSI-and-Standard-Deviation-Based-Exit-Candlestick-Height-Breakout-Trading-Strategy -> `fmz_446428_prior4_range_break_ema55_flag_exits_reversal`

- FMZ source id: 446428 (lineage).
- Source: https://www.fmz.com/strategy/446428 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 16:13:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the prior bars' range excludes the current bar |
| 2 | PASS | Range breakouts with an EMA filter and band / EMA exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`candle_count` [4, 3] x `exit_len` [12, 20]: **4 trials**; the EMA filter length and the std-dev multiplier fixed.

## Ambiguities resolved

- Flags and position can drift apart as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
