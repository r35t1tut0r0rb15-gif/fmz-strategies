"""Two EMA chains on daily bars: chain 1 enters on closes crossing a weekly EMA 10 and exits on closes crossing the daily EMA 10; chain 2 enters on closes crossing a 12-hour EMA 9 and exits on closes crossing a 9-hour EMA 9; long and short, one position at a time, each close acting only on its own chain's trade; reversing.
Port of FMZ strategy #473411 "Dual Chain Hybrid Momentum EMA Tracking Trading System" (Dual Chain Strategy).

FMZ source id: 473411

Source
    https://www.fmz.com/strategy/473411 (PineScript v5, FMZ last modified 2024-11-29 17:04:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-239), chain 1: EMA 10, entry "W", exit "D"; chain 2: EMA 9, entry "720", exit "540"; both on; date window always true
    crossover(close, emaW) -> entry BUY_Chain_1;  crossunder -> entry SELL_Chain_1;  crossunder(close, emaD) -> close BUY_Chain_1;  crossover -> close SELL_Chain_1;  same for chain 2 with ema720 / ema540

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly request (higher than the chart, no lookahead) is the last completed broker week (as
      #437508): the EMA 10 of weekly closes of the previous broker week. "D" is the chart (a daily EMA 10).
      The 720- and 540-minute requests are LOWER than the chart: each returns the chart bar's last bar
      of that size (as #436765), counted from the broker day's start (the 540-minute day ends with a
      6-hour bar); the EMA 9 runs over those bars; all built in precompute. One position at a time
      (pyramiding 1): an entry on the side already held or ordered is ignored, an opposite entry
      reverses, the later call wins a bar, and a close acts only on its own id held into the bar and not
      reversed on it (#437773, 446232); a loop follows the held id. A close and a new same-side entry of
      the other chain on one bar continue the position. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed weekly values, last lower-time-frame bars.
    2 generic: PASS, multi-time-frame EMA crossing chains.
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

NAME = "fmz_473411_dual_chain_weekly_12h_ema_entries_daily_9h_exits"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [10, 20],
    "len2": [9, 18],
}
DEFAULT_PARAMS = {"len1": 10, "len2": 9, "entry2_minutes": 720, "exit2_minutes": 540}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _ltf_last(df, lab, minutes, n):
    """EMA n of `minutes`-bar closes counted from each broker day's start, on the day's last bar."""
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=int(minutes)))
    bc = df["close"].groupby([lab, blk]).last()
    ema = bc.ewm(span=int(n), adjust=False).mean()
    day = ema.index.get_level_values(0)
    last = ema[~day.duplicated(keep="last")]
    last.index = last.index.get_level_values(0)
    return last


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # weekly EMA of the previous (completed) broker week, labelled by its Monday
    day = pd.DatetimeIndex(bars.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    wk_ema = bars["close"].groupby(week).last().ewm(span=int(p["len1"]), adjust=False).mean()
    bars["ema_w"] = wk_ema.shift(1).reindex(week).to_numpy()
    bars["ema_e2"] = _ltf_last(df, lab, p["entry2_minutes"], p["len2"]).reindex(bars.index).to_numpy()
    bars["ema_x2"] = _ltf_last(df, lab, p["exit2_minutes"], p["len2"]).reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _x(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1, e2, x2 = bars_df["ema_w"], bars_df["ema_e2"], bars_df["ema_x2"]
    x1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    calls = [                                    # (signal, kind, side, chain) in the written order
        (_x(c, e1), "entry", 1, 1), (_x(e1, c), "entry", -1, 1),
        (_x(x1, c), "close", 1, 1), (_x(c, x1), "close", -1, 1),
        (_x(c, e2), "entry", 1, 2), (_x(e2, c), "entry", -1, 2),
        (_x(x2, c), "close", 1, 2), (_x(c, x2), "close", -1, 2),
    ]
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hs, hid = 0, 0
    for i in range(m):
        ns, nid = hs, hid
        for sig, kind, side, chain in calls:
            if not sig[i]:
                continue
            if kind == "entry":
                if ns != side:
                    ns, nid = side, chain
            elif (hs, hid) == (side, chain) and (ns, nid) == (hs, hid):
                ns, nid = 0, 0
        if ns != hs:
            if ns == 1:
                le[i] = True
            elif ns == -1:
                se[i] = True
            elif hs == 1:
                lx[i] = True
            else:
                sx[i] = True
        hs, hid = ns, nid
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
