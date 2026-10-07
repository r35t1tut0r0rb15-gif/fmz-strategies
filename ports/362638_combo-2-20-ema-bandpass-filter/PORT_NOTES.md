# #362638 Combo 2/20 EMA & Bandpass Filter -> `fmz_362638_combo_ema20_bandpass`

- Source: https://www.fmz.com/strategy/362638 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 16:09:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Zones +-5 (price units) -> +-`zone_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 14, 20] x `zone_atr` [0.1, 0.5, 1.0] = **9 trials**. `length_bpf` 20 and `delta` 0.5 stay at the originals; ATR length 14 is fixed.

## Ambiguities resolved

- SellZone/BuyZone (+-5, price units) -> +-`zone_atr` x ATR(14) (criterion 2).
- The 2005 start-date filter is a backtest window and is dropped; "Trade reverse" (default false) is not ported.
- `close_all` when the two positions disagree -> both exit Series.
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`bar_size_pending`
