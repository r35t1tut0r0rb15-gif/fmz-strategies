"""Noro's MA + ATR trend state, 1-hour bars: a low above the SMA 30 of ohlc4 plus twice the 30-bar average true range holds a long, a high under the SMA minus it holds a short; reversing.
Port of FMZ strategy #438456 "Trend Tracking Strategy Based on Moving Average and Average True Range" (MA+ATR str).

FMZ source id: 438456

Source
    https://www.fmz.com/strategy/438456 (PineScript v4, FMZ last modified 2024-01-12 11:14:01).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 167-199), MA 30 on ohlc4; ATR = sma(tr, 30) x 2; limit mode off; long and short on; capital 100 %
    atr = sma(tr, 30) x 2;  ma = sma(ohlc4, 30);  trend = 1 if low > ma + atr, -1 if high < ma - atr, else trend[1];  trend 1 -> entry Long, trend -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; trend 0 sends nothing. The
      limit-mode branches are the same orders. strategy.entry reverses: REVERSAL INTENDED. The equity lot
      and capital input are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA band of average true range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity lot, capital input and percent-of-equity size stored.
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

NAME = "fmz_438456_noro_ma_atr_band_state"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [30, 60],
    "mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"len": 30, "mult": 2.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[:1] = np.nan                                 # tr is na on the first bar
    atr = tr.rolling(n).mean() * float(p["mult"])
    ma = ((o + h + lo + c) / 4).rolling(n).mean()
    t_up = (lo > ma + atr).to_numpy()
    t_dn = (h < ma - atr).to_numpy()
    m = len(c)
    st = np.zeros(m)
    for i in range(m):
        prev = st[i - 1] if i > 0 else 0.0
        st[i] = 1.0 if t_up[i] else (-1.0 if t_dn[i] else prev)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(st == 1, index=ix), false, pd.Series(st == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
