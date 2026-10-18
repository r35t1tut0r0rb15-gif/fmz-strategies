"""Three-ten oscillator on daily hl2, broker days: the signal line (SMA 16 of the EMA 3 minus EMA 10 of hl2) under the MACD line holds a long, over it a short (reversing);
the "Trade reverse" input flips the side.
Port of FMZ strategy #436242 "Oscillator Index Transformation Strategy" (D_Three Ten Osc).

FMZ source id: 436242

Source
    https://www.fmz.com/strategy/436242 (PineScript v2, FMZ last modified 2023-12-22 14:21:28).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 130-147), EMA 3 / 10 of the daily hl2, signal SMA 16
    xPrice = security(tickerid, "D", hl2);  xMACD = ema(xPrice, 3) - ema(xPrice, 10);  xSignal = sma(xMACD, 16);  pos = xSignal > xMACD ? -1 : xSignal < xMACD ? 1 : last;  possig = reverse ? -pos : pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily backtest chart the "D" read is the chart's own hl2. The state holds until the opposite
      order; the signal is sent on the change of state only. REVERSAL INTENDED. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator against its signal.
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

NAME = "fmz_436242_three_ten_oscillator_state"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
    "length2": [10, 15],
}
DEFAULT_PARAMS = {"reverse": False, "length1": 3, "length2": 10, "length3": 16}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    macd = hl2.ewm(span=int(p["length1"]), adjust=False).mean() - hl2.ewm(span=int(p["length2"]), adjust=False).mean()
    sig = macd.rolling(int(p["length3"])).mean()
    dn = (sig > macd).to_numpy()
    up = (sig < macd).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if dn[i]:
            q = -1
        elif up[i]:
            q = 1
        tgt[i] = q
    if p["reverse"]:
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
