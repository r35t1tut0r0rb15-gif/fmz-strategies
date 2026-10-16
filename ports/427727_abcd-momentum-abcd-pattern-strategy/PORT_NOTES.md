# #427727 Momentum ABCD Pattern Strategy -> `fmz_427727_abcd_fractal_zigzag`

- FMZ source id: 427727 (lineage).
- Source: https://www.fmz.com/strategy/427727 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-24 13:08:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Fractals confirmed 2 bars after the pivot; the lookahead_on variable is never used. |
| 2 | ADAPT | 100 / 20 USD -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.7, 2] x `sl_atr` [0.15, 1]: **4 trials**; defaults 0.7 / 0.15 (100 / 20 USD on 45-minute BTC, judgement before any backtest); the fractal switch fixed at the source's default.

## Ambiguities resolved

- filterBW false selects isBWFractal (as the source's ternary reads).
- Pine's exits wait until both a long and a short signal have occurred; the port's bracket applies from the first trade (stated approximation).
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "harmonic_pattern"`.

## Marks

`none`
