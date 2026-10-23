# #471663 Multi Volume Momentum Combined Trading Strategy -> `fmz_471663_seven_volume_indicator_vote_long_only`

- FMZ source id: 471663 (lineage).
- Source: https://www.fmz.com/strategy/471663 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 10:52:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A vote of seven volume indicators |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`need` [4, 3] x `cmf_len` [20, 40]: **4 trials**; MFI 14, volume SMA 5 / 10, volume RSI 14.

## Ambiguities resolved

- Daily VWAP = the close: that item never counts. Volume = broker tick volume (all seven items). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_vote"`.

## Marks

`none`
