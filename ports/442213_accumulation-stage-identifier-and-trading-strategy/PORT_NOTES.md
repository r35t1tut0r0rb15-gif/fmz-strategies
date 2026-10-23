# #442213 Accumulation Stage Identifier and Trading Strategy -> `fmz_442213_sma_stack_pvt_macd_accumulation_reversal`

- FMZ source id: 442213 (lineage).
- Source: https://www.fmz.com/strategy/442213 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 11:29:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend stack with a PVT MACD confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50]: **4 trials**; MACD signal 9, SMA 200 / 50 / 90.

## Ambiguities resolved

- Later call wins on a two-sided bar. Volume = broker tick volume (PVT). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
