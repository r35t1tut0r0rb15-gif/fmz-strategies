"""SMA 10 / 30 crossings, 2-day bars: the cross up goes long, the cross down closes the long and goes short; reversing. The long's 1 % stop and 2 % target are set from strategy.position_avg_price on the signal bar (na from flat, the replaced short's price on a reversal), as written; the short has no exit.
Port of FMZ strategy #473365 "Dual Moving Average Crossover Adaptive Parameter Trading Strategy" (Two Moving Averages Strategy with Adjustable Parameters).

FMZ source id: 473365

Source
    https://www.fmz.com/strategy/473365 (PineScript v5, FMZ last modified 2024-11-29 15:29:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-128), SMA 10 / 30; stop 1 %, target 2 % of avg on the signal bar; trail_offset 1.5 (no trail_points)
    crossover(fastMA, slowMA) -> sl := avg x 0.99, tp := avg x 1.02, entry Long;  long: exit(stop = sl, limit = tp, trail_offset = 1.5);  crossunder -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on the signal bar from strategy.position_avg_price, which is na from flat
      (no bracket) and the replaced short's fill price on a reversal, as written (as #468309, #473147);
      the exit re-sent while long keeps those stored levels. trail_offset without trail_points sets no
      trail (as #441084). The loop tracks the fill prices and the bracket inside each bar; the levels
      are sent as fractions of the long's fill open (a level at or through it is marketable and closed
      one bar late). Crossings alternate, so no repeat signal re-sets the levels. The short ends only
      at the next long entry. Same bracket rules as #473353 (same author), on SMA crossings. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-day bars: mark coarse_bar_stop.
      No sizing code. FREQ = "2D" from the backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, SMA crossings with a long bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (16 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473365_sma10_30_cross_reversal_long_bracket_from_replaced_avg"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [30, 60],
    "sl_pct": [0.01, 0.02],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "sl_pct": 0.01, "tp_pct": 0.02, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    a, b = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    lc = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    sc = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    slp, tpp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, sl, tp = pend, 0, ov[i], sl_n, tp_n
            if pos == 1 and (sl >= ov[i] or tp <= ov[i]):   # a level through the fill: closed at the next open
                lx[i], pend, sl, tp = True, 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, avg, sl, tp = 0, 0, np.nan, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan     # the bracket fills inside this bar
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = np.nan, np.nan                      # the short has no exit
            se[i], pend, side[i] = True, -1, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0)
    tp_f = (tp_l / o - 1).where(sd > 0)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
