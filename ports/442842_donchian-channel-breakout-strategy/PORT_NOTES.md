# #442842 Donchian Channel Breakout Strategy -> `fmz_442842_close_vs_prior_channel_mid_reversal`

- FMZ source id: 442842 (lineage).
- Source: https://www.fmz.com/strategy/442842 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-26 14:55:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs channel mid-line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427308. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50]: **2 trials**.

## Ambiguities resolved

- The closes repeat the reversals. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
