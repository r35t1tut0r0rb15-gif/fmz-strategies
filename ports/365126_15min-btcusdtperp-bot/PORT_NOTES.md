# #365126 15MIN BTCUSDTPERP BOT -> `fmz_365126_twelve_filter_confluence_cvd_vwma_state_pct_bracket_reversal`

- FMZ source id: 365126 (lineage).
- Source: https://www.fmz.com/strategy/365126 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-06-20 10:25:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Multi-indicator trend confluence with a self-re-arming state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rvol_trigger` [1.5, 1.0] x `th` [12.0, 20.0]: **4 trials**; TP 0.8 %, SL 3.6 %, the other settings as written.

## Ambiguities resolved

- The script's own re-arming state is kept; 0 / 0 power bars add nothing to the CVD. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
