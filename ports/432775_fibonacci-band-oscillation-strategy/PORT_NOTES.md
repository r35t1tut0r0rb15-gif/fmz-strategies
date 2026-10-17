# #432775 Fibonacci Band Oscillation Strategy -> `fmz_432775_fibonacci_atr_band_breakout`

- FMZ source id: 432775 (lineage).
- Source: https://www.fmz.com/strategy/432775 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 13:47:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ATR bands and percentage exits of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_ratio` [1.618, 1.0] x `sl_pct` [4.0, 2.0]: **4 trials**; EMA / ATR 14, the short band (1 ATR) and TP 1.5 % fixed.

## Ambiguities resolved

- The FIBOTOP1 option reads FIBOTOP2, as written. Entries from flat, the bracket followed on bars. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop`
