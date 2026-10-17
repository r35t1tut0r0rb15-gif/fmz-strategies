"""TSI and Vortex crosses on one bar with one-bar trades, 1-hour bars: the TSI 25 / 13 crossing above its signal on the same
bar as VI+ crosses above VI- goes long; the mirror goes short (reversing); each trade is closed one bar after its signal.
Port of FMZ strategy #435143 "Trend Tracking Strategy Based on Dual Vortex Indicator Combined with True Strength Index" (Vortex TSI strategy).

FMZ source id: 435143

Source
    https://www.fmz.com/strategy/435143 (PineScript v4, FMZ last modified 2023-12-12 16:23:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 153-202), TSI 25 / 13, signal 13; Vortex 14; close after 1 bar
    long = crossover(tsi, tsi_signal) and crossover(vi_plus, vi_minus) -> entry long;  long[1] -> close long
    short = crossunder(tsi, tsi_signal) and crossunder(vi_plus, vi_minus) -> entry short;  short[1] -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Close after x bar" closes the position on the bar after the signal (the fill bar), so it
      exits at the following open, unless a new signal on that bar wins. The closes act on the
      position held on the bar. strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TSI and Vortex crosses.
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

NAME = "fmz_435143_tsi_vortex_cross_one_bar"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 28],
    "bar": [1, 3],
}
DEFAULT_PARAMS = {"long_len": 25, "short_len": 13, "signal": 13, "period": 14, "bar": 1}


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
    pc = c.diff()
    ds = lambda x: x.ewm(span=int(p["long_len"]), adjust=False).mean().ewm(span=int(p["short_len"]), adjust=False).mean()  # noqa: E731
    tsi = 100 * ds(pc) / ds(pc.abs())
    tsig = tsi.ewm(span=int(p["signal"]), adjust=False).mean()
    n = int(p["period"])
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    vmp = (h - lo.shift(1)).abs().rolling(n).sum()
    vmm = (lo - h.shift(1)).abs().rolling(n).sum()
    st = tr.rolling(n).sum()
    vip, vim = vmp / st, vmm / st
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    lo_ = (xo(tsi, tsig) & xo(vip, vim)).to_numpy()
    so_ = (xo(tsig, tsi) & xo(vim, vip)).to_numpy()
    k = int(p["bar"])
    lcl = np.concatenate((np.zeros(k, dtype=bool), lo_[:-k])) if len(lo_) > k else np.zeros(len(lo_), dtype=bool)
    scl = np.concatenate((np.zeros(k, dtype=bool), so_[:-k])) if len(so_) > k else np.zeros(len(so_), dtype=bool)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if lo_[i] and pos != 1:                    # a long signal while long is a no-op entry
            new = 1
        if so_[i] and pos != -1:
            new = -1
        if pos == 1 and lcl[i] and not so_[i]:     # the close still acts on the open long
            new = 0
        if pos == -1 and scl[i] and not lo_[i]:
            new = 0
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
