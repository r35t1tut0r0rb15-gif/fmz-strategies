# #452280 EMA SMA Crossover Bull Market Support Band Strategy -> `fmz_452280_ema21_sma20_confirmed_cross_reversal`

- FMZ source id: 452280 (lineage).
- Source: https://www.fmz.com/strategy/452280 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-23 18:11:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Confirmed MA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital setting stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [20, 50] x `ema_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- Unconfirmed crosses only close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
