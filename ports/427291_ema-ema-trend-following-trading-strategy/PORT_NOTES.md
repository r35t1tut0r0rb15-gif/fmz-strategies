# #427291 EMA Trend Following Trading Strategy -> `fmz_427291_ema_12_26_long`

- FMZ source id: 427291 (lineage).
- Source: https://www.fmz.com/strategy/427291 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 19:38:53). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | BTC-quoted pair in the header only. |
| 4 | DONE | Initial capital / currency stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50, 100]: **6 trials**; defaults 12 / 26 (the source's).

## Ambiguities resolved

- `inTradeWindow = true`: no date window; the window exit never fires.
- Long only; the up-cross and down-cross cannot fall on one bar. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
