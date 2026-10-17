"""EMA 50 / 200 golden and death crosses with a 1 % / 2 % bracket, 2-hour bars: EMA 50 crossing above EMA 200 goes
long, crossing below goes short; each trade has a 1 % stop and a 2 % target.
Port of FMZ strategy #489154 "多重均线交叉动量风险比优化策略-Multi-EMA-Crossover-Momentum-Strategy-with-Risk-Reward-Optimization" (Golden Cross & Death Cross Strategy with SL & TP).

FMZ source id: 489154

Source
    https://www.fmz.com/strategy/489154 (PineScript v5, FMZ last modified 2025-04-02 11:19:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 190-216), EMA 50 / 200, SL 1 %, RR 2
    golden = crossover(ema50, ema200) -> entry long + exit(stop = close x 0.99, limit = close x 1.02)
    death = crossunder(ema50, ema200) -> entry short + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop 1 %, tp_stop 2 % of the fill (scalars, house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489154_golden_death_cross_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "rr": [2.0, 4.0],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "sl_pct": 1.0, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((ef > es) & (ef.shift(1) <= es.shift(1))).astype(bool)
    dn = ((ef < es) & (ef.shift(1) >= es.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["sl_pct"] * p["rr"] / 100}


def portfolio_kwargs(**params):
    return {}
