# #458067 Magic-Channel-Price-Action-Trading-Strategy-魔法通道价格行为交易策略 -> `fmz_458067_magic_channel_base_cross_displaced_spans_reversal`

- FMZ source id: 458067 (lineage).
- Source: https://www.fmz.com/strategy/458067 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:53:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel mid-line crossings with displaced spans; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [5, 9] x `base` [51, 26] x `displace` [21, 26]: **8 trials**; the span-2 length 68 fixed; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`
