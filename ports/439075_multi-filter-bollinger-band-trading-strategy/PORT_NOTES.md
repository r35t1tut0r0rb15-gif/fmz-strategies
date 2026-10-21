# #439075 Multi filter Bollinger Band Trading Strategy -> `fmz_439075_noro_bollinger_dip_long`

- FMZ source id: 439075 (lineage).
- Source: https://www.fmz.com/strategy/439075 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-17 15:12:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands, bar colour, body and a fast RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [1.0, 2.0]: **4 trials**; filters on; RSI 7 at 30 / 70 fixed.

## Ambiguities resolved

- Zero-quantity short closes the long; adds blocked. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
