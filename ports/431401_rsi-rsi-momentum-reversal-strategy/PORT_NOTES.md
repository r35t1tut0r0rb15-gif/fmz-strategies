# #431401 RSI动量反转策略RSI-Momentum-Reversal-Strategy -> `fmz_431401_connors_fast_rsi`

- FMZ source id: 431401 (lineage).
- Source: https://www.fmz.com/strategy/431401 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-07 15:45:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | RSI composites and bar colour / body filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, the lot formula and pyramiding 10 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [25, 15] x `fast_len` [7, 14]: **4 trials**; CRSI 3 / 2 / 100 and the filters fixed.

## Ambiguities resolved

- Adds not ported (average = first fill); close_all after an entry leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
