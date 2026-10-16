# #429509 Algorithm-RSI区间突破策略Algorithm-RSI-Range-Breakout-Strategy -> `fmz_429509_rsi_zone_bracket`

- FMZ source id: 429509 (lineage).
- Source: https://www.fmz.com/strategy/429509 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 17:14:09). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | Tick distances -> ATR multiples. |
| 3 | PASS | "BTC/USD" in the title only; exchange pair in the header. |
| 4 | DONE | The lot input stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [1.7, 3.0] x `sl_atr` [3.3, 1.5]: **4 trials**; RSI 14 and the zone levels fixed.

## Ambiguities resolved

- Unreachable nested entries noted. Flat tracked through the bracket. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
