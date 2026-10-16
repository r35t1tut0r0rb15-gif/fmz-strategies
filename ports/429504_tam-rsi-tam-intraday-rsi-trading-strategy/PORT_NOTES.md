# #429504 TAM日内RSI交易策略TAM-Intraday-RSI-Trading-Strategy -> `fmz_429504_two_rsi_momentum_long`

- FMZ source id: 429504 (lineage).
- Source: https://www.fmz.com/strategy/429504 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 16:58:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_len2` [14, 21] x `close_len2` [50, 30]: **4 trials**; RSI 2 / 7 and the 50 levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
