# #432780 康纳双均线RSI反转交易策略Connors-Dual-Moving-Average-RSI-Reversal-Trading-Strategy -> `fmz_432780_connors_rsi2_sma_as_written`

- FMZ source id: 432780 (lineage).
- Source: https://www.fmz.com/strategy/432780 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 14:20:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | RSI levels, SMA trend and percentages of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the close-checked stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [2, 3] x `exit_ma` [5, 10]: **4 trials**; SMA 200, the levels 5 / 95 and the 3 % test fixed.

## Ambiguities resolved

- Inverted stop tests ported as written (decision owed). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
