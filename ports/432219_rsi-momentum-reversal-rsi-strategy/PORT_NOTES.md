# #432219 基于相对强弱指标RSI策略Momentum-Reversal-RSI-Strategy -> `fmz_432219_noro_frsi_dip_long`

- FMZ source id: 432219 (lineage).
- Source: https://www.fmz.com/strategy/432219 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-15 16:29:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and body sizes against their own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND432219. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `limit` [30, 20]: **4 trials**; the body EMA 30 and its 1/4, 1/2 factors fixed.

## Ambiguities resolved

- sps is always 0 as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
