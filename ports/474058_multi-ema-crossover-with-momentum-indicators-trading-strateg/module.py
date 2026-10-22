"""Double EMA crossings with RSI and MACD confirmation, daily bars: EMA 10 crossing over EMA 100 on the same bar as EMA 20 over EMA 50, with RSI over 50 and MACD over its signal, goes long; the mirror goes short; reversing. The 1.5 % stop and 3 % target are set from strategy.position_avg_price on the signal bar (na from flat, the replaced position's price on a reversal), as written.
Port of FMZ strategy #474058 "Multi EMA Crossover with Momentum Indicators Trading Strategy" (4 EMA Strategy with RSI & MACD).

FMZ source id: 474058

Source
    https://www.fmz.com/strategy/474058 (PineScript v5, FMZ last modified 2024-12-05 16:37:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-171), EMA 10 / 20 / 50 / 100; RSI 14, 50; MACD 12 / 26 / 9; stop 1.5 %, target 3 % of avg on the signal bar
    crossover(e10, e100) and crossover(e20, e50) and rsi > 50 and macd > signal -> entry Buy, sl := avg x 0.985, tp := avg x 1.03;  short mirror;  long: exit(stop = sl, limit = tp);  short: exit(stop = sl, limit = tp)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on the signal bar from strategy.position_avg_price, which is na from flat
      (no bracket) and the replaced position's fill price on a reversal, as written (as #468309,
      #473147); the exits re-sent while in a position keep those stored levels. The loop tracks the
      fill prices and the bracket inside each bar; the levels are sent as fractions of the new fill
      open (a level at or through it is marketable and closed one bar late). A repeat signal inside a
      trade is not followed (it would re-store levels from the trade's own price; such double crossings
      are rare). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the bracket base, as written.
    2 generic: PASS, double EMA crossings with RSI / MACD confirmation and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474058_double_ema_cross_rsi_macd_bracket_from_replaced_avg"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.015, 0.03],
    "tp_pct": [0.03, 0.06],
}
DEFAULT_PARAMS = {"sl_pct": 0.015, "tp_pct": 0.03}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e10, e20, e50, e100 = (c.ewm(span=n, adjust=False).mean() for n in (10, 20, 50, 100))
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lc = (_x(e10, e100) & _x(e20, e50) & (r > 50) & (macd > sig)).to_numpy()
    sc = (_x(e100, e10) & _x(e50, e20) & (r < 50) & (macd < sig)).to_numpy()
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
            sl_n, tp_n = avg * (1 + slp), avg * (1 - tpp)
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
