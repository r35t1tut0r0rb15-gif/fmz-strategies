# #442011 基于ATREOM和VORTEX的长线趋势策略ATR-EOM-and-VORTEX-Based-Long-Trend-Strategy -> `fmz_442011_atr_expansion_eom_vortex_long_only`

- FMZ source id: 442011 (lineage).
- Source: https://www.fmz.com/strategy/442011 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 16:01:07). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility expansion with ease-of-movement and vortex agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 20] x `vortex_len` [10, 20]: **4 trials**; ATR EMA 5, EOM 10.

## Ambiguities resolved

- EOM sign only. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_state"`.

## Marks

`none`
