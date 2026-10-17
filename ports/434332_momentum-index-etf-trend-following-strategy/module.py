"""SMA 50 / 150 trend with a slope test, 1-hour bars, long only: from flat, an SMA 50 crossing above the SMA 150 with the
SMA 50's slope angle above 5 degrees, or a close above the SMA 50 with the SMA 50 above the SMA 150 and the same slope,
goes long; an SMA 50 crossing below the SMA 150, or its slope angle under -5 degrees, closes the long.
Port of FMZ strategy #434332 "Momentum Index ETF Trend Following Strategy" (50-150 INDEX TREND FOLLOWING).

FMZ source id: 434332

Source
    https://www.fmz.com/strategy/434332 (PineScript v4, FMZ last modified 2023-12-05 15:13:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 123-159), SMA 50 / 150; slope angles +5 / -5 degrees on ATR 14; risk 100 %
    angle = 180 / 3.14159265359 x atan((sma50 - sma50[1]) / atr(14))
    long = (crossover(sma50, sma150) and angle > 5) or (close > sma50 and sma50 > sma150 and angle > 5);  flat -> order long
    exit = crossunder(sma50, sma150) or angle < -5;  long -> order short (position size)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry needs a flat position and the exit a long one, at the bar's calculation: a small
      state machine, so the entry and the exit never share a bar. The author's pi constant is kept.
      The comment asks for daily index charts; the backtest header says 1h, which is used: FREQ =
      "1h". The unit count (risk % of equity over the close) is sizing. Long only.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses and an ATR-normalised slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-percent unit count and the initial capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434332_sma_50_150_slope_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 25],
    "slope_deg": [5, 10],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 150, "slope_deg": 5, "atr_len": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    ang = (180 / 3.14159265359) * np.arctan((f - f.shift(1)) / atr)
    th = float(p["slope_deg"])
    xu = (f > s) & (f.shift(1) <= s.shift(1))
    xd = (f < s) & (f.shift(1) >= s.shift(1))
    lc = ((xu & (ang > th)) | ((c > f) & (f > s) & (ang > th))).to_numpy()
    ex = (xd | (ang < -th)).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0  # position held on bar i
    for i in range(m):
        if pos == 0 and lc[i]:
            le[i] = True
            pos = 1
        elif pos == 1 and ex[i]:
            lx[i] = True
            pos = 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
