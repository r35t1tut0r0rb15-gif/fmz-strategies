"""Very slow stochastic of ohlc4, 1-minute bars: the D line (10-bar SMA of a 275-bar SMA of a 400-bar stochastic) crossing over 23 goes long, crossing under 78.5 goes short (reversing); D crossing over 78.5
closes a long, crossing under 23 closes a short.
Port of FMZ strategy #436904 "Slow Stochastic Trend Following Strategy" (Slow Stochastic OB/OS Strategy).

FMZ source id: 436904

Source
    https://www.fmz.com/strategy/436904 (PineScript v4, FMZ last modified 2023-12-28 17:50:36).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 123-154), stochastic 400 of ohlc4, K smoothing 275, D 10, OB 78.5, OS 23
    k = sma(stoch(ohlc4, high, low, 400), 275);  d = sma(k, 10)
    crossover(d, 23) -> entry Long;  crossunder(d, 78.5) -> entry Short;  crossover(d, 78.5) -> close Long;  crossunder(d, 23) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stoch(ohlc4, high, low, n) = 100 (ohlc4 - lowest low) / (highest high - lowest low). Orders follow
      the script's call order (entries, then closes of a position open at the bar's close). REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic levels.
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

NAME = "fmz_436904_slow_stochastic_ob_os"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smooth_k": [400, 200],
    "sma_k": [275, 140],
}
DEFAULT_PARAMS = {"smooth_k": 400, "sma_k": 275, "smooth_d": 10, "ob": 78.5, "os": 23.0}


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
    src = (o + h + lo + c) / 4
    n = int(p["smooth_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (src - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["sma_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ob, os_ = float(p["ob"]), float(p["os"])
    d1 = d.shift(1)
    lc = ((d > os_) & (d1 <= os_)).to_numpy()
    sc = ((d < ob) & (d1 >= ob)).to_numpy()
    lxc = ((d > ob) & (d1 <= ob)).to_numpy()
    sxc = ((d < os_) & (d1 >= os_)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and pos <= 0:
            new = 1
        elif sc[i] and pos >= 0:
            new = -1
        elif (lxc[i] and pos == 1) or (sxc[i] and pos == -1):
            new = 0
        if new == 1 and pos != 1:
            le[i] = True
        elif new == -1 and pos != -1:
            se[i] = True
        elif new == 0 and pos == 1:
            lx[i] = True
        elif new == 0 and pos == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
