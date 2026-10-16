"""Center-of-gravity bands with an ATR stop, 4-hour bars: the close above the regression line + 6 % holds a
long, below the line - 6 % holds a short; each entry has a stop 2 true ranges from the signal bar's close.
Port of FMZ strategy #429390 "动态ATR止损中心线策略Dynamic-ATR-Stop-Loss-Center-Line-Strategy" (Center of Gravity BF).

FMZ source id: 429390

Source
    https://www.fmz.com/strategy/429390 (PineScript v4, FMZ last modified 2023-10-16 16:20:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 137-197), linreg 25 offset 5, band 6 %, ATR stop period 1 x 2
    xLG = linreg(close, 25, 5); pos = close > xLG + 6 % close ? 1 : close < xLG - 6 % close ? -1 : pos[1]
    pos == 1 -> entry long; pos == -1 -> entry short
    longStop = close - 2 x atr(1) on the bar the long phase starts (kept), exit(stop = longStop) from the next bar on

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(close, 25, 5) is the least-squares line through the last 25 closes read 5 bars back from
      the current bar: intercept + slope x (25 - 1 - 5).
    * The stop is fixed at entry: sl_stop = 2 x the signal bar's true range as a fraction of its close
      (shifted one bar inside stops(), re-based on the fill). Stated approximations: the source arms it
      from the bar after the fill (vbt from the fill bar), and a re-entry within the same phase after a
      stop-out keeps the phase's first level in the source, the signal bar's own level here.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry (approximations stated).
    2 generic: PASS, percentage bands and a true-range multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and commission stored; the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427304 (3 members, best partner #427304, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429390_cog_bands_atr_stop"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "percent": [6.0, 3.0],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 25, "offset": 5, "percent": 6.0, "atr_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(x, n, offset):
    xs = np.arange(n, dtype=float)
    sx, sxx = xs.sum(), (xs * xs).sum()

    def f(y):
        slope = (n * (xs * y).sum() - sx * y.sum()) / (n * sxx - sx * sx)
        icpt = (y.sum() - slope * sx) / n
        return icpt + slope * (n - 1 - offset)
    return x.rolling(n).apply(f, raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    lg = _linreg(c, int(p["length"]), int(p["offset"]))
    band = c * p["percent"] / 100
    upc, dnc = (c > lg + band).to_numpy(), (c < lg - band).to_numpy()
    m = len(c)
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if upc[i]:
            q = 1
        elif dnc[i]:
            q = -1
        pos[i] = q
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(pos == 1, index=idx), false, pd.Series(pos == -1, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return {"sl_stop": (p["atr_mult"] * tr / c).shift(1)}


def portfolio_kwargs(**params):
    return {}
