"""Generalized SSL channel flips, 3-hour bars: the SSL state turning up (a close at or above the SMA 10 of highs after being below the channel) goes long, turning down goes short; reversing; every position
has a stop and a tight trailing stop in tick distances, re-expressed as ATR multiples.
Port of FMZ strategy #438782 "Trend Following Channel Breakout Strategy with Moving Average and Trailing Stop" (GSSL Backtest).

FMZ source id: 438782

Source
    https://www.fmz.com/strategy/438782 (PineScript v3, FMZ last modified 2024-01-15 12:25:26).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 132-205), Lb 10, MA type SMA; loss 300 ticks, trail points 150, trail offset 1 (ticks); dates true
    maH = sma(high, 10), maL = sma(low, 10);  bbb = in channel ? bbb[1] : below ? -1 : 1;  up = bbb 1 ? maL : maH, dn = bbb 1 ? maH : maL;  long = crossover(dn, up);  short = crossover(up, dn)
    entry Long / Short;  exit(Exit, all entries, loss = 300, trail_points = 150, trail_offset = 1);  exit(Exit, when = signal) with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick distances are re-expressed with the ATR(14) of the module's bars: sl_stop =
      k_sl x ATR / close of the signal bar (shifted one bar inside stops(), re-based on the fill) and the
      house volatility trail k_trail x ATR behind the best price, active after a gain of activate (a
      fraction of the fill); 0.086 / 0.0003 / 0.00036 are the reading (30, 0.1 and 15 on BTC with 0.1
      ticks, against a 3-hour ATR near 350 and a price near 42000), 1.0 / 0.5 a wider pair (anchor
      high_low; mark trailing_stop). The level-free exit calls place nothing. startTimeOk() is true.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header (bars on UTC
      multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; house trail.
    2 generic: ADAPT, tick stop and trail -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438782_gssl_channel_flip_atr_trail"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.086, 1.0],
    "k_trail": [0.0003, 0.5],
}
DEFAULT_PARAMS = {"k_sl": 0.086, "k_trail": 0.0003, "activate": 0.00036, "lb": 10, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lb"])
    mah = h.rolling(n).mean().to_numpy()
    mal = lo.rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    b = np.nan
    for i in range(m):
        inside = cv[i] < mah[i] and cv[i] > mal[i]
        below = cv[i] < mah[i] and cv[i] < mal[i]
        b = b if inside else (-1.0 if below else 1.0)
        up[i] = mal[i] if b == 1 else mah[i]
        dn[i] = mah[i] if b == 1 else mal[i]
    us, ds = pd.Series(up, index=c.index), pd.Series(dn, index=c.index)
    lc = (ds > us) & (ds.shift(1) <= us.shift(1))
    sc = (us > ds) & (us.shift(1) <= ds.shift(1))
    false = pd.Series(False, index=c.index)
    return lc, false, sc, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["k_trail"]),
                      "anchor": "high_low", "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
