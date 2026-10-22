"""RSI 14 crossings of 30 / 70 with close tests, 4-hour bars: the RSI crossing over 30 goes long, under 70 short, reversing; a long closes on the RSI crossing over 70, the close crossing over a level 3 %
under the close, or a one-bar rise above 0.2 price units; a short mirrors it.
Port of FMZ strategy #441010 "动态RSI指标交易策略Dynamic-RSI-Trading-Strategy" (Modified RSI-Based Trading Strategy).

FMZ source id: 441010

Source
    https://www.fmz.com/strategy/441010 (PineScript v5, FMZ last modified 2024-02-04 17:36:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-182), RSI 14; levels 70 / 30 (fixed); trailing 3 %; profit target 20 (used as 20 / 100 = 0.2 in price units)
    trailingStopLevel (var) = close (1 - 3 %) while long, close (1 + 3 %) while short, kept while flat
    crossover(rsi, 30) -> entry Buy;  crossover(rsi, 70) or crossover(close, trailingStopLevel) or change(close) > 0.2 -> close Buy
    crossunder(rsi, 70) -> entry Sell;  crossunder(rsi, 30) or crossunder(close, trailingStopLevel) or change(close) < -0.2 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing" level is rebuilt from each bar's own close while in a position, so its crossings can
      only fire on a bar where the level was last set on the other side (or never set), as written. The
      profit test compares the one-bar change of the close in price units with 20 / 100 = 0.2: as a
      fraction of the close at the BTC 42000 reading, 0.2 / 42000 = 4.762e-06 (so nearly any rise closes a
      long, as written). A close acts only on the held position; a close written after a reversing entry
      leaves the reversal standing (as #438020). REVERSAL INTENDED. No sizing code. FREQ = "4h" from the
      backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit change test -> fraction of the close.
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

NAME = "fmz_441010_rsi_30_70_cross_close_level_exits"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 9],
    "trail_pct": [3, 5],
}
DEFAULT_PARAMS = {"rsi_length": 14, "trail_pct": 3, "change_frac": 4.762e-06, "overbought": 70, "oversold": 30}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    ob, os_ = float(p["overbought"]), float(p["oversold"])
    el = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    es = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    xl = ((r > ob) & (r.shift(1) <= ob)).to_numpy()
    xs = ((r < os_) & (r.shift(1) >= os_)).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp = float(p["trail_pct"]) / 100
    fr = float(p["change_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, tsl = 0, np.nan
    for i in range(m):
        prev_tsl = tsl
        if held == 1:
            tsl = cv[i] * (1 - tp)
        elif held == -1:
            tsl = cv[i] * (1 + tp)
        cp = cv[i - 1] if i > 0 else np.nan
        ch = cv[i] - cp
        xo = cv[i] > tsl and cp <= prev_tsl
        xu = cv[i] < tsl and cp >= prev_tsl
        new = held
        if el[i] and new != 1:
            new = 1
        if (xl[i] or xo or ch > fr * cv[i]) and held == 1 and new == 1:
            new = 0
        if es[i] and new != -1:
            new = -1
        if (xs[i] or xu or ch < -fr * cv[i]) and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
