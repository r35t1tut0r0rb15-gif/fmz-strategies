# #468316 动态仓位管理RSI超买反转策略-Dynamic-Position-Management-RSI-Overbought-Reversal-Strategy -> `fmz_468316_rsi2_two_bar_overbought_below_sma200_short`

- FMZ source id: 468316 (lineage).
- Source: https://www.fmz.com/strategy/468316 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:29:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI 2 overbought shorts under the SMA 200 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed quantities and scale-in sizes stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_long` [200, 100] x `rsi_th` [75, 90] x `exit_th` [30, 50]: **8 trials**; the SMA 10 / 30 exit fixed.

## Ambiguities resolved

- Scale-ins never fill (pyramiding 1). Short only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
