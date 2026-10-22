# #442637 RSI均线双金叉震荡策略RSI-Moving-Average-Double-Cross-Oscillation-Strategy -> `fmz_442637_rsi_band_extreme_long_resent_bracket`

- FMZ source id: 442637 (lineage).
- Source: https://www.fmz.com/strategy/442637 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:07:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | RSI against its own bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `bb_length` [14, 30]: **4 trials**; the levels fixed.

## Ambiguities resolved

- The re-sent bracket pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
