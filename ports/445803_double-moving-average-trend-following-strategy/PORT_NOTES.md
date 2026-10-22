# #445803 Double Moving Average Trend Following Strategy -> `fmz_445803_ssl32_flip_reversal`

- FMZ source id: 445803 (lineage).
- Source: https://www.fmz.com/strategy/445803 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 13:56:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SSL channel flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ssl_len` [32, 10]: **2 trials**; the MA type SMA fixed.

## Ambiguities resolved

- Hlv starts na. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`none`
