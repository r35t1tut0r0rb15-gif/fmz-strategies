# #438777 RSI多空分歧指标交易策略RSI-Bullish-and-Bearish-Divergence-Trading-Strategy -> `fmz_438777_rsi20_divergence_reversal`

- FMZ source id: 438777 (lineage).
- Source: https://www.fmz.com/strategy/438777 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 12:09:54). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI pivots and divergences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438777. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [20, 14] x `lb` [5, 3]: **4 trials**; pivot sides swept together; range 5-60 fixed.

## Ambiguities resolved

- Strict pivots; exits only at the opposite entry. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
