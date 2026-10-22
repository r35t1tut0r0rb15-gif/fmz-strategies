"""Bull and bear traps on a 5-bar range, broker days: a break above the previous 5-bar high that dips one ATR(5) back under the EMA 21 goes short, the mirror goes long; a target 80 % of the 5-bar range from
the signal close; reversing.
Port of FMZ strategy #442341 "EMA Breakthrough Trap Strategy" (Bull and Bear Trap Strategy with EMA 21 - 1min Chart).

FMZ source id: 442341

Source
    https://www.fmz.com/strategy/442341 (PineScript v5, FMZ last modified 2024-02-21 11:29:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-154), length 5; ATR multiplier 1; EMA 21; target 80 % of the range (limit only)
    bullTrap = close > highest(high, 5)[1] and low <= highest(high, 5) - atr(5) and close < ema21 -> entry Short, exit(limit = close - 0.8 (high5 - low5))
    bearTrap = close < lowest(low, 5)[1] and high >= lowest(low, 5) + atr(5) and close > ema21 -> entry Long, exit(limit = close + 0.8 (high5 - low5))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is set on the signal bar from its close: tp = 0.8 (5-bar high - 5-bar low) / close,
      shifted one bar inside stops() and re-based on the fill; there is no stop. A later trap while held
      moves the script's target, which the port does not follow. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry from signal-bar data.
    2 generic: PASS, trap tests and a range target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442341_bull_bear_trap_range_target_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [5, 10],
    "ema_length": [21, 50],
}
DEFAULT_PARAMS = {"length": 5, "ema_length": 21, "atr_mult": 1.0, "target_share": 0.8}


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


def _tp(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    return float(p["target_share"]) * (h.rolling(n).max() - lo.rolling(n).min()) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n) * float(p["atr_mult"])
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    bull_trap = ((c > hh.shift(1)) & (lo <= hh - atr) & (c < e)).to_numpy()
    bear_trap = ((c < ll.shift(1)) & (h >= ll + atr) & (c > e)).to_numpy()
    tp = _tp(bars_df, p).to_numpy()
    ov, hv, lv = bars_df["open"].to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and hv[i] >= x * (1 + t_):
                pos = 0
            elif pos == -1 and lv[i] <= x * (1 - t_):
                pos = 0
        if i + 1 < m and not np.isnan(tp[i]):
            if bull_trap[i] and pos != -1:
                se[i], pos, entry_i, t_ = True, -1, i + 1, tp[i]
            elif bear_trap[i] and pos != 1:
                le[i], pos, entry_i, t_ = True, 1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": _tp(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
