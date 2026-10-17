"""MACD histogram zero-line crosses with fixed histogram exit levels, broker days: the MACD (12 / 26, signal 20)
histogram crossing above zero goes long, below zero goes short; a long closes when the histogram crosses above its
upper exit level, a short when it crosses below the lower one (levels as ATR multiples).
Port of FMZ strategy #483794 "多指标动量波浪交易策略-Multi-Indicator-Momentum-Wave-Trading-Strategy" (Neon Momentum Waves Strategy).

FMZ source id: 483794

Source
    https://www.fmz.com/strategy/483794 (PineScript v5, FMZ last modified 2025-02-26 10:30:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 277-328), MACD 12 / 26 / 20, entry level 0, exit levels +11 / -9
    crossover(hist, 0) -> entry long;  crossunder(hist, 0) -> entry short
    position > 0 and crossover(hist, 11) -> close long;  position < 0 and crossunder(hist, -9) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the histogram is in price units, so +11 / -9 are price levels: on the author's daily ETH_USDT (daily
      ATR about 120) they are about +0.09 / -0.075 Wilder ATR(14) (judgement before any backtest): the exit levels are
      long_exit_atr x ATR and -short_exit_atr x ATR of the bar.
    * The closes test the position held at the bar's start and never undo an entry on that bar (#430850); entries
      reverse (REVERSAL INTENDED).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit histogram levels -> ATR multiples; MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483794_macd_hist_zero_cross_levels"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_exit_atr": [0.09, 0.3],
    "signal_length": [20, 9],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal_length": 20, "long_exit_atr": 0.09, "short_exit_atr": 0.075,
                  "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal_length"]), adjust=False).mean()
    atr = _atr(bars_df, int(p["atr_len"]))
    up_lvl, dn_lvl = p["long_exit_atr"] * atr, -p["short_exit_atr"] * atr
    h1 = hist.shift(1)
    go_l = ((hist > 0) & (h1 <= 0)).to_numpy()
    go_s = ((hist < 0) & (h1 >= 0)).to_numpy()
    out_l = ((hist > up_lvl) & (h1 <= up_lvl.shift(1))).to_numpy()
    out_s = ((hist < dn_lvl) & (h1 >= dn_lvl.shift(1))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
