"""Standard-deviation band re-entries with RSI extremes, 1-hour bars: the close crossing back over SMA 20 - 1.5 SD with the RSI 14 under 30 goes long, back under SMA + 1.5 SD with the RSI over 70 goes short; the long closes on the close crossing under SMA - 0.5 SD or an RSI over 70, the short mirrored; reversing.
Port of FMZ strategy #452691 "基于相对强弱指数RSI和滑动平均SMA的波动率标准差DEV交易策略-Standard-Deviation-DEV-Trading-Strategy-Based-on-Relative-Strength-Index-RSI-and-Simple-Moving-Average-SMA" (Estratégia de Desvio Padrão com RSI).

FMZ source id: 452691

Source
    https://www.fmz.com/strategy/452691 (PineScript v5, FMZ last modified 2024-05-28 10:57:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-164), SMA 20 +- 1.5 / 0.5 SD; RSI 14, levels 70 / 30; margins 100 / 100
    crossover(close, sma - 1.5 sd) and rsi < 30 -> entry Long;  crossunder(close, sma + 1.5 sd) and rsi > 70 -> entry Short
    crossunder(close, sma - 0.5 sd) or rsi > 70 -> close Long;  crossover(close, sma + 0.5 sd) or rsi < 30 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; an opposite entry reverses and the close then finds
      the trade reversed (a long entry always meets the short's RSI < 30 close, which therefore never
      cancels it); a close acts only on the trade held into the bar. REVERSAL INTENDED. The margin
      settings are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SD-band re-entries with RSI extremes.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452691_sd_band_reentry_rsi_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "entry_sd": [1.5, 2.0],
    "exit_sd": [0.5, 0.0],
}
DEFAULT_PARAMS = {"length": 20, "entry_sd": 1.5, "exit_sd": 0.5, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    sma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    ob, os_ = float(p["ob"]), float(p["os"])
    c1 = c.shift(1)

    def over(x):
        return (c > x) & (c1 <= x.shift(1))

    def under(x):
        return (c < x) & (c1 >= x.shift(1))

    ke, kx = float(p["entry_sd"]), float(p["exit_sd"])
    el = (over(sma - ke * sd) & (r < os_)).to_numpy()
    es = (under(sma + ke * sd) & (r > ob)).to_numpy()
    xl = (under(sma - kx * sd) | (r > ob)).to_numpy()
    xs = (over(sma + kx * sd) | (r < os_)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
