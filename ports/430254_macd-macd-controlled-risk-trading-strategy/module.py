"""MACD cross below zero above a WMA 150, broker days, long only from flat: within 5 bars of a MACD / signal cross-up, with
both lines under zero and the close above the WMA 150, go long with a stop at the prior 3-bar low and a target 4 R
above the close.
Port of FMZ strategy #430254 "基于MACD指标的止损策略MACD-Controlled-Risk-Trading-Strategy" (McDonalds).

FMZ source id: 430254

Source
    https://www.fmz.com/strategy/430254 (PineScript v4, FMZ last modified 2023-10-26 15:51:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 118-158), MACD 12 / 26 / 9, WMA 150, stop = lowest(low, 3)[1], target 4 R
    golong = barssince(crossover(macd, signal)) <= 5 and macd < 0 and signal < 0 and close > wma(close, 150)
             and strategy.opentrades == 0
    stop = lowest(low, 3)[1]; tp = close + 4 x (close - stop)
    golong -> entry long; exit(stop = stop, limit = tp)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the signal bar: stop distance (close - stop) / close, target 4 times it,
      as fractions of the signal close shifted one bar (re-based on the fill). A signal whose stop is
      not below the close (no risk) places no entry.
    * Entries only from flat (opentrades == 0): "flat" follows the house bracket on bars (a stop or
      target touched on a bar frees the next signal from that bar on). Opposite entries cannot
      occur. Long only.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, MACD signs, a moving average and a risk-multiple target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 % risk sizing stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430254_macd_below_zero_wma_bracket_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "wma_length": [150, 100],
    "r_exit": [4.0, 2.0],
}
DEFAULT_PARAMS = {"wma_length": 150, "r_exit": 4.0, "fast": 12, "slow": 26, "signal": 9, "window": 5, "low_len": 3}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _setup(bars_df, p):
    c, lo = bars_df["close"], bars_df["low"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    xo = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    since = np.full(len(c), np.inf)
    last = -1
    for i in range(len(c)):
        if xo[i]:
            last = i
        if last >= 0:
            since[i] = i - last
    cond = (since <= int(p["window"])) & (macd < 0).to_numpy() & (sig < 0).to_numpy() & \
        (c > _wma(c, int(p["wma_length"]))).to_numpy()
    stop = lo.rolling(int(p["low_len"])).min().shift(1)
    sl_frac = ((c - stop) / c).to_numpy()
    return cond, sl_frac, sl_frac * float(p["r_exit"])


def _run(bars_df, p):
    buy, sl_f, tp_f = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_):
                pos = 0
        if pos == 0 and buy[i] and sl_f[i] > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_f[i], tp_f[i]
            sl_arr[i], tp_arr[i] = s_, t_
    return le, sl_arr, tp_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
