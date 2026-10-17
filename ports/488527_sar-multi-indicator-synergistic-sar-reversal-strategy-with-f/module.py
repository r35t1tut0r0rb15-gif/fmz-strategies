"""Parabolic SAR flips filtered by RSI, MACD, stochastic RSI and an offset LSMA, always in, 3-hour bars: the close
crossing above the SAR goes long when RSI 14 > 30, MACD is above its signal, the stochastic RSI is above 20 and the
close is above the LSMA(4) of 9 bars ago; shorts mirrored; the opposite signal reverses.
Port of FMZ strategy #488527 "多指标联动SAR反转策略与过滤入场模型-Multi-Indicator-Synergistic-SAR-Reversal-Strategy-with-Filtered-Entry-Model" (SAR Reversal Strategy with Filtered Entries & Opposite Exits).

FMZ source id: 488527

Source
    https://www.fmz.com/strategy/488527 (PineScript v6, FMZ last modified 2025-03-28 16:36:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 174-222), SAR 0.02 / 0.02 / 0.2, RSI 14 (30 / 70), stoch RSI 14 (20 / 80), LSMA 4 offset 9
    validLong = crossover(close, sar) and rsi > 30 and macd > signal and stochRsi > 20 and close > lsma[9]
    validShort = crossunder(close, sar) and rsi < 70 and macd < signal and stochRsi < 80 and close < lsma[9]
    validLong -> close short, entry long;  validShort -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.sar as TradingView documents it (as #428699); ta.stoch(rsi, rsi, rsi, 14) = 100 x (rsi - lowest) / (highest
      - lowest) over 14 bars (na on a flat window); ta.linreg(close, 4, 0) is the least-squares line's value at the
      current bar; MACD 12 / 26 / 9 on EMAs.
    * The close before each entry is the reversal itself (REVERSAL INTENDED); the two signals cannot fall on one bar.
    * FREQ = "3h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR, oscillators and a regression line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_488527_sar_flip_rsi_macd_stoch_lsma"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_max": [0.2, 0.1],
    "lsma_offset": [9, 4],
}
DEFAULT_PARAMS = {"sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30,
                  "stoch_len": 14, "stoch_ob": 80, "stoch_os": 20, "lsma_len": 4, "lsma_offset": 9}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _linreg(x, n):
    """ta.linreg(x, n, 0): the least-squares line over the last n values, evaluated at the current bar."""
    w = np.arange(n, dtype=float)
    wm = w.mean()
    den = ((w - wm) ** 2).sum()

    def f(y):
        ym = y.mean()
        return ym + ((w - wm) * (y - ym)).sum() / den * (n - 1 - wm)
    return x.rolling(n).apply(f, raw=True)


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar), as #428699."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
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
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo_r, hi_r = rsi.rolling(n).min(), rsi.rolling(n).max()
    stoch = (100 * (rsi - lo_r) / (hi_r - lo_r)).where(hi_r != lo_r)
    sar = _sar_pine(bars_df, p["sar_start"], p["sar_inc"], p["sar_max"])
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lsma = _linreg(c, int(p["lsma_len"])).shift(int(p["lsma_offset"]))
    up = (c > sar) & (c.shift(1) <= sar.shift(1))
    dn = (c < sar) & (c.shift(1) >= sar.shift(1))
    long_e = (up & (rsi > p["rsi_os"]) & (macd > sig) & (stoch > p["stoch_os"]) & (c > lsma)).astype(bool)
    short_e = (dn & (rsi < p["rsi_ob"]) & (macd < sig) & (stoch < p["stoch_ob"]) & (c < lsma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
