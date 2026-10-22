"""Previous-day range breaks, daily bars, entries only from flat: a close over the previous day's high buys, a close under its low sells, each with a 50-point stop and target from the signal close (fractions of 42000).
Port of FMZ strategy #474679 "Daily Range Breakout Single Direction Trading Strategy" (US 30 Daily Breakout Strategy (Single Trade Per Breakout/Breakdown, New York Time)).

FMZ source id: 474679

Source
    https://www.fmz.com/strategy/474679 (PineScript v5, FMZ last modified 2024-12-11 15:23:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-140), pip 1 point; target / stop 50 points from the signal close; 100 % of equity; trim_orders
    close > security("D", high[1]) and no open trade and not breakout_traded -> entry Long, exit(limit = close + 50, stop = close - 50), breakout_traded := true;  short mirror on the previous low;  change(time("D")) -> flags reset

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily chart the "D" request is the chart, so the levels are the previous broker day's high
      and low; time("D") changes on every bar, so the once-per-day flags reset before every test and feed
      nothing. The 50 points are price amounts, ported as fractions of 42000 of the signal close
      (0.00119). Entries only from flat: a loop follows each trade's bracket on the bar's high / low so
      the flat gate lines up (as 449508); the levels are sent as fractions of the fill open (a level at
      or through it is marketable and closed one bar late). Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The equity share is
      not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of the signal close.
    2 generic: PASS, previous-day range breaks with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474679_prev_day_range_break_point_bracket_from_flat"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.00119, 0.0119],
    "tp_frac": [0.00119, 0.0119],
}
DEFAULT_PARAMS = {"sl_frac": 0.00119, "tp_frac": 0.00119}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lc = (c > h.shift(1)).to_numpy()
    sc = (c < lo.shift(1)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    slf, tpf = float(p["sl_frac"]), float(p["tp_frac"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, sl, tp = 0, 0, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, sl, tp = 0, np.nan, np.nan      # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, sl, tp = 0, np.nan, np.nan
        if pend != 0 or pos != 0:
            continue
        if lc[i]:
            sl_n, tp_n = cv[i] * (1 - slf), cv[i] * (1 + tpf)
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            sl_n, tp_n = cv[i] * (1 + slf), cv[i] * (1 - tpf)
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
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
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
