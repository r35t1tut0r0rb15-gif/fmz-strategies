"""LazyBear squeeze release with momentum colour, 2-hour bars: the squeeze turning off with rising positive momentum goes long, with falling negative momentum short; a fading colour closes; a
600-tick stop and 1000-tick target (about 0.2 / 0.33 ATR); reversing.
Port of FMZ strategy #441084 "基于LazyBear压缩动量指标的量化交易策略Squeeze-Momentum-Trading-Strategy-Based-on-LazyBear-Indicator" (SMS).

FMZ source id: 441084

Source
    https://www.fmz.com/strategy/441084 (PineScript v4, FMZ last modified 2024-02-05 14:48:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-171), BB 12 x 2, KC 16 x 1.5 on ohlc4; momentum filter off; stop 600, target 1000, trail_points 20 (ticks)
    val = linreg(ohlc4 - avg(avg(highest(hl2, 16), lowest(low, 16)), sma(hl2, 16)), 16, 0);  bcolor lime / green / red / maroon by sign and change;  scolor aqua = squeeze off
    long = scolor turns aqua and bcolor lime -> entry SQ_Long, exit(profit = 1000, trail_points = 20, loss = 600);  bcolor green -> close SQ_Long
    short = scolor turns aqua and bcolor red -> entry SQ_Short, same exit;  bcolor maroon -> close SQ_Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are tick counts from the entry: 60 and 100 price units at mintick 0.1 on the
      BTC reading; as ATR multiples at the 2-hour ATR(14) reading of about 300, a stop of 0.2 ATR and a
      target of 0.333 ATR (sl / tp = k ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill). trail_points is given without trail_offset, so the script places no trailing
      stop; none is ported. The KC uses the SMA of high - low, as written. A close acts only on the held
      position. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header (bars on UTC multiples of 2
      hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441084_squeeze_release_momentum_colour_tick_bracket"
FAMILY = "volatility_squeeze"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [12, 20],
    "length_kc": [16, 20],
}
DEFAULT_PARAMS = {"length": 12, "length_kc": 16, "mult": 2.0, "mult_kc": 1.5, "atr_len": 14,
                  "sl_atr": 0.2, "tp_atr": 0.333}


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


def _linreg_end(x, n):
    """Pine linreg(x, n, 0): the least-squares line over the last n values, valued at the current bar."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float)
        tm = t.mean()
        ym = w.mean(axis=1)
        slope = ((w - ym[:, None]) @ (t - tm)) / ((t - tm) ** 2).sum()
        out[n - 1:] = ym + slope * (n - 1 - tm)
    return pd.Series(out, index=x.index)


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4
    hl2 = (h + lo) / 2
    n, nk = int(p["length"]), int(p["length_kc"])
    ma1, ma2 = src.rolling(n).mean(), src.rolling(nk).mean()
    rma_ = (h - lo).rolling(nk).mean()
    dev = float(p["mult"]) * src.rolling(n).std(ddof=0)
    ubb, lbb = ma1 + dev, ma1 - dev
    ukc, lkc = ma2 + rma_ * float(p["mult_kc"]), ma2 - rma_ * float(p["mult_kc"])
    sqz_on = (lbb > lkc) & (ubb < ukc)
    sqz_off = (lbb < lkc) & (ubb > ukc)
    aqua = sqz_off & ~sqz_on      # scolor aqua: not no-squeeze and not squeeze-on
    mid = ((hl2.rolling(nk).max() + lo.rolling(nk).min()) / 2 + hl2.rolling(nk).mean()) / 2
    val = _linreg_end(src - mid, nk)
    vp = val.shift(1).where(val.shift(1).notna(), 0.0)
    lime = (val > 0) & (val > vp)
    green = (val > 0) & ~(val > vp)
    red = ~(val > 0) & (val < vp)
    maroon = ~(val > 0) & ~(val < vp) & val.notna()
    turn = aqua & ~aqua.shift(1, fill_value=False)
    el, es = (turn & lime).to_numpy(), (turn & red).to_numpy()
    xl, xs = green.to_numpy(), maroon.to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = o.to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        held = pos
        ok = i + 1 < m and not np.isnan(sl[i])
        if el[i] and pos != 1 and ok:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
        elif xl[i] and held == 1 and pos == 1 and i >= entry_i:
            lx[i], pos = True, 0
        if es[i] and pos != -1 and ok:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
        elif xs[i] and held == -1 and pos == -1 and i >= entry_i:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
