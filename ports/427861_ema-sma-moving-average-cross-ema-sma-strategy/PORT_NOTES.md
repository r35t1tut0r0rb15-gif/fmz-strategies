# #427861 Moving Average Cross EMA SMA Strategy -> `fmz_427861_ema_sma_state`

- FMZ source id: 427861 (lineage).
- Source: https://www.fmz.com/strategy/427861 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-26 11:27:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 8] x `slow` [30, 50]: **4 trials**; defaults 13 / 30 (the source's).

## Ambiguities resolved

- VWMA and RSI drawn only (no volume reaches an order). Repeated same-side entries are ignored.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
