# #436906 Relative Volume Price Strategy -> `fmz_436906_relative_volume_normal_atr_trailing_low_long`

- FMZ source id: 436906 (lineage).
- Source: https://www.fmz.com/strategy/436906 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 17:54:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR trailing line in the signals |
| 2 | PASS | Relative-volume spikes in a normal volatility regime |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [1.5, 2.0] x `tsl_mult` [2.0, 3.0]: **4 trials**; ATR 14, volume SMA 20.

## Ambiguities resolved

- Close-and-re-signal bar ported as the close only. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_filter"`.

## Marks

`none`
