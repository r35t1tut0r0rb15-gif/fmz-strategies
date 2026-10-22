# #443246 MACDRSI与EMA策略MACD-RSI-and-EMA-Strategy -> `fmz_443246_ema_macd_rsi_signal_agreement_reversal`

- FMZ source id: 443246 (lineage).
- Source: https://www.fmz.com/strategy/443246 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-01 12:23:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA, MACD and RSI agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len2` [20, 50] x `rsi_signal_len` [20, 9]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
