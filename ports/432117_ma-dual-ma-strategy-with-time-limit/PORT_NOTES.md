# #432117 双MA时间限制交易策略Dual-MA-Strategy-with-Time-Limit -> `fmz_432117_open_ema_flip_tick_bracket`

- FMZ source id: 432117 (lineage).
- Source: https://www.fmz.com/strategy/432117 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-14 16:45:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits are ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.1, 1.0] x `tp_atr` [0.5, 3.0]: **4 trials**; EMA 14 / 21 of the open and ATR 14 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the 200-point trail without an offset. Tick bracket as ATR fractions. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
