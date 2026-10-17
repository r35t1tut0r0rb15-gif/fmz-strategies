"""UT Bot on Heikin Ashi closes with a T3 filter for the bracket, broker days: the HA close crossing above its ATR trailing
line goes long, below goes short; a bracket of 1 ATR 50 (target at 1:1) is set from the HA close when the close is on
the T3's far side, and kept until the next such setup.
Port of FMZ strategy #431431 "基于T3移动平均线和ATR的交易策略Volatility-Adjusted-Moving-Average-Trading-Strategy" (UT Bot Alerts (QuantNomad) Strategy w/ NinjaView).

FMZ source id: 431431

Source
    https://www.fmz.com/strategy/431431 (PineScript v5, FMZ last modified 2023-11-07 17:18:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 201-302), T3 100, key 1, ATR 50, HA signals on, R:R 1
    src = Heikin Ashi close; UT trailing line of src with nLoss = 1 x ATR(50); buy = src > line and crossover(src, line)
    buy and close < T3 -> long levels: SL = src - nLoss, TP = src + nLoss (short levels cleared); mirror for sell and close > T3
    buy -> entry long;  sell -> entry short;  exit(stop, limit) every bar with the current levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi close of the chart's own timeframe is ohlc4. ATR is Pine's (Wilder, SMA seed).
    * The bracket uses the levels held when the entry is taken (possibly from an earlier setup, or
      none if the last setup was the other side), as fractions of the entry fill (the open after the
      signal, known at that open); a level already passed at that open exits at once. A new setup while
      in the position moves the levels (re-issued exit): rule 2, mark trailing_stop_pending, not
      emitted.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; levels fixed at entry (rule 2).
    2 generic: PASS, ATR trailing line, a T3 filter and ATR brackets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 in the alert text only; no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG431431 (3 members, best partner #442400, Jaccard 0.829); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431431_ut_bot_t3_bracket"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "key": [1.0, 2.0],
    "t3_len": [100, 50],
}
DEFAULT_PARAMS = {"key": 1.0, "t3_len": 100, "atr_len": 50, "rr": 1.0}


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
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    L = int(p["t3_len"])
    e = [c]
    for _ in range(6):
        e.append(e[-1].ewm(span=L, adjust=False).mean())
    b = 0.7
    t3 = ((-b ** 3) * e[6] + (3 * b * b + 3 * b ** 3) * e[5] + (-6 * b * b - 3 * b - 3 * b ** 3) * e[4]
          + (1 + 3 * b + b ** 3 + 3 * b * b) * e[3]).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    nl = _rma(tr, int(p["atr_len"])) * float(p["key"])
    src = ((o + h + lo + c) / 4).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.zeros(m)
    prev = 0.0
    for i in range(m):
        s1 = src[i - 1] if i else np.nan
        if src[i] > prev and s1 > prev:
            v = max(prev, src[i] - nl[i])
        elif src[i] < prev and s1 < prev:
            v = min(prev, src[i] + nl[i])
        else:
            v = src[i] - nl[i] if src[i] > prev else src[i] + nl[i]
        line[i] = v
        prev = 0.0 if np.isnan(v) else v
    l1 = np.concatenate(([np.nan], line[:-1]))
    s1a = np.concatenate(([np.nan], src[:-1]))
    buy = (src > line) & (s1a <= l1)
    sell = (src < line) & (s1a >= l1)
    rr = float(p["rr"])
    sl_l = tp_l = sl_s = tp_s = np.nan
    sl_lvl, tp_lvl = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if buy[i] and cv[i] < t3[i]:
            sl_l, tp_l, sl_s, tp_s = src[i] - nl[i], src[i] + nl[i] * rr, np.nan, np.nan
        if sell[i] and cv[i] > t3[i]:
            sl_s, tp_s, sl_l, tp_l = src[i] + nl[i], src[i] - nl[i] * rr, np.nan, np.nan
        if buy[i]:
            sl_lvl[i], tp_lvl[i] = sl_l, tp_l
        elif sell[i]:
            sl_lvl[i], tp_lvl[i] = sl_s, tp_s
    return buy, sell, sl_lvl, tp_lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(buy & ~sell, index=idx), false, pd.Series(sell, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, sl_lvl, tp_lvl = _run(bars_df, p)
    idx = bars_df.index
    o = bars_df["open"]
    side = pd.Series(np.where(buy, 1.0, np.where(sell, -1.0, np.nan)), index=idx).shift(1)
    sl = pd.Series(sl_lvl, index=idx).shift(1)
    tp = pd.Series(tp_lvl, index=idx).shift(1)
    sl_f = ((o - sl) / o * side).clip(lower=1e-9)       # a level already passed exits at once
    tp_f = ((tp - o) / o * side).clip(lower=1e-9)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
