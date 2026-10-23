# #442212 基于OBVCMO和Coppock曲线的交易策略OBV-CMO-and-Coppock-Curve-Based-Trading-Strategy -> `fmz_442212_obv_coppock_cmo_agreement_long_only`

- FMZ source id: 442212 (lineage).
- Source: https://www.fmz.com/strategy/442212 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 11:26:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | OBV, Coppock curve and CMO agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cmo_buy` [50, 30] x `cmo_period` [14, 9]: **4 trials**; Coppock 14 / 11 / 10, sell -50.

## Ambiguities resolved

- OBV direction only. Volume = broker tick volume (OBV). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
