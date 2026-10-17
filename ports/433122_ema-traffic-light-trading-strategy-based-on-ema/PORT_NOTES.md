# #433122 基于EMA均线的交易策略Traffic-Light-Trading-Strategy-Based-on-EMA -> `fmz_433122_traffic_light_emas`

- FMZ source id: 433122 (lineage).
- Source: https://www.fmz.com/strategy/433122 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 15:46:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily filter from completed broker days; bracket fixed at entry |
| 2 | PASS | EMA order and percent / ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 20 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `filter_len` [100, 50]: **4 trials**; EMA 8 / 14 / 16, TP 40 % / 30 % and ATR 14 fixed.

## Ambiguities resolved

- Ratchet on bar lows minus 2 ATR not expressible (trailing_stop_pending); the first level is fixed at entry. Side-dependent target via the fill bar. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
