"""Triple-EMA crossing with a higher-timeframe confirmation, broker days: a fast TEMA over a slow TEMA, with the daily TEMA 5 over the TEMA 15, goes long (the long closes when the fast falls under the slow); the
mirror goes short; each side closes when the fast crosses back.
Port of FMZ strategy #436516 "基于多时间框架TEMA指标交叉的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Timeframe-TEMA-Crossover" (TEMA Cross +HTF Backtest).

FMZ source id: 436516

Source
    https://www.fmz.com/strategy/436516 (PineScript v4, FMZ last modified 2023-12-25 14:20:36).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 139-221), fast 20, slow 60, higher timeframe "D" with 5 / 15, Longs+Shorts
    TEMA(n) = 3 ema1 - 3 ema2 + ema3 of close;  x = TEMA(20), y = TEMA(60);  HTF x, y = the same on resolution "D" with lengths 5 / 15 (security, lookahead on)
    LongEntry = x > y and HTFx > HTFy;  LongClose = x < y;  ShortEntry = x < y and HTFx < HTFy;  ShortClose = x > y;  entry Long, close Long, entry Short, close Short in that order

Interpretation choices (Pine rules in SURVEY_README.md)
    * The backtest header chart is the daily chart, so the higher-timeframe resolution "D" is the chart's
      own series: the higher-timeframe TEMAs are the same indicators with lengths 5 and 15 (the
      lookahead switch has no effect on a same-resolution request). The date window is always true. The
      four rules of one bar are filled at the next open in the script's call order; a close only acts
      on a position of its own side. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, triple-average crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_436516_tema_cross_htf_filter"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [60, 40],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 60, "htf_fast": 5, "htf_slow": 15}


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


def _tema(s, n):
    n = int(n)
    e1 = s.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * e1 - 3 * e2 + e3


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    x, y = _tema(c, p["fast"]), _tema(c, p["slow"])
    hx, hy = _tema(c, p["htf_fast"]), _tema(c, p["htf_slow"])
    el = ((x > y) & (hx > hy)).to_numpy()
    xl = (x < y).to_numpy()
    es = ((x < y) & (hx < hy)).to_numpy()
    xs = (x > y).to_numpy()
    valid = (x.notna() & y.notna() & hx.notna() & hy.notna()).to_numpy()
    m = len(c)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "XL" and pos > 0:
                    pos = 0
                elif op == "XS" and pos < 0:
                    pos = 0
        held[i] = pos
        ops = []
        if valid[i]:
            if el[i]:
                ops.append("eL")
            if xl[i]:
                ops.append("XL")
            if es[i]:
                ops.append("eS")
            if xs[i]:
                ops.append("XS")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
