"""HPotter's money-flow state (EMA 10 of the 10-bar sum against EMA 3 of the 3-bar sum of (close - open) / range x volume), 3-hour bars: a positive difference goes long, a negative one goes short (held on zero); reversing.
Port of FMZ strategy #429077 "Chaikin Oscillator Strategy" (Money Flow Indicator (Chaikin Oscillator)).

FMZ source id: 429077

Source
    https://www.fmz.com/strategy/429077 (PineScript v2, FMZ last modified 2023-10-12 16:41:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-200), fast 3, slow 10; reverse off
    flow = (high - low) x volume > 0 ? (close - open) / (high - low) x volume : 0;  nRes = ema(sum(flow, 10), 10) - ema(sum(flow, 3), 3)
    pos = nRes > 0 ? 1 : nRes < 0 ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is EMA(sum over 10) minus EMA(sum over 3), the slow minus the fast as written (the money
      flow half of #427091 on its own). REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, money-flow oscillator sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the money flow (close - open) / range x volume; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429077_chaikin_style_money_flow_sum_ema_state_reversal"
FAMILY = "money_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [10, 20],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 10}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    fast, slow = int(p["fast"]), int(p["slow"])
    lmax, lmin = max(fast, slow), min(fast, slow)
    rng = h - lo
    flow = ((c - o) / rng.where(rng != 0) * v).where(rng * v > 0, 0.0)
    nres = (flow.rolling(lmax).sum().ewm(span=lmax, adjust=False).mean()
            - flow.rolling(lmin).sum().ewm(span=lmin, adjust=False).mean()).to_numpy()
    pos = np.zeros(len(nres), dtype=np.int8)
    q = 0
    for i in range(len(nres)):
        if nres[i] > 0:
            q = 1
        elif nres[i] < 0:
            q = -1
        pos[i] = q
    prev = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prev != 1), index=ix), false,
            pd.Series((pos == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
