"""10-minute bars: a close below each of the 3 previous closes with the low under the Keltner Channel (EMA 20, 2 x EMA 20 of the true range) goes long, a close above each of the 3 previous closes with the high over the upper channel goes short, each side only once until a close moves the other way; reversing.
Port of FMZ strategy #474710 "Multi Factor Counter Trend Trading Strategy" (The Bar Counter Trend Reversal Strategy [TradeDots]).

FMZ source id: 474710

Source
    https://www.fmz.com/strategy/474710 (PineScript v5, FMZ last modified 2024-12-11 17:36:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-160), falls / rises 3; KC 20 x 2 (channel confirm on, volume confirm off); 80 % of equity
    rise_triangle_ready := falling(close, 3) and low < lower;  fall_triangle_ready := rising(close, 3) and high > upper
    close > close[1] -> rise_triangle_plotted := false;  close < close[1] -> fall_triangle_plotted := false
    rise_triangle_ready and not rise_triangle_plotted -> entry Long, plotted := true;  fall mirrored -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default inputs (channel confirm on, volume confirm off) the volume branch is not used
      (held for volume, not used). ta.falling(close, 3) means the close is under each of the 3 previous
      closes (not a falling run). ta.kc(close, 20, 2) uses the EMA of the true range. A side fires again
      only after a close in the opposite direction resets its flag. Entries only; an opposite entry
      reverses. REVERSAL INTENDED. 80 % of equity and the commission are sizing and costs. FREQ = "10min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, counter-trend entries at Keltner Channel extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 80 % of equity, capital and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474710_bar_counter_keltner_reversal_10m"
FAMILY = "keltner_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "count": [3, 5],
    "mult": [2, 3],
}
DEFAULT_PARAMS = {"count": 3, "kc_len": 20, "mult": 2}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kc_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    basis = c.ewm(span=n, adjust=False).mean()
    rng = tr.ewm(span=n, adjust=False).mean() * int(p["mult"])
    k = int(p["count"])
    below = pd.Series(True, index=c.index)
    above = pd.Series(True, index=c.index)
    for i in range(1, k + 1):
        below &= c < c.shift(i)
        above &= c > c.shift(i)
    rise = (below & (lo < basis - rng)).to_numpy()
    fall = (above & (h > basis + rng)).to_numpy()
    up, dn = (c > pc).to_numpy(), (c < pc).to_numpy()
    m = len(rise)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    rp = fp = False
    for i in range(m):
        if up[i]:
            rp = False
        if dn[i]:
            fp = False
        if rise[i] and not rp:
            le[i], rp = True, True
        if fall[i] and not fp:
            se[i], fp = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
