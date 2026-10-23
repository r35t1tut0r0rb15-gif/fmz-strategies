"""A close-based Renko direction (bricks of the current ATR 14) with Bollinger Bands 14 / 2 of the close, hourly bars: a close above the upper band in an up direction goes long, a close below the lower band in a down direction goes short; reversing.
Port of FMZ strategy #426569 "Weis Wave Bollinger Band Trading Strategy" (Weis BB Strategy).

FMZ source id: 426569

Source
    https://www.fmz.com/strategy/426569 (PineScript v4, FMZ last modified 2023-09-13 13:55:24).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 116-178), Renko ATR 14 on the close; BB 14, 2 sd; exit profit 20 / loss 10 ticks (placed only on the short signal bar); strategy() commented out
    currclose := hi > prevclose + atr ? hi : lo < prevclose - atr ? lo : prevclose (hi = lo = close);  direction = sign of the change of currclose (kept when unchanged)
    close > upper and direction > 0 -> entry Buy;  close < lower and direction < 0 -> entry Sell, then exit("exit", "Buy", when = directionIsDown, profit = 20, loss = 10) and exit("exit", "Sell", when = directionIsUp, ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Weis wave volume only feeds the plot, so volume does not reach the orders: ported as not using
      volume (check 8). The two exits sit inside the short-entry block: the Buy exit is sent on the bar
      whose Sell entry reverses that Buy at the next open, and the Sell exit needs an up direction on a
      bar that requires a down one, so neither ever acts (their 20 / 10-tick distances are not ported).
      The Renko line starts from nz(currclose[1]) = 0 and ATR is Pine's atr (Wilder). REVERSAL INTENDED.
      strategy() and the max intraday loss are commented out. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts confirmed by a Renko direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (10 % of equity) stored, not ported.
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

NAME = "fmz_426569_renko_atr14_direction_bb14_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "methodvalue": [14, 28],
}
DEFAULT_PARAMS = {"length": 14, "methodvalue": 14, "mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    atr = _rma(tr, int(round(float(p["methodvalue"])))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    direc = np.zeros(m)
    cur_p, d_p = 0.0, 0.0
    for i in range(m):
        prev = cur_p                                     # nz(currclose[1])
        if cv[i] > prev + atr[i]:
            cur = cv[i]
        elif cv[i] < prev - atr[i]:
            cur = cv[i]
        else:
            cur = prev
        d = 1.0 if cur > prev else (-1.0 if cur < prev else d_p)
        direc[i] = d
        cur_p, d_p = cur, d
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up = pd.Series(direc > 0, index=c.index)
    dn = pd.Series(direc < 0, index=c.index)
    le = (c > basis + dev) & up
    se = (c < basis - dev) & dn
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
