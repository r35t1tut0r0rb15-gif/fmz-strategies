"""EMA 5 crossing over the EMA 200, broker days, long only: the long takes a 5 % target from its entry price; the stop 2 ATR under the latest close is re-sent every bar (pending), and the loop closes the trade on the bar that touches it.
Port of FMZ strategy #482774 "EMA交叉趋势追踪与ATR动态止损优化策略-EMA-Cross-Over-Trend-Following-Strategy-with-ATR-Dynamic-Stop-Loss-Optimization" (EMA5 Cross-Up EMA200 ATR Stop).

FMZ source id: 482774

Source
    https://www.fmz.com/strategy/482774 (PineScript v6, FMZ last modified 2025-02-27 17:51:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-158), EMA 5 / 200; ATR 14 x 2.0 stop from each close; take-profit 5 % of the avg price; 100 % of equity; capital 100000
    crossover(ema5, ema200) -> entry Long
    every bar: exit(stop = close - 2 atr, limit = avg x 1.05 while long, else na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a fixed 5 % of the entry price: a scalar fraction active from the fill (as #440797;
      the source sends it from the bar after the fill). The stop is re-sent on every bar from that bar's
      close: stops() cannot express a level re-set every bar, so it is kept pending (as #438034, mark
      trailing_stop_pending); since it is the only other exit, the loop follows the level sent at the bar
      before on each bar's low (as #449508) and sends the close at that bar's close (one bar late, not at
      the level). A crossing while the long is held is ignored. Long only. Stop module: portfolio_kwargs
      {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 100 % of equity size and capital are
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent target from the fill; re-sent ATR stop followed in the loop (pending).
    2 generic: PASS, EMA 5 / 200 crossings with an ATR stop and a percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482774_ema5_200_cross_resent_atr2_stop_tp5_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 3.0],
    "take_profit_perc": [5.0, 10.0],
}
DEFAULT_PARAMS = {"atr_mult": 2.0, "take_profit_perc": 5.0, "ema_fast": 5, "ema_slow": 200, "atr_period": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    stop = (c - _atr(bars_df, int(p["atr_period"])) * float(p["atr_mult"])).to_numpy(dtype=float)
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp = float(p["take_profit_perc"]) / 100
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos, avg = 1, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        hit = False
        if pos == 1 and hv[i] >= avg * (1 + tp):
            pos = 0                               # the target fills inside this bar (stop module)
        elif pos == 1 and i > 0 and lv[i] <= stop[i - 1]:
            hit = True                            # the stop re-sent at the bar before is touched
        if hit:
            lx[i], pend = True, 2                 # closed at this bar's close (one bar late)
        elif pos == 0 and up[i]:
            le[i], pend = True, 1
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["take_profit_perc"]) / 100}


def portfolio_kwargs(**params):
    return {}
