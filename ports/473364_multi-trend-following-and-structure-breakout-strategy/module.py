"""Pullback breakouts in the EMA 200 trend, daily bars, entries only from flat: with the close over a rising EMA 200, a low touching the EMA 25 or 50, RSI over 50, a high over the previous 5-bar high and a white candle, it buys; the mirror sells. Each trade has a 10 / 15-point stop and target from its signal close.
Port of FMZ strategy #473364 "Multi Trend Following and Structure Breakout Strategy" (Custom Buy/Sell Strategy).

FMZ source id: 473364

Source
    https://www.fmz.com/strategy/473364 (PineScript v5, FMZ last modified 2024-11-29 15:27:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-163), EMA 25 / 50 / 200, RSI 14; stop 10 / target 15 x syminfo.pointvalue from the signal close
    uptrend and pullback and rsi > 50 and high > highest(high, 5)[1] and close > open and flat -> entry Buy, exit(limit = close + 15, stop = close - 10);  mirror and flat -> entry Sell, exit(limit = close - 15, stop = close + 10)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 10 / 15 pips times syminfo.pointvalue (1 on the header's pair) are 10 / 15 in price, ported as
      fractions of 42000 of the signal close (0.000238 / 0.000357). Entries only from flat: a loop
      follows each trade's bracket on the bar's high / low so the flat gate lines up (as 449508); the
      levels are sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late). The two setups cannot hold on one bar, and entries come only from flat, so
      opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of the signal close.
    2 generic: PASS, trend pullback breakouts with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the point bracket stored.
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

NAME = "fmz_473364_ema200_trend_pullback_break5_point_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.000238, 0.00238],
    "tp_frac": [0.000357, 0.00357],
}
DEFAULT_PARAMS = {"sl_frac": 0.000238, "tp_frac": 0.000357}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e25, e50, e200 = (c.ewm(span=n, adjust=False).mean() for n in (25, 50, 200))
    r = _rsi(c, 14)
    buy = ((e200 < c) & (e200 > e200.shift(1)) & ((lo <= e25) | (lo <= e50)) & (r > 50)
           & (h > h.rolling(5).max().shift(1)) & (c > o))
    sell = ((e200 > c) & (e200 < e200.shift(1)) & ((h >= e25) | (h >= e50)) & (r < 50)
            & (lo < lo.rolling(5).min().shift(1)) & (c < o))
    lc, sc = buy.to_numpy(), sell.to_numpy()
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
