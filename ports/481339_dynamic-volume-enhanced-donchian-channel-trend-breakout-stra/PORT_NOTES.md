# #481339 Dynamic Volume Enhanced Donchian Channel Trend Breakout Strategy -> `fmz_481339_donchian20_breakout_volume_3h_reversal`

- FMZ source id: 481339 (lineage).
- Source: https://www.fmz.com/strategy/481339 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:18:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian breakouts on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 55] x `vol_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- The channel exits can never fire. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
