# #475623 Break of Structure with Volume Confirmation Multi Condition Intelligent Trading Strategy -> `fmz_475623_bos_confirmed_volume_2_15pct_bracket_reversal`

- FMZ source id: 475623 (lineage).
- Source: https://www.fmz.com/strategy/475623 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 16:15:43). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | Confirmed breaks of structure on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.02, 0.05] x `sl` [0.15, 0.05]: **4 trials**; swing 20, volume SMA 10 x 1.1, 2 bars.

## Ambiguities resolved

- Bracket from the signal close (source: from the bar after the fill). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
