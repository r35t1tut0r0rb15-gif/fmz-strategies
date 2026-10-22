# #468338 Dual Moving Average Channel Trend Following Strategy -> `fmz_468338_vegas_sma55_cross_ema576_sma300_ref_close_tests_reversal`

- FMZ source id: 468338 (lineage).
- Source: https://www.fmz.com/strategy/468338 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:28:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop and target are close tests against the fill |
| 2 | PASS | MA crossings with reference-close exits; armed trails described (pending) |
| 3 | PASS | Exchange pair in the header only (BTC named in the title). |
| 4 | DONE | The fixed 1-unit quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [55, 34] x `long_len` [300, 200] x `ema_len` [576, 288]: **8 trials**; the offsets and the 70 / 140 divisors fixed; the armed trails pending.

## Ambiguities resolved

- Offsets as fractions of 42000; armed trailing exits pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
