# #442621 Reversal Momentum Breakout Strategy -> `fmz_442621_new_closing_high_decay_long`

- FMZ source id: 442621 (lineage).
- Source: https://www.fmz.com/strategy/442621 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:11:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | New-high momentum with a decay count |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [20, 50] x `decay` [5, 10]: **4 trials**.

## Ambiguities resolved

- A repeat new high restarts the count. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
