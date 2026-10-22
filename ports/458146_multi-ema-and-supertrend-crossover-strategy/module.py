"""EMA 22 / 79 / 200 trend with three Supertrend lines (ATR 50 / 13 / 6, factor 6), 1-hour bars: the EMA 22 over the EMA 79 with the close over the EMA 200 and all three Supertrend lines goes long, the mirror goes short; reversing.
Port of FMZ strategy #458146 "Multi EMA and Supertrend Crossover Strategy" (Strategia EMA i Supertrend).

FMZ source id: 458146

Source
    https://www.fmz.com/strategy/458146 (PineScript v5, FMZ last modified 2024-07-30 12:14:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 168-225), EMA 22 / 79 / 200 (constants); ta.supertrend(6, 50 / 13 / 6)
    ema79 < ema22 and close > ema200 and close > st50, st13, st6 -> entry Long (and close Short);  the mirror -> entry Short (and close Long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's built-in supertrend. The tests are states: repeated entries while held do nothing, and the
      closes only repeat the reversals (a close finds its position being reversed, #437773). REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend with three Supertrend confirmations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458146_ema22_79_200_triple_supertrend_state_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [6.0, 3.0],
    "ema_short": [22, 10],
}
DEFAULT_PARAMS = {"factor": 6.0, "ema_short": 22, "ema_medium": 79, "ema_long": 200}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    em = c.ewm(span=int(p["ema_medium"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    f = float(p["factor"])
    lines = [pd.Series(_supertrend(h, lo, c, f, n)[1], index=c.index) for n in (50, 13, 6)]
    le = (em < es) & (c > el)
    se = (em > es) & (c < el)
    for s in lines:
        le = le & (c > s)
        se = se & (c < s)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
