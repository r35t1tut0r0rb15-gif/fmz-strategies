# #428887 Trend Following Strategy Based on Volume Flow Indicator -> `fmz_428887_volume_flow_indicator_cross_ema50_200_filter_long`

- FMZ source id: 428887 (lineage).
- Source: https://www.fmz.com/strategy/428887 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-10 14:51:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits |
| 2 | PASS | Volume flow indicator crossings with an EMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed quantity, pyramiding 2, capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vfi_length` [8, 130] x `buy_line` [-4.0, 0.0]: **4 trials**; sell line 5, stop 5 %.

## Ambiguities resolved

- Exits only on the VFI crossing, as written. Volume = broker tick volume. Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
