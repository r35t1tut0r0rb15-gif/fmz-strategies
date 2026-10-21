"""MACD signal crossings on the far side of zero with an EMA 200 trend test and an EMA bracket, broker days: a MACD crossing over its signal below zero with the close above the EMA 200 goes long (from flat or
short), stopped at the EMA 200 with a target twice that distance; a crossing under above zero with the close under the EMA goes short from flat only, with the mirror bracket.
Port of FMZ strategy #436876 "MACD和EMA金叉死叉策略MACD-and-EMA-Crossover-Strategy" (MACD & EMA 200 Strategy).

FMZ source id: 436876

Source
    https://www.fmz.com/strategy/436876 (PineScript v5, FMZ last modified 2023-12-28 15:22:14).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 108-133), MACD 12 / 26 / 9, EMA 200; stop at the EMA, target 2x the EMA distance
    long = crossover(macd, signal) and macd < 0 and close > ema200 and position_size <= 0 -> entry Long, exit(stop = ema200, limit = close + 2 (close - ema200))
    short = crossunder(macd, signal) and macd > 0 and close < ema200 and position_size <= 0 -> entry Short, exit(stop = ema200, limit = close - 2 (ema200 - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket levels are the signal bar's EMA 200 and its doubled distance, re-expressed as distances
      from the signal close (sl_stop / tp_stop fractions), shifted one bar inside stops() and re-based on
      the fill. Both entries test position_size <= 0, so a long may reverse a short but a short is only
      entered from flat; "flat" and "long" follow the house bracket (the loop marks a trade closed once a
      bar's low / high reaches its stop or target from the fill price). REVERSAL INTENDED (longs reverse
      shorts). Stop module: portfolio_kwargs {} (driver D4). No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA-distance bracket.
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

NAME = "fmz_436876_macd_zero_side_ema_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [12, 8],
    "ema_len": [200, 100],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "ema_len": 200, "tp_mult": 2.0}


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


def _setup(bars_df, p):
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    lc = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0) & (c > ema)
    sc = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (macd > 0) & (c < ema)
    d_l = (c - ema) / c
    d_s = (ema - c) / c
    k = float(p["tp_mult"])
    sl = pd.Series(np.where(lc, d_l, np.where(sc, d_s, np.nan)), index=c.index)
    tp = pd.Series(np.where(lc, k * d_l, np.where(sc, k * d_s, np.nan)), index=c.index)
    return lc, sc, sl.where(sl > 0), tp.where(tp > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, sc, sl, tp = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    el, es, slv, tpv = lc.to_numpy(), sc.to_numpy(), sl.to_numpy(), tp.to_numpy()
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, f_sl, f_tp = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - f_sl) or hv[i] >= e * (1 + f_tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + f_sl) or lv[i] <= e * (1 - f_tp)):
                pos = 0
        if i + 1 >= m or np.isnan(slv[i]):
            continue
        if el[i] and pos <= 0:
            le[i] = True
            pos, entry_i, f_sl, f_tp = 1, i + 1, slv[i], tpv[i]
        elif es[i] and pos == 0:
            se[i] = True
            pos, entry_i, f_sl, f_tp = -1, i + 1, slv[i], tpv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
