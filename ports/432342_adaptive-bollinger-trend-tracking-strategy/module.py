"""Regression-band re-entries, 1-hour bars: the position of the close in a 40-bar regression line +- 2 standard deviations
marks a support (the previous low when it climbs back above the lower band) and a resistance (the previous high when it
falls back below the upper band); a new support level goes long, a new resistance level goes short; each trade has a
70-tick stop and a 10-tick trail that starts after 50 ticks (house stop and trail).
Port of FMZ strategy #432342 "Adaptive Bollinger Trend Tracking Strategy" (Linear Regression (Backtest / Trailing Stop)).

FMZ source id: 432342

Source
    https://www.fmz.com/strategy/432342 (PineScript v4, FMZ last modified 2023-11-16 16:35:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-266), linreg 40, 2 sd, overbought 1, oversold 0, SL 70 ticks, trail 50 points / offset 10
    bbr = (close - (linreg(close, 40) - 2 sd)) / (4 sd)
    red := bbr[1] > 1 and bbr < 1 ? high[1] : red[1];  green := bbr[1] < 0 and bbr > 0 ? low[1] : green[1]
    crossover(green, green[1]) or crossunder(green, green[1]) -> entry long;  same on red -> entry short
    exit(loss = 70, trail_points = 50, trail_offset = 10) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands use the chart's own resolution (custom timeframe off). crossover(x, x[1]) is
      x > x[1] and x[1] <= x[2], as Pine defines it, so a level step that follows another step on the
      previous bar does not count. The ATR band (top / bott) is plotted only.
    * Criterion 2: on hourly BTC (0.1 tick, ATR about 200 USD) the 70-tick stop is about 0.035 ATR,
      the trail activates after 50 ticks (about 0.00014 of the price) and trails 10 ticks behind the
      best price (about 0.005 ATR). Ported: sl_atr x Wilder ATR(14) of the signal bar (shifted,
      re-based) and the house trail {"type": "volatility", "atr_n": 14, "k": 0.005, "anchor":
      "high_low", "activate_after": 0.00014} (stated approximation, as #429564; mark trailing_stop).
    * On a bar with both signals the short (written later) wins. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick distances -> ATR multiples / a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 10 stored; the exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432342_linreg_band_levels_trail"
FAMILY = "mean_reversion_band"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [40, 20],
    "sl_atr": [0.035, 1.0],
}
DEFAULT_PARAMS = {"length": 40, "mult": 2.0, "overbought": 1.0, "oversold": 0.0, "atr_len": 14, "sl_atr": 0.035,
                  "trail_k": 0.005, "trail_activate": 0.00014}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def _steps(x):
    """crossover(x, x[1]) or crossunder(x, x[1]) with Pine's definition."""
    x1, x2 = x.shift(1), x.shift(2)
    return (((x > x1) & (x1 <= x2)) | ((x < x1) & (x1 >= x2))).to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = _linreg(c, n)
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    bbr = ((c - (basis - dev)) / (2 * dev)).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    ob, osd = float(p["overbought"]), float(p["oversold"])
    m = len(c)
    red, grn = np.zeros(m), np.zeros(m)
    r_, g_ = 0.0, 0.0
    for i in range(m):
        if i >= 1 and bbr[i - 1] > ob and bbr[i] < ob:
            r_ = hv[i - 1]
        if i >= 1 and bbr[i - 1] < osd and bbr[i] > osd:
            g_ = lv[i - 1]
        red[i], grn[i] = r_, g_
    zz = _steps(pd.Series(grn, index=c.index))
    kp = _steps(pd.Series(red, index=c.index))
    le = zz & ~kp
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, kp, false.copy()))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
