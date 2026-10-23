# #432909 Kairou Strategy -> `fmz_432909_ichimoku_macd_cmf_tsi_agreement_reversal`

- FMZ source id: 432909 (lineage).
- Source: https://www.fmz.com/strategy/432909 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 16:28:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku trend with MACD, money-flow and TSI agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432909. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ks_bars` [30, 26] x `cmf_level` [0.1, 0.05]: **4 trials**; Tenkan 10, Senkou B 52, MACD 12 / 26 / 9, TSI 20 / 20.

## Ambiguities resolved

- Closes never act (both entry switches on). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
