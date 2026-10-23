# #482782 Multi Indicator Trend Recognition and Momentum Validation Trading Strategy -> `fmz_482782_ichimoku_cloud_adx_session_vwap_1m_long_only`

- FMZ source id: 482782 (lineage).
- Source: https://www.fmz.com/strategy/482782 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 10:48:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku cloud side with ADX strength and a VWAP filter |
| 3 | PASS | Exchange pair in the header only (TRUMP_USDT). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25.0, 20.0] x `base` [26, 52]: **4 trials**; conversion 9, span B 52.

## Ambiguities resolved

- Spans undisplaced in the logic. Volume = broker tick volume (VWAP). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
