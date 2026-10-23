# #431218 Dual Laser Trend seeking Strategy -> `fmz_431218_squeeze_momentum_volume_rsi_sar_alternating_reversal`

- FMZ source id: 431218 (lineage).
- Source: https://www.fmz.com/strategy/431218 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 10:01:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Squeeze momentum with volume RSI and SAR agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [85, 20] x `kc_length` [38, 20]: **4 trials**; SAR 0.73 / 0.5 / 0.06, RSI 22 / 45.

## Ambiguities resolved

- First set after the opposite one, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "squeeze_momentum"`.

## Marks

`none`
