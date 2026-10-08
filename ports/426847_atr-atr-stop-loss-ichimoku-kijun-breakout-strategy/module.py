"""Kijun breakout with one-bar Williams %R: from flat, a bar opening below the 20-bar Kijun and
closing above it with %R(1) >= -25 goes long (shorts mirrored at <= -75); a close back across
the Kijun closes it; each trade carries an ATR stop and a fixed target.
Port of FMZ strategy #426847 "ATR Stop Loss Ichimoku Kijun Breakout Strategy".

Source
    https://www.fmz.com/strategy/426847 (PineScript v4, FMZ last modified 2023-09-14 20:06:11).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 146-214), ATR 14 x 1.5, Kijun 20, %R 1 (-25 / -75),
target 150 points
    kijun = (highest(high, 20) + lowest(low, 20)) / 2
    long  = open < kijun and close > kijun and wpr(1) >= -25 and no open trade
    short = open > kijun and close < kijun and wpr(1) <= -75 and no open trade
    exit(loss = atr * 100000 * 1.5, profit = 150) re-issued every bar
    close < kijun -> close long;  close > kijun -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: loss = ATR x 100000 x 1.5 ticks is 1.5 ATR on a 5-digit forex pair (the
      evident meaning, as #426142); the 150-point target becomes tp_atr x ATR(14). Both at the
      signal bar, applied to the fill.
    * The loss is re-issued every bar with the current ATR (a moving level): rule 2, mark
      trailing_stop_pending; the port fixes the signal bar's ATR.
    * The equity protector (close all when the open loss exceeds 30 % of the balance) is a
      balance check: sizing (original_sizing.txt), not ported.
    * Entries need a flat position, so simulate() mirrors the engine's stop and target from the
      fill bar on; the Kijun exits are close-based exit signals. Opposite entries cannot occur.
    * FREQ = "15min" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426847_kijun_wpr_atr_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ks_period": [20, 26],
    "sl_atr": [1.5, 2.0],
    "tp_atr": [0.25, 1.0, 2.0],
}
DEFAULT_PARAMS = {"atr_period": 14, "ks_period": 20, "wpr_len": 1, "wpr_up": -25, "wpr_low": -75,
                  "sl_atr": 1.5, "tp_atr": 0.25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _setup(bars_df, p):
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["ks_period"])
    kijun = (h.rolling(n).max() + l.rolling(n).min()) / 2
    w = int(p["wpr_len"])
    hh, ll = h.rolling(w).max(), l.rolling(w).min()
    wpr = -100 * (hh - c) / (hh - ll)
    long_c = (o < kijun) & (c > kijun) & (wpr >= p["wpr_up"])
    short_c = (o > kijun) & (c < kijun) & (wpr <= p["wpr_low"])
    frac = _atr_pine(bars_df, int(p["atr_period"])) / c
    return long_c.to_numpy(), short_c.to_numpy(), (c < kijun).to_numpy(), (c > kijun).to_numpy(), frac


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, x_long, x_short, frac = _setup(bars_df, p)
    fr = frac.to_numpy()
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pending, f, stop, target = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop, target = e * (1 - pos * p["sl_atr"] * f), e * (1 + pos * p["tp_atr"] * f)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            pos = 0
        if pos == 0 and not pending:
            if long_c[i]:
                le[i], pending, f = True, 1, fr[i]
            elif short_c[i]:
                se[i], pending, f = True, -1, fr[i]
        elif pos == 1 and x_long[i]:
            lx[i], pos = True, 0
        elif pos == -1 and x_short[i]:
            sx[i], pos = True, 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = simulate(bars_df, **params)
    *_, frac = _setup(bars_df, p)
    f = frac.where(le | se)
    return {"sl_stop": (p["sl_atr"] * f).shift(1), "tp_stop": (p["tp_atr"] * f).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
