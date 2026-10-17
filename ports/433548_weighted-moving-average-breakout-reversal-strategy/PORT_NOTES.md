# #433548 Weighted Moving Average Breakout Reversal Strategy -> `fmz_433548_wma_pierce_fade_trail`

- FMZ source id: 433548 (lineage).
- Source: https://www.fmz.com/strategy/433548 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 14:11:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house trail (approximation stated) |
| 2 | ADAPT | Tick distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The per-contract commission and quantity 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["America/New_York", "UTC"] x `trail_k` [0.25, 1.0]: **4 trials**; WMA 20, ATR 14 and target = trail_k / 2 fixed.

## Ambiguities resolved

- Tick trail as an ATR volatility trail (approximation stated), session in New York or UTC. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks

`trailing_stop`
