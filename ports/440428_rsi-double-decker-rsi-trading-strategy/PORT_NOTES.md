# #440428 双层RSI交易策略Double-Decker-RSI-Trading-Strategy -> `fmz_440428_double_decker_rsi`

- FMZ source id: 440428 (lineage).
- Source: https://www.fmz.com/strategy/440428 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 15:21:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Size 1 is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_rsi` [5, 3] x `slow_rsi` [14, 21]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Opposite signal flattens (close_all after the entry). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
