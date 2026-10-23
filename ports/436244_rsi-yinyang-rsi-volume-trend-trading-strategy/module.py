"""Hourly bars: a purchase zone around an EMA 80 of VWMA-smoothed 80-bar highs and lows, widened by an RSI 80 of a volume-weighted mid line times the average range; the close coming back up out of the lower zone line (once re-armed) goes long and back down out of the upper line goes short; each side closes at the opposite line, a 0.1 % stop beyond its line, or a basis cross back after a cross through it; reversing.
Port of FMZ strategy #436244 "基于RSI和交易量的阴阳双轨趋势交易策略YinYang-RSI-Volume-Trend-Trading-Strategy" (YinYang RSI Volume Trend Strategy).

FMZ source id: 436244

Source
    https://www.fmz.com/strategy/436244 (PineScript v5, FMZ last modified 2023-12-22 14:29:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 207-298), length 80; purchase / exit source close; take profit on, stop loss on, stop multiplier 0.1 %; reset after Entry
    mid = avg(vwma(highest(high, 80), 80), vwma(lowest(low, 80), 80));  midSmoothed = ema(mid, 80);  midAdd = rsi(vwma(midSmoothed x volume / vwma(volume, 80), 3), 80) / 100 x sma(midHigh - midLow, 80)
    zones = midSmoothed +- midAdd;  longStart = crossover(close, zoneLow) and longAvailable;  longAvailable re-armed by crossunder(close, zoneHigh) or crossunder(close, zoneLow) (reset after Entry), cleared by longStart
    longStart -> entry buy, else crossover(close, zoneHigh) or crossunder(close, stopLow) or (basis crossed up then down) -> close buy;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The availability flags and the take-profit arming run as written; with "Reset Purchase Availability
      After: Entry" a dip under the lower line re-arms the long side. The stop and take-profit are bar-close
      crossings (exit at the next open), in the signals. A close acts only on a position the bar's entries
      leave unchanged (call order). The volume enters as its ratio to its own VWMA. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; zone-based close conditions in the signals.
    2 generic: PASS, volume-weighted RSI purchase-zone re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMA mid lines and the volume ratio volume / vwma(volume, 80); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436244_yinyang_rsi_volume_purchase_zone_reentry_reversal"
FAMILY = "zone_reentry"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [80, 40],
    "sl_mult": [0.1, 0.5],
}
DEFAULT_PARAMS = {"length": 80, "sl_mult": 0.1}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _vwma(x, v, n):
    s = v.rolling(n).sum()
    return (x * v).rolling(n).sum() / s.where(s != 0)


def _xo(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def _xu(a, b):
    return ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length"])
    mh = _vwma(h.rolling(n).max(), v, n)
    ml = _vwma(lo.rolling(n).min(), v, n)
    ms = ((mh + ml) / 2).ewm(span=n, adjust=False).mean()
    av = _vwma(v, v, n)
    vd = v / av.where(av != 0)
    mvs = _vwma(ms * vd, v, 3)
    add = _rsi(mvs, n) * 0.01 * (mh - ml).rolling(n).mean()
    zh, zl = ms + add, ms - add
    zb = (zh + zl) / 2
    k = float(p["sl_mult"]) * 0.01
    slh, sll = zh * (1 + k), zl * (1 - k)
    l_entry, l_cross_up, l_rearm = _xu(c, zl), _xo(c, zl), _xu(c, zh)
    l_end, l_sl, l_basis_up, l_basis_dn = _xo(c, zh), _xu(c, sll), _xo(c, zb), _xu(c, zb)
    s_entry, s_cross_dn, s_rearm = _xo(c, zh), _xu(c, zh), _xo(c, zl)
    s_end, s_sl = _xu(c, zl), _xo(c, slh)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    l_av = s_av = False
    l_tpa = s_tpa = False
    pos = 0
    for i in range(m):
        l_start = l_cross_up[i] and l_av
        l_av = True if (l_rearm[i] or l_entry[i]) else (False if l_start else l_av)
        l_tpa = True if l_basis_up[i] else (False if l_end[i] else l_tpa)
        l_tp = l_basis_dn[i] and l_tpa
        s_start = s_cross_dn[i] and s_av
        s_av = True if (s_rearm[i] or s_entry[i]) else (False if s_start else s_av)
        s_tpa = True if l_basis_dn[i] else (False if s_end[i] else s_tpa)
        s_tp = l_basis_up[i] and s_tpa
        changed = False
        if l_start:
            if pos != 1:
                le[i], pos, changed = True, 1, True
        elif (l_end[i] or l_sl[i] or l_tp) and pos == 1:
            lx[i], pos = True, 0
        if s_start:
            if pos != -1:
                se[i], le[i], lx[i], pos, changed = True, False, False, -1, True
        elif (s_end[i] or s_sl[i] or s_tp) and pos == -1 and not changed:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
