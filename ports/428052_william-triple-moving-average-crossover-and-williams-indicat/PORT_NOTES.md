# #428052 Triple Moving Average Crossover and Williams Indicator Strategy -> `fmz_428052_three_smma_fractal_rsi`

- FMZ source id: 428052 (lineage).
- Source: https://www.fmz.com/strategy/428052 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-28 10:58:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fractals confirmed n bars after the pivot; bracket fixed at entry. |
| 2 | PASS | MA lengths, RSI level, percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [2, 3] x `stop_loss` [0.1, 0.5] x `target_profit` [0.4, 1]: **8 trials**; defaults 2 / 0.1 / 0.4 (the source's); SMMAs 21 / 50 / 200 and RSI 14 fixed.

## Ambiguities resolved

- SMMA = rma seeded by the SMA. Fractal loop generalised for n (the source's offsets for n = 2).
- "Flat" follows the house bracket (loop marks the exit when a bar reaches the stop / target from the fill).
- Stop module: `portfolio_kwargs` `{}`; entries only from flat. Stops on 3-hour bars: mark `coarse_bar_stop`. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
