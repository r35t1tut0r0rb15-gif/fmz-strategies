"""SMA 20 / 50 crossings on the SMA 200 side, 2-day bars: the cross up above the SMA 200 goes long, the cross down below it goes short; any opposite crossing closes; a 2 % / 4 % bracket exists only on a reversal, from the replaced position's price; reversing.
Port of FMZ strategy #481350 "Triple Moving Average Momentum Trend Trading Strategy" (Oliver Valez Triple MA Strategy).

FMZ source id: 481350

Source
    https://www.fmz.com/strategy/481350 (PineScript v5, FMZ last modified 2025-02-10 14:37:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-151), SMA 20 / 50 / 200 (EMA off); stop 2 %, target 4 % of strategy.position_avg_price (long formulas for both sides)
    crossover(sma20, sma50) and close > sma200 -> entry Long + exit(stop = avg x 0.98, limit = avg x 1.04);  crossunder and close < sma200 -> entry Short + exit(same formulas);  crossunder -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar from strategy.position_avg_price, which is still the price
      of the position held then: na from flat (no bracket), and the replaced position's fill price on a
      reversal, as written (as #473147); the short uses the long formulas, so its levels are on the wrong
      side and close it one bar after its fill. A loop tracks those prices; the levels are sent as
      fractions of the new fill open (a level at or through it is marketable and closed one bar late). A
      close acts only on the held position and leaves a same-bar reversal standing (as #441963). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. Margin 100 % is sizing. 2-day bars are blocks of two broker days. FREQ = "2D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, SMA crossings on the SMA 200 side with crossing closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 % stored, not ported; the bracket percentages stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_481350_sma20_50_cross_sma200_side_reversal_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "trend": 200, "sl_pct": 0.02, "tp_pct": 0.04, "days": 2}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    t = c.rolling(int(p["trend"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    lc = up & (c > t).to_numpy()
    sc = dn & (c < t).to_numpy()
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
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, avg, sl, tp = 0, 0, np.nan, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan     # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = avg * (1 - slp), avg * (1 + tpp)    # the long formulas, as written
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
        if pos == 1 and dn[i] and not se[i]:
            lx[i], pend = True, 2
        elif pos == -1 and up[i] and not le[i]:
            sx[i], pend = True, 2
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
