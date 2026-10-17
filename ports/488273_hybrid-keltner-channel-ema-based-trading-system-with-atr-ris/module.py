"""Keltner fades plus EMA-cross trend entries, each with its own exit and a 1.5 / 3 ATR bracket, 1-hour bars: the close
crossing under the lower Keltner band (EMA 20 +- 1.5 ATR 20) goes long and leaves on a cross back over the EMA 20; the
upper band mirrors it for shorts; an EMA 9 / 21 cross in the EMA 50 trend goes long (short) and leaves on the
opposite cross; every trade has a stop 1.5 ATR and a target 3 ATR away.
Port of FMZ strategy #488273 "尺度移动均线与双布林线动量混合交易系统-Hybrid-Keltner-Channel-EMA-Based-Trading-System-with-ATR-Risk-Management" (Keltner Channel Strategy).

FMZ source id: 488273

Source
    https://www.fmz.com/strategy/488273 (PineScript v5, FMZ last modified 2025-03-26 14:21:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 173-221), KC EMA 20 +- 1.5 x ATR 20, EMA 9 / 21 / 50, stop 1.5 ATR, target 3 ATR
    Long_KC: crossunder(close, lowerKC), closed by crossover(close, ema20);  Short_KC mirrored
    Long_Trend: crossover(ema9, ema21) and close > ema50, closed by crossunder(ema9, ema21);  Short_Trend mirrored
    every bar: exit(from each entry, stop = close -+ 1.5 ATR, limit = close +- 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * One position at a time (default pyramiding 1): a same-side entry under another id is ignored; an opposite entry
      reverses; several entries on one bar are taken in the order written. Each close applies only to the entry id
      that opened the position and acts on the position held at the bar's start (#430850).
    * The bracket is re-issued every bar from the current close (moving): fixed at entry, mark
      trailing_stop_pending (sl_stop = sl_mult x ATR / close of the signal bar, tp_stop = 2 x that, shifted one bar
      inside stops(), re-based on the fill). simulate() mirrors that bracket from the fill bar (#430254) so the entry
      ids and their closes follow the position the engine holds.
    * REVERSAL INTENDED. Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (re-issue marked).
    2 generic: PASS, channels, EMAs and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488273_keltner_fade_ema_trend_bracket"
FAMILY = "keltner_channel"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "kc_mult": [1.5, 2.0],
    "sl_mult": [1.5, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "kc_mult": 1.5, "sl_mult": 1.5, "tp_ratio": 2.0}


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


def _cross(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def _sl_frac(bars_df, p):
    return p["sl_mult"] * _atr(bars_df, int(p["length"])) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.ewm(span=n, adjust=False).mean()
    atr = _atr(bars_df, n)
    up_kc, lo_kc = basis + p["kc_mult"] * atr, basis - p["kc_mult"] * atr
    e9, e21, e50 = (c.ewm(span=k, adjust=False).mean() for k in (9, 21, 50))
    above50, below50 = (c > e50).to_numpy(), (c < e50).to_numpy()
    rules = [  # (side, entry, close) in the order written
        (1, _cross(lo_kc, c), _cross(c, basis)),
        (-1, _cross(c, up_kc), _cross(basis, c)),
        (1, _cross(e9, e21) & above50, _cross(e21, e9)),
        (-1, _cross(e21, e9) & below50, _cross(e9, e21)),
    ]
    sl_f = _sl_frac(bars_df, p).to_numpy(dtype=float)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pid, fill_i, s_, t_ = 0, -1, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= fill_i:                     # the house bracket from the fill price
            e = ov[fill_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos, pid = 0, -1
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos, pid = 0, -1
        start, spid = pos, pid
        for k, (side, ent, ext) in enumerate(rules):
            if ent[i] and pos != side:
                pos, pid, fill_i = side, k, i + 1
                s_, t_ = sl_f[i], p["tp_ratio"] * sl_f[i]
            if ext[i] and start == side and spid == k and pos == start and pid == spid:
                pos, pid = 0, -1
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = _sl_frac(bars_df, p).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_ratio"] * sl}


def portfolio_kwargs(**params):
    return {}
