# #437403 Signal to Noise Moving Average Trading Strategy Based on Quantitative Trading -> `fmz_437403_signal_to_noise_sma_state`

- FMZ source id: 437403 (lineage).
- Source: https://www.fmz.com/strategy/437403 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-02 12:24:35). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A log-price line against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 42] x `smooth` [7, 14]: **4 trials**; reverse off.

## Ambiguities resolved

- Sum over 1 .. length - 1 divided by length, as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
