"""RSI and Bollinger 100 / 2.1 band re-entries, 1-hour bars: the RSI 7 crossing above 45 on the same bar as the close crosses
back above the lower band goes long, closed when the low crosses under the upper band; the RSI 14 crossing below 65 on
the same bar as the close crosses back under the upper band goes short, closed when the low crosses above the lower band.
Port of FMZ strategy #435096 "RSI与布林带双重策略RSI-and-Bollinger-Bands-Dual-Strategy" (Ezieh Str.v2).

FMZ source id: 435096

Source
    https://www.fmz.com/strategy/435096 (PineScript v4, FMZ last modified 2023-12-12 11:53:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 135-206), RSI 7 / 45 (long), RSI 14 / 65 (short); BB 100 x 2.1; date / session filters off; pyramiding 10
    crossover(rsi7, 45) and crossover(close, lower) -> entry long;  crossunder(low, upper) -> close long
    crossunder(rsi14, 65) and crossunder(close, upper) -> entry short;  crossover(low, lower) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Further entries while in the trade (pyramiding 10, equity-sized quantity) are adds: sizing,
      not ported. strategy.cancel only withdraws unfilled entries (no effect with bar-close orders).
      The closes act on the position held on the bar; an entry on the same bar wins. strategy.entry
      reverses: REVERSAL INTENDED. Population stdev, Wilder RSI. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and band crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-sized quantity, pyramiding and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the session filter is off).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435096_rsi_bb_reentry"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [100, 50],
    "l_os": [45, 30],
}
DEFAULT_PARAMS = {"l_len": 7, "l_os": 45, "s_len": 14, "s_ob": 65, "bb_len": 100, "bb_mult": 2.1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    lr, sr = _rsi(c, int(p["l_len"])), _rsi(c, int(p["s_len"]))
    n = int(p["bb_len"])
    basis, dev = c.rolling(n).mean(), float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, lw = basis + dev, basis - dev
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))  # noqa: E731
    lv_os, lv_ob = float(p["l_os"]), float(p["s_ob"])
    lc = ((lr > lv_os) & (lr.shift(1) <= lv_os) & xo(c, lw)).to_numpy()
    sc = ((sr < lv_ob) & (sr.shift(1) >= lv_ob) & xu(c, up)).to_numpy()
    xl, xs = xu(lo, up).to_numpy(), xo(lo, lw).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if lc[i]:
            new = 1
        if sc[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
