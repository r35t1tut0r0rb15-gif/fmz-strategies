"""Breakouts of an SMA 20 +- 2 ATR 20 band, 1-hour bars: a high over the upper band goes long and a low under the lower band goes short; a long closes on a low under SMA - 1 ATR or a high over SMA + 2 ATR (so also on the next upper-band breakout), the short mirrored; reversing.
Port of FMZ strategy #451698 "ATR均线突破策略-ATR-Average-Breakout-Strategy" (Consolidation Breakout Strategy (ATR average breakout)).

FMZ source id: 451698

Source
    https://www.fmz.com/strategy/451698 (PineScript v5, FMZ last modified 2024-05-17 10:22:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-151), SMA 20; ATR 20; band 2 ATR; exits SMA -1 / +2 ATR (the 'percentage' inputs used as ATR multiples); risk 1 % of equity / ATR
    high > sma + 2 atr -> entry Long;  low < sma - 2 atr -> entry Short
    low < sma - 1 atr or high > sma + 2 atr -> close Long;  high > sma + 1 atr or low < sma - 2 atr -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; an entry on the held side is ignored, an opposite
      entry reverses, and a close acts only on the trade held into the bar when no earlier call
      reversed it. The long's take-profit test equals its entry test, so a held long is closed on the
      next bar whose high clears the upper band, and a new long needs a later breakout bar (the short
      likewise). A bar breaking both bands ends short (the later call wins, as #437773). The
      'not consolidating' test is implied by a breakout. REVERSAL INTENDED. The risk-per-ATR quantity
      is sizing (stored). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-band breakouts with band exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-per-ATR quantity stored.
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

NAME = "fmz_451698_sma_atr_band_breakout_band_exits_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "sl_mult": 1.0, "tp_mult": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length"])
    atr = _atr(bars_df, n)
    avg = bars_df["close"].rolling(n).mean()
    k, ks, kt = float(p["mult"]), float(p["sl_mult"]), float(p["tp_mult"])
    el = (h > avg + k * atr).to_numpy()
    es = (lo < avg - k * atr).to_numpy()
    xl = ((lo < avg - atr * ks) | (h > avg + atr * kt)).to_numpy()
    xs = ((h > avg + atr * ks) | (lo < avg - atr * kt)).to_numpy()
    m = len(el)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
