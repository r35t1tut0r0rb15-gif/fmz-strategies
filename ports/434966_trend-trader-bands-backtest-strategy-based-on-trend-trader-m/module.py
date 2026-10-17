"""HPotter Trend Trader bands, broker days: Abraham's trend line (the 21-bar high less 3 average true ranges, or the 21-bar
low plus 3, whichever the close has broken) is smoothed by an EMA 21; a close above that average plus a band step goes
long, below it less the step goes short; held in between. The 20-price-unit step is re-expressed as an ATR multiple.
Port of FMZ strategy #434966 "Trend Trader Bands Backtest Strategy Based on Trend Trader Moving Average" (Trend Trader Bands Backtest).

FMZ source id: 434966

Source
    https://www.fmz.com/strategy/434966 (PineScript v3, FMZ last modified 2023-12-11 13:12:44).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 128-151), length 21, MA 21, band step 20 (price units), multiplier 3; reverse false
    avgTR = wma(atr(1), 21);  hiLimit = highest(21)[1] - 3 avgTR[1];  loLimit = lowest(21)[1] + 3 avgTR[1]
    ret = close > hiLimit and close > loLimit ? hiLimit : close < loLimit and close < hiLimit ? loLimit : ret[1];  ma = ema(ret, 21)
    pos = close < ma - 20 ? -1 : close > ma + 20 ? 1 : pos[1];  1 -> entry long;  -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the band step is 20 price units; on daily BTC that is about 0.02 x the 21-bar
      weighted average true range in 2023, so the port uses step_atr x avgTR. highest / lowest use
      the bar highs / lows. ret starts at 0 (nz), as written.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit band step -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434966 (2 members, best partner #442566, Jaccard 0.852); ND434966 (2 members, best partner #438053, Jaccard 0.705); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434966_trend_trader_bands"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "step_atr": [0.02, 0.5],
}
DEFAULT_PARAMS = {"length": 21, "length_ma": 21, "mult": 3.0, "step_atr": 0.02}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    avg_tr = _wma(tr, n)
    hi_l = (h.rolling(n).max().shift(1) - avg_tr.shift(1) * float(p["mult"])).to_numpy()
    lo_l = (lo.rolling(n).min().shift(1) + avg_tr.shift(1) * float(p["mult"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ret = np.zeros(m)
    r = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if cv[i] > hi_l[i] and cv[i] > lo_l[i]:
                r = hi_l[i]
            elif cv[i] < lo_l[i] and cv[i] < hi_l[i]:
                r = lo_l[i]
            ret[i] = r
    ma = pd.Series(ret, index=c.index).ewm(span=int(p["length_ma"]), adjust=False).mean().to_numpy()
    step = float(p["step_atr"]) * avg_tr.to_numpy()
    with np.errstate(invalid="ignore"):
        dn, up = cv < ma - step, cv > ma + step
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if dn[i]:
            q = -1
        elif up[i]:
            q = 1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
