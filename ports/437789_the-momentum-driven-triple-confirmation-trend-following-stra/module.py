"""Momentum RSI, SuperTrend and an EMA trail line agreeing, broker days: from flat, the EMA 12 above its 1 % trail line with the SuperTrend (10, 3) up and the RSI 10 of the 10-bar momentum above 60 goes long, the
mirror (EMA under the trail line, SuperTrend down, the same RSI test) goes short; a close on the wrong side of the SuperTrend line closes the position at the next open.
Port of FMZ strategy #437789 "The Momentum Driven Triple Confirmation Trend Following Strategy" (The Flash-Strategy (Momentum-RSI, EMA-crossover, ATR)).

FMZ source id: 437789

Source
    https://www.fmz.com/strategy/437789 (PineScript v5, FMZ last modified 2024-01-05 15:46:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 197-291), Mom-RSI 10, limit 60; SuperTrend ATR 10, factor 3; EMA 12, percent 1; direction BOTH; Version 1 (dynamic) on, Version 2 (static 5 % / 10 %) off; 50000 per position
    buy = Trail1 > Trail2 and direction < 0 and rsi(close - close[10], 10) > 60;  sell = Trail1 < Trail2 and direction > 0 and rsi_mom > 60;  opentrades == 0 -> entry Long_0 / Short_0
    close < supertrend -> exit(Long_Close, stop = supertrend);  close > supertrend -> exit(Short_Close, stop = supertrend)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Version 1: the exit stop is placed only once the close is already beyond the SuperTrend line, so a
      long's sell stop sits above the market (a short's buy stop below it) and fills at the next bar's
      open; the port reads it as a close at the next open (a next bar that opens back across the line
      would leave the stop waiting; not modelled). Version 2 is off and not ported (its inputs stored).
      Trail2 is the recursive EMA trail line of the source (nz(Trail2[1], 0) start). Entries only from
      flat: Opposite entries cannot occur. The fixed 50000 per position is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the beyond-the-market stop read as a close at the next open.
    2 generic: PASS, momentum RSI, SuperTrend and an EMA trail line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed 50000 per position and the unused static bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND437789 (2 members, best partner #439601, Jaccard 0.707); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437789_mom_rsi_supertrend_ema_trail"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "mom_rsi_val": [60, 50],
}
DEFAULT_PARAMS = {"factor": 3.0, "mom_rsi_val": 60, "mom_len": 10, "atr_period": 10, "ema_len": 12,
                  "ema_pct": 1.0}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _supertrend(h, lo, c, factor, n):
    """Pine's ta.supertrend(factor, atrPeriod): (line, direction), direction -1 up, 1 down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub = np.full(m, np.nan), np.full(m, np.nan)
    st, d = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            dn_dir = True
        elif st[i - 1] == ub[i - 1]:
            dn_dir = not (cv[i] > ub[i])
        else:
            dn_dir = cv[i] < lb[i]
        st[i] = ub[i] if dn_dir else lb[i]
        d[i] = 1.0 if dn_dir else -1.0
    return st, d


def _ema_trail(t1, af):
    """Trail2 of the source: the EMA's percent trail line, started from nz(Trail2[1], 0) = 0."""
    m = len(t1)
    t2 = np.zeros(m)
    for i in range(m):
        p = t2[i - 1] if i > 0 else 0.0
        a = t1[i]
        ap = t1[i - 1] if i > 0 else np.nan
        sl = a * af
        iff_1 = a - sl if a > p else a + sl
        iff_2 = min(p, a + sl) if (a < p and ap < p) else iff_1
        t2[i] = max(p, a - sl) if (a > p and ap > p) else iff_2
    return t2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["mom_len"])
    rsi_mom = _rsi(c - c.shift(n), n).to_numpy()
    st, d = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_period"]))
    t1 = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    t2 = _ema_trail(t1, float(p["ema_pct"]) / 100.0)
    lim = float(p["mom_rsi_val"])
    buy = (t1 > t2) & (d < 0) & (rsi_mom > lim)
    sell = (t1 < t2) & (d > 0) & (rsi_mom > lim)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, False
    for i in range(m):
        if pend:                                         # the stop fills at this bar's open
            pos, pend = 0, False
        if pos == 1 and cv[i] < st[i]:
            lx[i], pend = True, True
        elif pos == -1 and cv[i] > st[i]:
            sx[i], pend = True, True
        elif pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pos = True, 1
            elif sell[i]:
                se[i], pos = True, -1
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
