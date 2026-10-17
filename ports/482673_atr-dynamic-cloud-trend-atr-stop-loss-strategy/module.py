"""Tenkan / kijun crosses beyond the (undisplaced) cloud with the close 26 bars ago on the far side, a 1.5 ATR stop
from the signal close, closed at the opposite cross or when the 26-bar-old close flips sides, hourly bars.
Port of FMZ strategy #482673 "动态波云趋势ATR止损策略-Dynamic-Cloud-Trend-ATR-Stop-Loss-Strategy" (Ichimoku Cloud + ATR Strategy).

FMZ source id: 482673

Source
    https://www.fmz.com/strategy/482673 (PineScript v5, FMZ last modified 2025-02-27 17:54:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-143), Ichimoku 9 / 26 / 52, displacement 26, ATR 14 x 1.5
    spanA = sma((tenkan + kijun) / 2, 1), spanB = 52-bar mid (not displaced); chikou = close[26]
    crossover(tenkan, kijun) and close > spanA and close > spanB and close[26] > close -> entry long with
    exit(stop = close - 1.5 ATR) (short mirrored)
    crossunder(tenkan, kijun) or close[26] < close -> close long; crossover or close[26] > close -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chikou test compares close[26] with the current close, as written (a long needs the close BELOW the close
      26 bars ago).
    * The stop is placed with the entry: 1.5 ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill (house rule).
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). simulate() mirrors the house stop from the fill (as #430254); exits are emitted
      only on going flat.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a stop set at entry.
    2 generic: PASS, Ichimoku mid-points, lagged closes and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity; the stop via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482673_tenkan_kijun_cross_cloud_chikou_atr_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "base_len": [26, 20],
}
DEFAULT_PARAMS = {"conv_len": 9, "base_len": 26, "span_b_len": 52, "displacement": 26, "atr_len": 14,
                  "atr_mult": 1.5}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _mid(bars_df, n):
    return (bars_df["high"].rolling(n).max() + bars_df["low"].rolling(n).min()) / 2


def _fracs(bars_df, p):
    return (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy()


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    tk, kj = _mid(bars_df, int(p["conv_len"])), _mid(bars_df, int(p["base_len"]))
    a, b = (tk + kj) / 2, _mid(bars_df, int(p["span_b_len"]))
    ch = c.shift(int(p["displacement"]))
    up = (tk > kj) & (tk.shift(1) <= kj.shift(1))
    dn = (tk < kj) & (tk.shift(1) >= kj.shift(1))
    buy = (up & (c > a) & (c > b) & (ch > c)).to_numpy()
    sell = (dn & (c < a) & (c < b) & (ch < c)).to_numpy()
    xl, xs = (dn | (ch < c)).to_numpy(), (up | (ch > c)).to_numpy()
    sl = _fracs(bars_df, p)
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house stop from the fill price
            e = o[entry_i]
            if (pos == 1 and lo[i] <= e * (1 - s_)) or (pos == -1 and h[i] >= e * (1 + s_)):
                pos = 0
        start = pos
        if buy[i] and pos != 1 and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
        if sell[i] and pos != -1 and i + 1 < m and not np.isnan(sl[i]):
            se[i], pos, entry_i, s_ = True, -1, i + 1, sl[i]
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": pd.Series(_fracs(bars_df, p), index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
