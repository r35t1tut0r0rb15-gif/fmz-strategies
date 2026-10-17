# #431889 RSI回调突破策略RSI-Pullback-Breakout-Strategy -> `fmz_431889_rsi5_jump_long`

- FMZ source id: 431889 (lineage).
- Source: https://www.fmz.com/strategy/431889 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-13 10:15:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG431889. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [5, 10] x `jump_to` [60, 55]: **4 trials**; the 50 starting line fixed.

## Ambiguities resolved

- Long only. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
