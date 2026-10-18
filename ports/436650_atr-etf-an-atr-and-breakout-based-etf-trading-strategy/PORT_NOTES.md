# #436650 基于ATR和突破的ETF交易策略An-ATR-and-Breakout-based-ETF-Trading-Strategy -> `fmz_436650_donchian_atr_stop_trail`

- FMZ source id: 436650 (lineage).
- Source: https://www.fmz.com/strategy/436650 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 16:05:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C94). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Channel breakout with ATR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 40] x `atr_sl_mult` [2.0, 3.0]: **4 trials**; ATR 14, trailing 3.5 ATR over 4 bars and one sequel trade fixed.

## Ambiguities resolved

- Trailing close reaches the entry id only for some counts; short side off, not ported; take profit unused. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
