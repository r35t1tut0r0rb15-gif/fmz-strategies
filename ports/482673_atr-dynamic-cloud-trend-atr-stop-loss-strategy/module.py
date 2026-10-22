"""Tenkan / Kijun (9 / 26) crossings with the close beyond both (undisplaced) spans and the close 26 bars back on the far side, hourly bars: each side enters with a stop 1.5 ATR 14 from the signal close; the opposite crossing or the 26-bar-back close moving to the other side closes; reversing.
Port of FMZ strategy #482673 "动态波云趋势ATR止损策略-Dynamic-Cloud-Trend-ATR-Stop-Loss-Strategy" (Ichimoku Cloud + ATR Strategy).

FMZ source id: 482673

Source
    https://www.fmz.com/strategy/482673 (PineScript v5, FMZ last modified 2025-02-27 17:54:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-168), Tenkan 9, Kijun 26, Span B 52, displacement 26; ATR 14 x 1.5; 10 % of equity
    crossover(tenkan, kijun) and close > spanA and close > spanB and close[26] > close -> entry Long + exit(stop = close - 1.5 atr);  mirror -> entry Short + exit(stop = close + 1.5 atr)
    crossunder(tenkan, kijun) or close[26] < close -> close Long;  crossover or close[26] > close -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are compared without their forward displacement, as written (spanA is an SMA of 1, the
      plain midpoint), and the "Chikou" test compares the close 26 bars back with today's close. The stop
      is fixed at the signal close and sent as a fraction of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256); an opposite crossing always closes first, so no
      repeat re-sends it. The entries come before the closes: an entry that reverses a position stands
      although the other side's close is true on that bar (as #441963). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop as a fraction of the fill.
    2 generic: PASS, Tenkan / Kijun crossings with cloud and lag filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482673_tenkan_kijun_cross_cloud_lag26_atr_stop_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_multiplier": [1.5, 3.0],
    "displacement": [26, 52],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.5, "displacement": 26, "conversion": 9, "base": 26, "span_b": 52,
                  "atr_length": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    tk, kj, sb = mid(p["conversion"]), mid(p["base"]), mid(p["span_b"])
    sa = (tk + kj) / 2
    lag = c.shift(int(p["displacement"]))
    up = (tk > kj) & (tk.shift(1) <= kj.shift(1))
    dn = (tk < kj) & (tk.shift(1) >= kj.shift(1))
    le = up & (c > sa) & (c > sb) & (lag > c)
    se = dn & (c < sa) & (c < sb) & (lag < c)
    lx = dn | (lag < c)
    sx = up | (lag > c)
    d = _atr(bars_df, int(p["atr_length"])) * float(p["atr_multiplier"])
    return le, se, lx, sx, {"l_sl": c - d, "s_sl": c + d}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lx, sx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = lvl["l_sl"].shift(1) >= o                    # marketable at the fill
    s_thr = lvl["s_sl"].shift(1) <= o
    return le, ((lf & l_thr) | lx) & ~se & ~le, se, ((sf & s_thr) | sx) & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lx, sx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
