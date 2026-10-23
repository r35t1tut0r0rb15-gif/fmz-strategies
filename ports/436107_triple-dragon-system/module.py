"""Hourly bars: two price levels, the close at the last zero cross of an extended price-volume trend (cumulative volume-weighted returns against its 200-bar mid-range) and the close at the last cross of an ATR-stepped SAR with the price; the close crossing over either level goes long, crossing under either goes short; reversing.
Port of FMZ strategy #436107 "Triple Dragon System" (TRIPLE DRAGON SYSTEM).

FMZ source id: 436107

Source
    https://www.fmz.com/strategy/436107 (PineScript v5, FMZ last modified 2023-12-21 11:56:31).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 142-285), EPVT length 200; Donchian 200 (plots only); SAR-X start 0.02, increment 0.02, maximum 0.8, ATR 14; TP 5 / 10 / 15 % (plots only)
    vt = cum(change(close) / close[1] x volume);  VTX = vt - (highest(vt, 200) + lowest(vt, 200)) / 2;  VTY = valuewhen(cross(VTX, 0), close, 0);  SSARX = valuewhen(cross(psar, close), close, 0)
    DRAGONBUY = crossover(close, max(SSARX, VTY)) or crossover(close, min(...)) -> entry Long;  DRAGONSELL = crossunder(either) -> entry Short;  closes on the opposite crossings

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SAR-X is the script's own: it starts from the first bar's candle, steps by af x ATR(14) (the
      true range before the ATR exists) instead of toward the extreme point, flips when the close passes
      the previous SAR, and resets af to 0.02 on a flip, as written. VTX only changes sign with the volume's
      shape, not its units. The Donchian "dontrend", the take-profit lines and the EMA 5 feed only plots.
      The close calls repeat the opposite entry conditions, so the strategy is a pure reversal. REVERSAL
      INTENDED. 100 % of equity and the commission are sizing and costs. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, crossings of signal-cross price levels (EPVT and SAR).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1000, commission 0.01 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the extended price-volume trend vt = cum(change / close[1] x volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436107_epvt_sarx_cross_level_breakout_reversal"
FAMILY = "level_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "epvt_len": [200, 100],
    "sar_max": [0.8, 0.2],
}
DEFAULT_PARAMS = {"epvt_len": 200, "sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.8}


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


def _sarx(o, h, lo, c, start, inc, mx):
    """The script's SUPER SAR-X (ATR-stepped)."""
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, 14)
    atr = atr.where(atr.notna(), tr).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    psar = np.full(m, np.nan)
    td_p, af_p, ep_p, ps_p = 0, np.nan, np.nan, np.nan
    for i in range(m):
        first_prev = i == 1
        l2s = td_p == 1 and cv[i] <= ps_p
        s2l = td_p == -1 and cv[i] >= ps_p
        change = first_prev or l2s or s2l
        if first_prev:
            td = 1 if cv[0] > ov[0] else -1
        else:
            td = -1 if l2s else (1 if s2l else td_p)
        if change:
            af = start
        elif (td == 1 and hv[i] > ep_p) or (td == -1 and lv[i] < ep_p):
            af = min(mx, af_p + inc)
        else:
            af = af_p
        if change and td == 1:
            ep = hv[i]
        elif change and td == -1:
            ep = lv[i]
        elif td == 1:
            ep = max(ep_p, hv[i]) if not np.isnan(ep_p) else np.nan
        else:
            ep = min(ep_p, lv[i]) if not np.isnan(ep_p) else np.nan
        if first_prev:
            ps = lv[0] if cv[0] > ov[0] else hv[0]
        elif change:
            ps = ep_p
        elif td == 1:
            ps = ps_p + af * atr[i]
        else:
            ps = ps_p - af * atr[i]
        psar[i] = ps
        td_p, af_p, ep_p, ps_p = td, af, ep, ps
    return pd.Series(psar, index=c.index)


def _valuewhen(cond, val):
    c, v = np.asarray(cond, dtype=bool), np.asarray(val, dtype=float)
    idx = np.maximum.accumulate(np.where(c, np.arange(len(c)), -1))
    return np.where(idx >= 0, v[np.maximum(idx, 0)], np.nan)


def _cross(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))) | ((a < b) & (a.shift(1) >= b.shift(1)))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["epvt_len"])
    vt = (c.diff() / c.shift(1) * v).fillna(0.0).cumsum().where(c.shift(1).notna())
    vtx = vt - (vt.rolling(n).max() + vt.rolling(n).min()) / 2
    zero = pd.Series(0.0, index=c.index)
    vty = _valuewhen(_cross(vtx, zero).to_numpy(), c.to_numpy())
    ps = _sarx(o, h, lo, c, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    ssarx = _valuewhen(_cross(ps, c).to_numpy(), c.to_numpy())
    mx = pd.Series(np.fmax(ssarx, vty), index=c.index).where(~(np.isnan(ssarx) | np.isnan(vty)))
    mn = pd.Series(np.fmin(ssarx, vty), index=c.index).where(~(np.isnan(ssarx) | np.isnan(vty)))
    up = ((c > mx) & (c.shift(1) <= mx.shift(1))) | ((c > mn) & (c.shift(1) <= mn.shift(1)))
    dn = ((c < mx) & (c.shift(1) >= mx.shift(1))) | ((c < mn) & (c.shift(1) >= mn.shift(1)))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up & ~dn, false, dn & ~up, false.copy()


def portfolio_kwargs(**params):
    return {}
