"""TMO divergences inside an adaptive-moving-average band regime, 10-minute bars: the band regime is up after a high
crosses the upper AMA band and down after a low crosses the lower one; a bullish TMO divergence in the up regime (a
bearish one in the down regime), followed by the first of three growing smoothed candle bodies, opens a trade from flat
with a stop at the 10-bar swing low (high); a bearish divergence or the regime turning down closes a long (mirror for
shorts).
Port of FMZ strategy #433922 "双指标组合疯狂日内scalping策略Dual-Indicators-Combo-Crazy-Intraday-Scalping-Strategy" (TradeIQ - Crazy Scalping Trading Strategy [Kaspricci]).

FMZ source id: 433922

Source
    https://www.fmz.com/strategy/433922 (PineScript v5, FMZ last modified 2023-12-01 14:47:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 169-327), TMO 7 (close); AMA 50, factor 2, lag 1.0, overshoot 0.5; SL swing period 10
    osc = mom(sma(sma(close, 7), 7), 7);  bear = osc > 0 and crossunder(change(osc), 0) with a lower osc and a higher 7-bar high than at the previous such turn;  bull mirrors
    AMA = sum(close[i] b_i) / sum(b), b_i = sin(2 pi x^1) (1 - x^0.5), x = i / 49;  bands = AMA +/- 2 sma(|close - AMA|, 50);  os = cross(high, upper) ? 1 : cross(low, lower) ? 0 : os[1]
    longEntry = flat and growing bodies (first bar) and barssince(os == 1 and bull) < barssince(os == 0) and < barssince(bear);  exit(loss = (close - lowest(low, 10)) ticks)
    longExit = long and (bear or os == 0) -> close;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is placed in ticks equal to the distance from the signal close to the 10-bar swing low,
      i.e. at that distance from the entry price: sl_stop = (close - lowest(low, 10)) / close of the
      signal bar (highest(high, 10) for shorts), shifted one bar and re-based on the fill. A signal
      whose close is itself the 10-bar extreme (stop distance 0, a stop at the entry price) is skipped:
      a stated deviation, rare.
    * Entries need a flat position. The engine runs the stop; simulate() tracks the same stop on the
      bars' highs and lows (from the bar after the fill) only to know when the source is flat again.
      The ta.cross tests are crosses in either direction, as written; the smoothed candles use the
      same AMA kernel on the closes. pi is 3.14159 as written.
    * Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver
      D4). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, oscillator divergences, a band regime and a swing-distance stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433922_tmo_ama_scalper"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ama_len": [50, 100],
    "sl_len": [10, 20],
}
DEFAULT_PARAMS = {"tmo_len": 7, "ama_len": 50, "ama_mult": 2.0, "alpha": 1.0, "beta": 0.5, "sl_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ama(v, n, alpha, beta):
    x = np.arange(n) / (n - 1)
    b = np.sin(2 * 3.14159 * np.power(x, alpha)) * (1 - np.power(x, beta))   # b[i] weighs the value i bars ago
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (b[::-1] / b.sum())
    return out


def _barssince(v):
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _turns(turn, osc, ext):
    """valuewhen(turn, osc / ext, 0) and (..., 1): the values at the latest and the previous turn."""
    m = len(turn)
    o0, o1, e0, e1 = (np.full(m, np.nan) for _ in range(4))
    a0 = a1 = b0 = b1 = np.nan
    for i in range(m):
        if turn[i]:
            a1, a0, b1, b0 = a0, osc[i], b0, ext[i]
        o0[i], o1[i], e0[i], e1[i] = a0, a1, b0, b1
    return o0, o1, e0, e1


def _signals(bars_df, p):
    o = bars_df["open"].to_numpy(dtype=float)
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    cs = bars_df["close"]
    c = cs.to_numpy(dtype=float)
    t = int(p["tmo_len"])
    s2 = cs.rolling(t).mean().rolling(t).mean()
    osc_s = s2 - s2.shift(t)
    osc = osc_s.to_numpy()
    upx = cs.rolling(t).max().to_numpy()
    dnx = cs.rolling(t).min().to_numpy()
    chg = osc_s.diff()
    ph = ((chg < 0) & (chg.shift(1) >= 0)).to_numpy()
    pl = ((chg > 0) & (chg.shift(1) <= 0)).to_numpy()
    po0, po1, pu0, pu1 = _turns(ph, osc, upx)
    lo0, lo1, ld0, ld1 = _turns(pl, osc, dnx)
    with np.errstate(invalid="ignore"):
        bear = (osc > 0) & ph & (po0 < po1) & (pu0 > pu1)
        bull = (osc < 0) & pl & (lo0 > lo1) & (ld0 < ld1)
    n = int(p["ama_len"])
    f = _ama(c, n, float(p["alpha"]), float(p["beta"]))
    fs = pd.Series(f, index=cs.index)
    dev = ((cs - fs).abs().rolling(n).mean() * float(p["ama_mult"])).to_numpy()
    up_b, lo_b = f + dev, f - dev
    m = len(c)
    osr = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(1, m):
        ch_ = (h[i] > up_b[i] and h[i - 1] <= up_b[i - 1]) or (h[i] < up_b[i] and h[i - 1] >= up_b[i - 1])
        cl_ = (lo[i] > lo_b[i] and lo[i - 1] <= lo_b[i - 1]) or (lo[i] < lo_b[i] and lo[i - 1] >= lo_b[i - 1])
        if ch_:
            q = 1
        elif cl_:
            q = 0
        osr[i] = q
    body = (((fs.shift(1) + fs.shift(2)) / 2) - fs).abs()
    grow = ((body.shift(2) < body.shift(1)) & (body.shift(1) < body)).to_numpy()
    first_grow = grow & ~np.concatenate(([False], grow[:-1]))
    bs_l = _barssince((osr == 1) & bull)
    bs_s = _barssince((osr == 0) & bear)
    bs_o0, bs_o1 = _barssince(osr == 0), _barssince(osr == 1)
    bs_bear, bs_bull = _barssince(bear), _barssince(bull)
    with np.errstate(invalid="ignore"):
        lcond = first_grow & (bs_l < bs_o0) & (bs_l < bs_bear)
        scond = first_grow & (bs_s < bs_o1) & (bs_s < bs_bull)
    sl_n = int(p["sl_len"])
    ll = bars_df["low"].rolling(sl_n).min().to_numpy()
    hh = bars_df["high"].rolling(sl_n).max().to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    frac = np.full(m, np.nan)
    pos, pending, pend_exit, fill, entry, dist = 0, 0, False, -1, np.nan, np.nan
    for i in range(m):
        if pending != 0:
            pos, entry, fill, pending = pending, o[i], i, 0
        if pend_exit:
            pos, pend_exit = 0, False
        if pos == 1 and i > fill and lo[i] <= entry - dist:
            pos = 0
        elif pos == -1 and i > fill and h[i] >= entry + dist:
            pos = 0
        if pos == 1 and (bear[i] or osr[i] == 0):
            lx[i], pend_exit = True, True
        elif pos == -1 and (bull[i] or osr[i] == 1):
            sx[i], pend_exit = True, True
        elif pos == 0:
            if scond[i] and hh[i] > c[i]:
                se[i], pending, dist = True, -1, hh[i] - c[i]
                frac[i] = dist / c[i]
            elif lcond[i] and c[i] > ll[i]:
                le[i], pending, dist = True, 1, c[i] - ll[i]
                frac[i] = dist / c[i]
    return le, lx, se, sx, frac


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _signals(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _signals(bars_df, p)[4]
    return {"sl_stop": pd.Series(frac, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
