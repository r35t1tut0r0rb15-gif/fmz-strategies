"""Hourly bars: the close above the average of seven 12-bar moving averages of the high (SMA, EMA, WMA, ALMA, RMA, LSMA, VWMA) goes long, below the same average of the low goes short; the low crossing under the low channel closes a long, the high crossing over the high channel closes a short; brackets of 6 % / 5 % (long) and 4.5 % / 5 % (short); reversing.
Port of FMZ strategy #442220 "Multi Period Moving Average Channel Trend Following Strategy" (High/Low channel swing (Multi MA swing) (exlux99)).

FMZ source id: 442220

Source
    https://www.fmz.com/strategy/442220 (PineScript v4, FMZ last modified 2024-02-20 13:45:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 150-222), MA length 12; TP long 6 %, SL long 5 %, TP short 4.5 %, SL short 5 % (of the close, in ticks)
    avg_high = (sma + ema + wma + alma(0.85, 6) + rma + linreg + vwma)(high, 12) / 7;  long = close > avg_high -> entry long, exit(profit = close x 0.06 / mintick, loss = close x 0.05 / mintick);  close long when crossunder(low, avg_low)
    short = close < avg_low -> entry short, exit(profit = close x 0.045 / mintick, loss = close x 0.05 / mintick);  close short when crossover(high, avg_high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket distances are re-sent every bar from the latest close; the port fixes them at the
      signal close as fractions of the fill (pct x close[signal] / open[fill], mark trailing_stop_pending)
      and the signals follow that bracket, so a position it ends re-enters on the next bar of its state,
      as Pine's repeated entry does. ALMA as Pine's (offset 0.85, sigma 6, no floor). A close acts only on a
      position the bar's entries leave unchanged. The 2000 .. 2021 date inputs feed nothing. REVERSAL
      INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, breakouts of a seven-average high / low channel.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the VWMA of the high and of the low (one of the seven averages); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442220_seven_ma_high_low_channel_breakout_pct_bracket_1h_reversal"
FAMILY = "ma_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length_ma": [12, 24],
    "tp_long": [0.06, 0.03],
}
DEFAULT_PARAMS = {"length_ma": 12, "tp_long": 0.06, "sl_long": 0.05, "tp_short": 0.045, "sl_short": 0.05}


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


def _window(x, w):
    v = x.to_numpy(dtype=float)
    n = len(w)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w     # oldest first
    return pd.Series(out, index=x.index)


def _seven(x, v, n):
    wma_w = np.arange(1, n + 1, dtype=float)
    m = 0.85 * (n - 1)
    s = n / 6.0
    alma_w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))
    t = np.arange(n, dtype=float)
    tb = t.mean()
    lin_w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    sv = v.rolling(n).mean()
    parts = [x.rolling(n).mean(), x.ewm(span=n, adjust=False).mean(), _window(x, wma_w / wma_w.sum()),
             _window(x, alma_w / alma_w.sum()), _rma(x, n), _window(x, lin_w),
             (x * v).rolling(n).mean() / sv.where(sv != 0)]
    return sum(parts) / 7


def _levels(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["length_ma"])
    return _seven(h, v, n), _seven(lo, v, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    avg_h, avg_l = _levels(bars_df, p)
    lg, sh = (c > avg_h).to_numpy(), (c < avg_l).to_numpy()
    xl = ((lo < avg_l) & (lo.shift(1) >= avg_l.shift(1))).to_numpy()
    xs = ((h > avg_h) & (h.shift(1) <= avg_h.shift(1))).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    tl, sl_l = float(p["tp_long"]), float(p["sl_long"])
    ts, sl_s = float(p["tp_short"]), float(p["sl_short"])
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, up_px, dn_px = 0, np.nan, np.nan
    for i in range(m):
        if i > 0 and le[i - 1]:
            up_px, dn_px = ov[i] + tl * cv[i - 1], ov[i] - sl_l * cv[i - 1]
        elif i > 0 and se[i - 1]:
            up_px, dn_px = ov[i] + sl_s * cv[i - 1], ov[i] - ts * cv[i - 1]
        if tgt != 0 and (hv[i] >= up_px or lv[i] <= dn_px):     # the bracket ends the trade inside the bar
            tgt = 0
        pos = tgt
        new = pos
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and xl[i]:
                new = 0
            elif pos == -1 and xs[i]:
                new = 0
        if new != pos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, float(p["sl_long"]) * k).mask(sf, float(p["sl_short"]) * k)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, float(p["tp_long"]) * k).mask(sf, float(p["tp_short"]) * k)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
