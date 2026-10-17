# #431502 Donchian Channel Breakout Trading Strategy -> `fmz_431502_body_channel_one_bar`

- FMZ source id: 431502 (lineage).
- Source: https://www.fmz.com/strategy/431502 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-08 12:31:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close_all every bar as written |
| 2 | PASS | A channel on bodies and its percentage lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`history` [20, 40] x `pct_dev` [13, 25]: **4 trials**.

## Ambiguities resolved

- One-bar holds (close_all every bar) as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_reversal"`.

## Marks

`none`
