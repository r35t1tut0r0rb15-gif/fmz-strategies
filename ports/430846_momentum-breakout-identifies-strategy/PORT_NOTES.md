# #430846 Momentum Breakout Identifies Strategy -> `fmz_430846_capitulation_bar_long`

- FMZ source id: 430846 (lineage).
- Source: https://www.fmz.com/strategy/430846 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:39:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported; the moving target fixed at the fill (rule 2). |
| 2 | PASS | Body and distance ratios, an RSI level and a percentage target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50 % of equity per entry and pyramiding 1000 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [20.0, 10.0] x `body_mult` [2.5, 2.0]: **4 trials**; RSI 3 / 10, SMA 20 / 100 and distance 2 fixed.

## Ambiguities resolved

- Pending (not emitted as written): adds, and the target moved by later signals; fixed at 20 % of the fill here.
- Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_spike_reversal"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
