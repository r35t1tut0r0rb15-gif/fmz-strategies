"""MACD (12 / 26 / 9) signal crossings, broker days, entries only from flat: the cross up goes long with a stop at the 3-bar low and a 1.5 R target, the cross down goes short with a stop at the 3-bar high and a 1.5 R target.
Port of FMZ strategy #477604 "高级MACD均线交叉交易策略结合自适应风险管理-Advanced-MACD-Crossover-Trading-Strategy-with-Adaptive-Risk-Management" (Estrategia MACD).

FMZ source id: 477604

Source
    https://www.fmz.com/strategy/477604 (PineScript v5, FMZ last modified 2025-01-06 16:34:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-137), MACD 12 / 26 / 9; stop candles 3; ratio 1.5; direction both
    crossover(macd, signal) and hist > 0 and flat -> entry Larga + exit(stop = lowest(low, 3), limit = close + 1.5 (close - stop));  crossunder and hist < 0 and flat -> entry Corta + exit(stop = highest(high, 3), limit = close - 1.5 (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The histogram test always holds on a crossing. The bracket is set on the signal bar from that
      bar's 3-bar low / high and close, and sent as fractions of the fill open (a level at or through it
      is marketable and closed one bar late, as #458256). Entries need a flat position at the bar's
      close, so a loop follows the bracket on each bar's high / low (as #449508) to know when the
      position is flat. Opposite entries cannot occur (entries only from flat). Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar swing bracket as fractions of the fill.
    2 generic: PASS, MACD crossings with a swing stop and R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_477604_macd_cross_swing3_stop_r15_flat_only"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "velas_sl": [3, 5],
    "ratio": [1.5, 2.5],
}
DEFAULT_PARAMS = {"velas_sl": 3, "ratio": 1.5}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hist = macd - sig
    lc = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (hist > 0)).to_numpy()
    sc = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (hist < 0)).to_numpy()
    k = int(p["velas_sl"])
    ll = lo.rolling(k).min().to_numpy(dtype=float)
    hh = h.rolling(k).max().to_numpy(dtype=float)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    rr = float(p["ratio"])
    m = len(cv)
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
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and pend == 0 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos != 0 or pend != 0:
            continue
        if lc[i]:
            sl_n = ll[i]
            tp_n = cv[i] + abs(cv[i] - sl_n) * rr
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            sl_n = hh[i]
            tp_n = cv[i] - abs(sl_n - cv[i]) * rr
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
