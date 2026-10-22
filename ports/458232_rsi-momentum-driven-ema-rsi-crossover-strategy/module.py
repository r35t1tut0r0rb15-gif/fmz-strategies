"""Close crossings of the EMA 450 with RSI 14 momentum, 1-minute bars, long only: the close crossing over the EMA with the RSI over 67 buys; an RSI over 80 sells.
Port of FMZ strategy #458232 "动量驱动型均线-RSI交叉策略-Momentum-Driven-EMA-RSI-Crossover-Strategy" (EMA RSI Momentum Strategy TF5min).

FMZ source id: 458232

Source
    https://www.fmz.com/strategy/458232 (PineScript v5, FMZ last modified 2024-07-31 10:31:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-177), EMA 450; RSI 14, buy over 67, sell over 80
    crossover(close, ema450) and rsi > 67 -> entry Buy;  rsi > 80 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is called before the close; the close acts only on a long held into the bar. The title
      and comment name a 5-minute chart, but the backtest header runs 1-minute bars; the header is
      followed. Long only. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, long-EMA crossings with RSI momentum.
    3 crypto-exchange-only: no (exchange pair in the header only (RNDRUSDT named in a comment)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458232_close_cross_ema450_rsi67_exit_rsi80_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [450, 200],
    "buy_th": [67, 60],
    "sell_th": [80, 75],
}
DEFAULT_PARAMS = {"ema_len": 450, "buy_th": 67, "sell_th": 80, "rsi_len": 14}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    buy = ((c > e) & (c.shift(1) <= e.shift(1)) & (r > float(p["buy_th"]))).to_numpy()
    sell = (r > float(p["sell_th"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif sell[i] and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
