# #431959 Multi indicator Crossover Strong Trend Tracking Strategy -> `fmz_431959_rsi_mfi_cci_stochrsi_agreement_100_long`

- FMZ source id: 431959 (lineage).
- Source: https://www.fmz.com/strategy/431959 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 16:59:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator agreement entries and exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1000, commission 0.03 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `cci_level` [50, 100]: **4 trials**; RSI exit 49, CCI exit 0.

## Ambiguities resolved

- mf as the formula only (the discarded "if" lines). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_agreement"`.

## Marks

`none`
