# #434326 Low Frequency Fourier Transform Trend Following Moving Average Strategy -> `fmz_434326_fourier_shifted_ema`

- FMZ source id: 434326 (lineage).
- Source: https://www.fmz.com/strategy/434326 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 14:56:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed price with harmonic shifts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434326. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_fourier` [64, 32] x `slow` [200, 100]: **4 trials**; mid 20, fast 5 and the harmonics 1 / 2 / 3 fixed.

## Ambiguities resolved

- Harmonic amplitudes at i = 0 (cosine part only); pi exact; unarmed exits dropped. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
