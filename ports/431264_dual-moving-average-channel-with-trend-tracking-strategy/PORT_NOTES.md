# #431264 Dual Moving Average Channel with Trend Tracking Strategy -> `fmz_431264_sma_dmi_long`

- FMZ source id: 431264 (lineage).
- Source: https://www.fmz.com/strategy/431264 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 15:41:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMAs and DMI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [14, 30] x `key_level` [20, 25]: **4 trials**; SMA 7 and DMI 14 / 14 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
