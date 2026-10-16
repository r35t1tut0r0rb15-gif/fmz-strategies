# #427506 Trend Moving Average Trading Strategy -> `fmz_427506_noro_trend_mas_v23`

- FMZ source id: 427506 (lineage).
- Source: https://www.fmz.com/strategy/427506 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 20:34:43). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.
- Near-duplicate group: **ND427506** (4 members, best partner #438058, Jaccard 0.651); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts, ratios of averages. |
| 3 | PASS | The "crypto/fiat only" remark is advice; no exchange feature. |
| 4 | DONE | 100 % of equity and the (off) stop stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427506. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_len` [21, 10, 42] x `need_ex` [True, False]: **6 trials**; defaults 21 / True (the source's); fast 5, bars 2, fast filter on fixed.

## Ambiguities resolved

- Stops off by default; window and its close_all dropped (Noro template).
- Same-bar long and short: the side not held is taken. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
