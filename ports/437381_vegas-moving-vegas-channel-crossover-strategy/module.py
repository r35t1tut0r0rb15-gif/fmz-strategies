"""Vegas tunnel sub-strategies, broker days: four long setups (an EMA 36 crossing over the EMA 144 with the 48 / 56 MACD positive; pullbacks of the low to the EMA 144, EMA 36 or EMA 576 inside the tunnel order) and
three short setups (rejections of the high at the EMA 36, 169 or 676), each with its own exits; one position at a time, reversing.
Port of FMZ strategy #437381 "移動的Vegas通道穿越策略Moving-Vegas-Channel-Crossover-Strategy" (Vegas Tunnel strategy).

FMZ source id: 437381

Source
    https://www.fmz.com/strategy/437381 (PineScript v4, FMZ last modified 2024-01-02 10:53:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 120-231), EMA 36 / 43 / 144 / 169 / 576 / 676 / 2304, MACD = EMA 48 - EMA 56, BB 20 x 2; date range always true
    buy: crossunder(f3, f1) and macd > 0;  close on crossunder(f3, f5).  buy1: crossover(low, f3), macd > 0, f3 > f6;  close on macd < 0 or f3 < f6, or crossunder(close, upper x 0.999).  buy3 / buy4 alike
    sell1: macd < 0, crossunder(high, f1), f1 < f3 < f6;  close on macd > 0 or f1 > f4, or crossunder(lower x 0.999, close).  sell2 / sell3 alike

Interpretation choices (Pine rules in SURVEY_README.md)
    * With pyramiding 0 only one entry can be open: an entry in the open side is ignored, an opposite one
      reverses. Each close only acts on its own entry id when that id is the open position at the bar's
      close, so the port tracks which setup holds the position, and the orders follow the script's call
      order. The per-setup quantities (1 and 100) are sizing. The higher-timeframe EMA / SMA lines are
      plotted only. REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA tunnel, MACD sign, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the per-setup quantities stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437381_vegas_tunnel_setups"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 30],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0}
EMAS = (36, 43, 144, 169, 576, 676, 2304)


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


def _xunder(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f1, f2, f3, f4, f5, f6, f7 = (c.ewm(span=n, adjust=False).mean() for n in EMAS)
    macd = c.ewm(span=48, adjust=False).mean() - c.ewm(span=56, adjust=False).mean()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    xu_up = _xunder(c, upper * 0.999)
    # (kind, id, direction, condition) in the script's call order
    seq = [
        ("entry", "buy", 1, _xunder(f3, f1) & (macd > 0)),
        ("close", "buy", 1, _xunder(f3, f5)),
        ("entry", "buy1", 1, _xover(lo, f3) & (macd > 0) & (f3 > f6)),
        ("close", "buy1", 1, (macd < 0) | (f3 < f6)),
        ("close", "buy1", 1, xu_up),
        ("entry", "buy3", 1, (macd > 0) & _xunder(lo, f1) & (f1 > f4)),
        ("close", "buy3", 1, (macd < 0) | (f1 < f4)),
        ("close", "buy3", 1, xu_up),
        ("entry", "buy4", 1, (macd > 0) & _xunder(lo, f5) & (f4 > f5)),
        ("close", "buy4", 1, (macd < 0) | (f4 < f6)),
        ("close", "buy4", 1, xu_up),
        ("entry", "sell1", -1, (macd < 0) & _xunder(h, f1) & (f1 < f3) & (f3 < f6)),
        ("close", "sell1", -1, (macd > 0) | (f1 > f4)),
        ("close", "sell1", -1, _xunder(lower * 0.999, c)),
        ("entry", "sell2", -1, (macd < 0) & _xunder(h, f4) & (f4 < f6)),
        ("close", "sell2", -1, (macd > 0) | (f4 > f6)),
        ("close", "sell2", -1, _xunder(lower, c)),
        ("entry", "sell3", -1, (macd < 0) & _xunder(h, f6)),
        ("close", "sell3", -1, (macd > 0) | (f6 > f7)),
        ("close", "sell3", -1, _xunder(lower, c)),
    ]
    arrs = [(k, i, d, s.to_numpy()) for k, i, d, s in seq]
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    side, oid = 0, None
    for t in range(m):
        calc_id = oid                                  # the entry id open at the bar's close
        s, o = side, oid
        for kind, eid, d, cond in arrs:
            if not cond[t]:
                continue
            if kind == "entry":
                if s != d:
                    s, o = d, eid
            elif calc_id == eid and o == eid:
                s, o = 0, None
        if s == 1 and side != 1:
            le[t] = True
        elif s == -1 and side != -1:
            se[t] = True
        elif s == 0 and side == 1:
            lx[t] = True
        elif s == 0 and side == -1:
            sx[t] = True
        side, oid = s, o
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
