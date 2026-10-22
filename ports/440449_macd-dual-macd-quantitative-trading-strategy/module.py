"""Weekly / daily MACD, broker days, long only: the weekly MACD crossing over its signal, or the daily MACD crossing over its signal while the weekly MACD is above its own, goes long from flat; the daily
MACD crossing under its signal closes; a 30 % target from the entry (the script's trailing stop on lows is pending).
Port of FMZ strategy #440449 "基于双MACD量化交易策略Dual-MACD-Quantitative-Trading-Strategy" (Dual Macd Tester).

FMZ source id: 440449

Source
    https://www.fmz.com/strategy/440449 (PineScript v4, FMZ last modified 2024-01-30 16:43:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 200-320), MACD 12 / 26 / 9 on D and W; target 30 % on, stop 1 % off, trailing stop 5 % on (source low); 20 % of equity; dates 2018-2021 (start_time fixed true)
    buy = crossover(w_macd, w_signal) and flat -> entry First Entry;  re-entry = crossover(d_macd, d_signal) and w_macd > w_signal and flat -> entry Further Entry;  crossunder(d_macd, d_signal) and in trade -> close both
    trailing_stop = in trade ? max(trailing_stop[1], low x 0.95) : 0;  strategy.exit(limit = avg price x 1.30, stop = trailing_stop) for both entries

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: the weekly MACD
      is that of the last completed broker week (weeks of broker days, Monday labels), built from the
      module's own bars; the daily request is the chart itself. The target is a fixed fraction: tp_stop
      0.30. The trailing stop ratchets on 95 % of the lows, which the house trail (best high or close)
      cannot express: not ported, mark trailing_stop_pending. Entries only from flat. Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. The 20 % of
      equity size, capital and commission are sizing and costs. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks; the low-based trail pending.
    2 generic: PASS, daily and weekly MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 20 % of equity, capital and commission settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); broker weeks for the weekly MACD.
Long only.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440449_dual_macd_weekly_window_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.30, 0.10],
    "sign_len": [9, 5],
}
DEFAULT_PARAMS = {"tp": 0.30, "sign_len": 9, "fast_len": 12, "slow_len": 26}


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


def _macd(x, p):
    m = x.ewm(span=int(p["fast_len"]), adjust=False).mean() - x.ewm(span=int(p["slow_len"]), adjust=False).mean()
    return m, m.ewm(span=int(p["sign_len"]), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.dayofweek, unit="D")          # broker week, Monday label
    wc = c.groupby(week).last()
    wm, ws = _macd(wc, p)
    wm = pd.Series(wm.shift(1).reindex(week).to_numpy(), index=c.index)   # last completed week
    ws = pd.Series(ws.shift(1).reindex(week).to_numpy(), index=c.index)
    dm, ds = _macd(c, p)
    buy = ((wm > ws) & (wm.shift(1) <= ws.shift(1))).to_numpy()
    re_in = ((dm > ds) & (dm.shift(1) <= ds.shift(1)) & (wm > ws)).to_numpy()
    sell = ((dm < ds) & (dm.shift(1) >= ds.shift(1))).to_numpy()
    t_ = float(p["tp"])
    ov, hv = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + t_):
            pos = 0
        if pos == 1 and i >= entry_i and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and (buy[i] or re_in[i]) and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
