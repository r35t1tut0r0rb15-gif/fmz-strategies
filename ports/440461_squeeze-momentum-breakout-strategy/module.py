"""Hourly bars, long only: the first bar after a squeeze (Bollinger 21 inside Keltner 20 x 1.5) is released with the squeeze momentum line above zero goes long; a bar whose momentum is neither rising above zero nor falling below zero closes it.
Port of FMZ strategy #440461 "Squeeze Momentum Breakout Strategy" (SQZMOM STRAT (LazyBear squeeze momentum)).

FMZ source id: 440461

Source
    https://www.fmz.com/strategy/440461 (PineScript v4, FMZ last modified 2024-01-30 17:33:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-264), BB length 21 (deviation x 1.5, the KC factor), KC 20 x 1.5 true range; trade type LONG; VWMA filter off; leverage 1, risk 100 %
    sqzOn = lowerBB > lowerKC and upperBB < upperKC;  val = linreg(close - avg(avg(highest(high, 20), lowest(low, 20)), sma(close, 20)), 20, 0)
    val > 0 and noSqz == 0 and sqzOn == 0 and sqzOn[1] == 1 -> entry LONG (qty = equity x leverage / close x risk);  bcolor gray -> close LONG / SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger deviation uses the KC factor 1.5 instead of the BB factor 2 (weird case). bcolor is
      green when val > 0 and val > nz(val[1]), red when val < 0 and val < nz(val[1]), else gray: a gray bar
      closes the long. The EVWMA filter is off (useVWMA false), so volume feeds nothing (held for volume,
      not used). Pine's stdev is the population deviation. The contracts formula is sizing. Long only.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, squeeze release with positive momentum, closed when momentum fades.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x leverage / close x risk %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440461_squeeze_release_momentum_fade_exit_1h_long_only"
FAMILY = "squeeze_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [21, 20],
    "kc_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"bb_len": 21, "kc_len": 20, "kc_mult": 1.5}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    bl, kl, km = int(p["bb_len"]), int(p["kc_len"]), float(p["kc_mult"])
    basis = c.rolling(bl).mean()
    dev = km * c.rolling(bl).std(ddof=0)
    up_bb, lo_bb = basis + dev, basis - dev
    ma = c.rolling(kl).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    rng = tr.rolling(kl).mean()
    up_kc, lo_kc = ma + rng * km, ma - rng * km
    sqz_on = ((lo_bb > lo_kc) & (up_bb < up_kc)).to_numpy()
    sqz_off = ((lo_bb < lo_kc) & (up_bb > up_kc)).to_numpy()
    no_sqz = ~sqz_on & ~sqz_off
    mid = ((h.rolling(kl).max() + lo.rolling(kl).min()) / 2 + c.rolling(kl).mean()) / 2
    val = _linreg(c - mid, kl)
    pv = val.shift(1).fillna(0.0)
    green = ((val > 0) & (val > pv)).to_numpy()
    red = ((val < 0) & (val < pv)).to_numpy()
    gray = ~green & ~red
    vv = val.to_numpy()
    prev_on = np.concatenate(([False], sqz_on[:-1]))
    entry = (vv > 0) & ~no_sqz & ~sqz_on & prev_on
    m = len(vv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and gray[i]:
            lx[i], pos = True, 0
        elif pos == 0 and entry[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
