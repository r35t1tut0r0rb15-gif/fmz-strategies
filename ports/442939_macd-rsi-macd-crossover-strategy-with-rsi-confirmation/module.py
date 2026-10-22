"""MACD(12, 26, 9) crossings after the RSI 14 has once crossed 50, daily bars: a MACD cross up (once the RSI has ever crossed over 50) goes long, a cross down (once it has ever crossed under) goes short;
three bars after the latest cross the position closes; reversing.
Port of FMZ strategy #442939 "基于MACD与RSI结合的交叉策略MACD-Crossover-Strategy-with-RSI-Confirmation" (MACD Crossover Strategy with RSI Confirmation).

FMZ source id: 442939

Source
    https://www.fmz.com/strategy/442939 (PineScript v5, FMZ last modified 2024-02-27 15:07:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-240), MACD 12 / 26 / 9; RSI 14; exit after 3 bars
    above_50 / below_50 latch true at the first RSI crossing over / under 50 (never reset);  bullish_cross and above_50 -> entry Buy;  bearish_cross and below_50 -> entry Sell
    barssince(bullish_cross) >= 3 -> close Buy;  barssince(bearish_cross) >= 3 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two RSI flags are never reset, so once both crossings have happened the entries are plain
      MACD crossings, as written. Each close acts only on a held position; a close after a reversing
      entry leaves the reversal standing. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings with latched RSI flags; bar-count exits.
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

NAME = "fmz_442939_macd_cross_rsi50_latch_three_bar_exit"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "exit_after_bars": [3, 6],
    "fast_length": [12, 8],
}
DEFAULT_PARAMS = {"exit_after_bars": 3, "fast_length": 12, "slow_length": 26, "signal": 9, "rsi_length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast_length"]), adjust=False).mean() - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    bu = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    be = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    r = _rsi(c, int(p["rsi_length"]))
    r_up = ((r > 50) & (r.shift(1) <= 50)).to_numpy()
    r_dn = ((r < 50) & (r.shift(1) >= 50)).to_numpy()
    k = int(p["exit_after_bars"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held, a50, b50, lb, ls = 0, False, False, -1, -1
    for i in range(m):
        a50 = a50 or r_up[i]
        b50 = b50 or r_dn[i]
        if bu[i]:
            lb = i
        if be[i]:
            ls = i
        new = held
        if bu[i] and a50 and new != 1:
            new = 1
        if be[i] and b50 and new != -1:
            new = -1
        if lb >= 0 and i - lb >= k and held == 1 and new == 1:
            new = 0
        if ls >= 0 and i - ls >= k and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
