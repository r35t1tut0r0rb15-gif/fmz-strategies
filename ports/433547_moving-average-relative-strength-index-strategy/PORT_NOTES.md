# #433547 Moving Average Relative Strength Index Strategy -> `fmz_433547_rsi_open_sma_sign`

- FMZ source id: 433547 (lineage).
- Source: https://www.fmz.com/strategy/433547 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-28 14:07:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An RSI average sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 10 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [8, 14] x `ma_len` [34, 55]: **4 trials**.

## Ambiguities resolved

- Long on the average at or below zero, as written; trail without offset dropped. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
