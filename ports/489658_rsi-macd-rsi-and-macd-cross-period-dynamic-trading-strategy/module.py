"""MACD crosses at RSI extremes with a 2 % / 5 % bracket, 15-minute bars: a MACD cross up while RSI 14 is below 30
goes long; a cross down while RSI is above 70 goes short; each trade has a 2 % stop and a 5 % target.
Port of FMZ strategy #489658 "RSI与MACD交叉多周期动态交易策略-RSI-and-MACD-Cross-Period-Dynamic-Trading-Strategy" (RSI + MACD Strategy (15min)).

FMZ source id: 489658

Source
    https://www.fmz.com/strategy/489658 (PineScript v6, FMZ last modified 2025-04-07 13:50:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 207-235), RSI 14 (30 / 70), MACD 12 / 26 / 9, TP 5 %, SL 2 %
    long = rsi < 30 and crossover(macd, signal);  short = rsi > 70 and crossunder(macd, signal)
    on entry: exit(limit = close x (1 +- 5 %), stop = close x (1 -+ 2 %)), levels from the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop 2 %, tp_stop 5 % of the fill (scalars, house rule).
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, oscillators and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489658_macd_cross_rsi_extreme_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_oversold": [30, 40],
    "sl_pct": [2.0, 1.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_overbought": 70, "rsi_oversold": 30, "tp_pct": 5.0, "sl_pct": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    long_e = ((rsi < p["rsi_oversold"]) & up).astype(bool)
    short_e = ((rsi > p["rsi_overbought"]) & dn).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
