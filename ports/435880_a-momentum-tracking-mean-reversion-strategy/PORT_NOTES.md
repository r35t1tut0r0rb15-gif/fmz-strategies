# #435880 A Momentum Tracking Mean Reversion Strategy -> `fmz_435880_apex_rsi2_stoch12_oversold_ema_cross_exit_long`

- FMZ source id: 435880 (lineage).
- Source: https://www.fmz.com/strategy/435880 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 14:42:26). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target and stop in the signals |
| 2 | PASS | Short-RSI and stochastic oversold entries with an EMA-cross exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_oversold` [12, 20] x `stoch_oversold` [10, 20]: **4 trials**; RSI 2, stochastic 12, EMA 10 / 20, TP 1 %, SL 2 %.

## Ambiguities resolved

- bbBuy gated by the STOCHRSI switch (always true); bar-close TP / SL anchored at the signal close. Volume not used. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_agreement"`.

## Marks

`none`
