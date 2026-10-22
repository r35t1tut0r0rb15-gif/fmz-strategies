"""RSI 14 extremes in the SMA 10 / 50 trend, 5-minute bars: an RSI under 30 with the SMA 10 over the SMA 50 goes long, an RSI over 70 with the SMA 10 under goes short; a long closes on an RSI over 70, a short on an RSI under 30; reversing.
Port of FMZ strategy #471688 "双均线RSI趋势动量策略-Dual-Moving-Average-RSI-Trend-Momentum-Strategy" (Super Advanced Strategy).

FMZ source id: 471688

Source
    https://www.fmz.com/strategy/471688 (PineScript v5, FMZ last modified 2024-11-12 14:34:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-146), SMA 10 / 50; RSI 14, levels 30 / 70
    sma10 > sma50 and rsi < 30 -> entry Compra;  sma10 < sma50 and rsi > 70 -> entry Venda;  rsi > 70 -> close Compra;  rsi < 30 -> close Venda

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; a close acts only on a position held into the bar and
      not being reversed (#437773). REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI extremes with the SMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_471688_rsi_extreme_with_sma10_50_trend_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 20],
    "long_len": [50, 100],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 50, "rsi_len": 14}


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
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    lo_r, hi_r = (r < 30).to_numpy(), (r > 70).to_numpy()
    up, dn = (s > l).to_numpy(), (s < l).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if up[i] and lo_r[i]:
            cur = 1
        if dn[i] and hi_r[i]:
            cur = -1
        if hi_r[i] and pos == 1 and cur == 1:
            cur = 0                              # the close acts only on a long held, not reversed
        if lo_r[i] and pos == -1 and cur == -1:
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
