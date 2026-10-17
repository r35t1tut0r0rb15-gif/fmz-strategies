# #431284 Dual SSL Strategy with EMA Stop Loss -> `fmz_431284_ssl_ema200_stop`

- FMZ source id: 431284 (lineage).
- Source: https://www.fmz.com/strategy/431284 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 16:52:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop fixed at entry |
| 2 | PASS | SSL channel, an EMA and a profit test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity / close stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `ema_len` [200, 100]: **4 trials**.

## Ambiguities resolved

- openprofit > 0.1 read as in profit; the stop at the signal bar's SSL line. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`coarse_bar_stop`
