"""EMA 9 / 21 crossings with an RSI filter, 1-hour bars: the cross up with the RSI under 70 goes long, the cross down with the RSI over 30 goes short, each with a 1.5 % target and 1 % stop; reversing.
Port of FMZ strategy #472934 "双均线RSI交叉动态止盈止损量化策略-Dual-EMA-RSI-Crossover-Strategy-with-Dynamic-Take-Profit-Stop-Loss" (Estrategia BTC/USDT - Ajustada).

FMZ source id: 472934

Source
    https://www.fmz.com/strategy/472934 (PineScript v5, FMZ last modified 2024-11-25 11:01:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-128), EMA 9 / 21; RSI 14; target 1.5 %, stop 1 % of the signal close
    crossover(ema9, ema21) and rsi < 70 -> entry Compra + exit(limit = close x 1.015, stop = close x 0.99);  crossunder and rsi > 30 -> entry Venta + exit (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once on the signal bar from its close: ported as the fixed fractions 0.015 /
      0.01 of the fill. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, EMA crossings with an RSI filter and a percent bracket.
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

NAME = "fmz_472934_ema9_21_cross_rsi_filter_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
    "tp_pct": [0.015, 0.03],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "tp_pct": 0.015, "sl_pct": 0.01, "rsi_len": 14}


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
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
