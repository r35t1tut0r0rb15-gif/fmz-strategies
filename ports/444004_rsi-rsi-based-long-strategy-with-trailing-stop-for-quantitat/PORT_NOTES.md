# #444004 基于相对强弱指数RSI与止损的多头量化交易策略RSI-based-Long-Strategy-with-Trailing-Stop-for-Quantitative-Trading -> `fmz_444004_rsi14_cross_flat_entries_pct_stop`

- FMZ source id: 444004 (lineage).
- Source: https://www.fmz.com/strategy/444004 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:06:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | RSI level crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantities and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `percent_diff` [5, 10]: **4 trials**; the levels fixed.

## Ambiguities resolved

- The short's same-bar close acts on nothing. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
