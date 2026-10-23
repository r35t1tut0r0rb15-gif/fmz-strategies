# #468337 Multi Indicator Adaptive Momentum Trading Strategy -> `fmz_468337_macd_hist_vwma20_50_state_cross_exit_reversal`

- FMZ source id: 468337 (lineage).
- Source: https://www.fmz.com/strategy/468337 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:25:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram states filtered by VWMA 20 / 50 with MACD crossing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x leverage / close stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vw_fast` [20, 10] x `vw_slow` [50, 100]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- Entries are states; crossing exits. Volume = broker tick volume (VWMAs). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
