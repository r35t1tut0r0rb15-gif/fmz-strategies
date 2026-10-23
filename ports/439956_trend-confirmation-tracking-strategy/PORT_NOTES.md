# #439956 Trend Confirmation Tracking Strategy -> `fmz_439956_supertrend_state_inverted_macd_vwap_1h_reversal`

- FMZ source id: 439956 (lineage).
- Source: https://www.fmz.com/strategy/439956 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 11:57:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend state with MACD and VWAP confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 20]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- Supertrend direction as written (> 0 = down state). Session VWAP at the broker day. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
