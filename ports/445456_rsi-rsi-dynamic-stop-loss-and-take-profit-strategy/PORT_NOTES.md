# #445456 RSI动态止损止盈策略RSI-Dynamic-Stop-Loss-and-Take-Profit-Strategy -> `fmz_445456_rsi_pivot_divergence_falling_volume_2pct_stop_3m_reversal`

- FMZ source id: 445456 (lineage).
- Source: https://www.fmz.com/strategy/445456 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-19 15:54:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop at the signal close as a fraction of the fill |
| 2 | PASS | RSI pivot divergences with falling volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 21] x `stop_pct` [0.02, 0.01]: **4 trials**; levels 70 / 30.

## Ambiguities resolved

- Previous pivots via valuewhen(..., 1); stop at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
