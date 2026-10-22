# #458036 SMI与枢轴点结合的动量交叉策略-SMI-and-Pivot-Point-Momentum-Crossover-Strategy -> `fmz_458036_close_range_smi_signal_cross_reversal`

- FMZ source id: 458036 (lineage).
- Source: https://www.fmz.com/strategy/458036 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:03:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum-oscillator signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smi_len` [8, 14] x `smi_k` [6, 3] x `smi_d` [6, 3]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
