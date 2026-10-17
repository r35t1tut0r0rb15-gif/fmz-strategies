# #431924 基于快速RSI的风控复合交易策略Fast-RSI-Risk-Control-Compound-Futures-Trading-Strategy -> `fmz_431924_noro_fast_rsi_robot`

- FMZ source id: 431924 (lineage).
- Source: https://www.fmz.com/strategy/431924 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-13 11:36:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | RSI levels and bar colour / body filters |
| 3 | PASS | Exchange pair in the header only (BitMEX in the title only). |
| 4 | DONE | The capital % lot with the martingale multiplier stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [25, 15] x `open_bars` [4, 2]: **4 trials**; RSI 7 and the body filters fixed.

## Ambiguities resolved

- Adds not ported (average = first fill); close_all after an entry leaves the bar flat. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
