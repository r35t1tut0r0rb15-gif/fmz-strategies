"""MACD (16, 6, 5) signal crossings on the SAR side with an ATR stop, 1-hour bars: MACD crossing over its signal with the close above the SAR goes long, crossing under with the close below it short; a stop
1.5 ATR(14) from the signal close; reversing.
Port of FMZ strategy #442389 "动量均线交叉-Sakkoulas-交易策略Enhanced-Moving-Average-Crossover-Sakkoulas-Trading-Strategy" (Enhanced Moving Average Crossover sakkoulas with ATR and SAR).

FMZ source id: 442389

Source
    https://www.fmz.com/strategy/442389 (PineScript v5, FMZ last modified 2024-02-21 15:14:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-196), MACD fast 16, slow 6, signal 5 (as written); SAR ta.sar(0.02, 0.2, 15); ATR 14 x 1.5; RSI / SMA / stochastic / BB / RR inputs unused by the orders
    long = crossover(macd, signal) and close > sar -> entry Long Position, exit(stop = close - 1.5 atr);  short = crossunder(macd, signal) and close < sar -> entry Short Position, exit(stop = close + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SAR is called as ta.sar(0.02, 0.2, 15): increment 0.2 and maximum 15, as written. The stop is
      set on the signal bar from its close: sl = 1.5 ATR(14) / close, shifted one bar inside stops() and
      re-based on the fill; there is no target. A later signal while held moves the script's stop, which the
      port does not follow. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, MACD crossings on the SAR side with an ATR stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442389_macd_cross_sar_side_atr_stop_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 3.0],
    "signal_smoothing": [5, 9],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "signal_smoothing": 5, "fast": 16, "slow": 6, "atr_len": 14,
                  "sar_start": 0.02, "sar_inc": 0.2, "sar_max": 15.0}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar reference block: the SAR value (NaN on the first bar)."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _sl(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return float(p["atr_mult"]) * _rma(tr, int(p["atr_len"])) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sar = pd.Series(_sar(hv, lv, cv, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=c.index)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal_smoothing"]), adjust=False).mean()
    lsig = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > sar)).to_numpy()
    ssig = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (c < sar)).to_numpy()
    sl = _sl(bars_df, p).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_ = True, -1, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _sl(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
