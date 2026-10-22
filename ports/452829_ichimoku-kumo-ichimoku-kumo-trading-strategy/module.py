"""Ichimoku cloud re-entries after a set-up, 1-hour bars: within 50 bars of a set-up (the Kijun over the cloud with the close under it), a close back over the cloud top and the Kijun goes long; the mirror goes short; a 5-bar-high minus 3 ATR 5 trailing level, raised only, closes the long on a close under it (the short mirrored); reversing.
Port of FMZ strategy #452829 "Ichimoku-Kumo交易策略Ichimoku-Kumo-Trading-Strategy" (Kumo Trade Concept).

FMZ source id: 452829

Source
    https://www.fmz.com/strategy/452829 (PineScript v5, FMZ last modified 2024-05-29 17:23:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-197), Tenkan 9, Kijun 26, Senkou B 52 (Donchian midpoints), the cloud of 25 bars back; set-up look-back 0-50; trail highest(high, 5) - 3 ATR 5 / lowest(low, 5) + 3 ATR 5; 30 % of equity, margin 10, commission 0.1 %
    long set-up: kijun > cloud top and close < cloud bottom (any of the last 51 bars);  close > cloud top and close > kijun -> entry Buy, trail = na
    long: trail = max(trail, highest(high, 5) - 3 atr);  close < trail -> close Buy;  the mirror for Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud is the spans of 25 bars back (senkou A from the Tenkan / Kijun then, senkou B from the
      52-bar range then). The trailing level is a bar-close test, followed in a loop: it is reset on
      every entry signal (also inside a trade), raised only while the position is on and kept after
      the trade ends (a close against it while flat does nothing). A close acts only on the trade held
      into the bar when no earlier call reversed it. barstate.isconfirmed is true on every historical
      bar. REVERSAL INTENDED. The 30 % of equity, margin 10 and commission are stored. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-based trailing exit in a loop.
    2 generic: PASS, cloud re-entries after a set-up.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing, margin and commission stored.
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

NAME = "fmz_452829_kumo_setup_reentry_atr_trail_close_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "setup_lookback": [50, 10],
    "trail_atr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"setup_lookback": 50, "trail_atr": 3.0, "atr_len": 5, "tenkan": 9, "kijun": 26,
                  "senkou_b": 52, "back": 25, "trail_len": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    tenkan, kijun = mid(p["tenkan"]), mid(p["kijun"])
    k = int(p["back"])
    sa = (tenkan.shift(k) + kijun.shift(k)) / 2
    sb = mid(p["senkou_b"]).shift(k)
    top = sa.where(sa >= sb, sb)
    bot = sa.where(sb >= sa, sb)
    long_setup = (kijun > top) & (c < bot)
    short_setup = (kijun < bot) & (c > top)
    w = int(p["setup_lookback"]) + 1
    ls = long_setup.astype(float).rolling(w, min_periods=1).max() > 0
    ss = short_setup.astype(float).rolling(w, min_periods=1).max() > 0
    buy = ((c > top) & ls & (c > kijun)).to_numpy()
    sell = ((c < bot) & ss & (c < kijun)).to_numpy()
    atr = _atr(bars_df, p["atr_len"]) * float(p["trail_atr"])
    tl = (h.rolling(int(p["trail_len"])).max() - atr).to_numpy()
    ts = (lo.rolling(int(p["trail_len"])).min() + atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, stl, sts = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend = (0 if pend == 2 else pend), 0
        cur = pos
        if buy[i]:
            cur, stl = (1 if cur != 1 else cur), np.nan
        if sell[i]:
            cur, sts = (-1 if cur != -1 else cur), np.nan
        if pos > 0 and (tl[i] > stl or np.isnan(stl)):
            stl = tl[i]
        if pos < 0 and (ts[i] < sts or np.isnan(sts)):
            sts = ts[i]
        if cv[i] < stl and pos == 1 and cur == 1:
            lx[i], cur = True, 0
        if cv[i] > sts and pos == -1 and cur == -1:
            sx[i], cur = True, 0
        if cur != pos:
            pend = 2 if cur == 0 else cur
    ix = bars_df.index
    return (pd.Series(buy & ~lx, index=ix), pd.Series(lx, index=ix),
            pd.Series(sell & ~sx, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
