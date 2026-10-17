"""HPotter TTM scalper switch, broker days, always in the market: a close above the previous close, with the previous close
above the close two or three bars back ("sell trigger"), turns the switch long; a close below the previous close, with
the previous close below the close two or three bars back, turns it short. The switch starts short.
Port of FMZ strategy #434330 "基于价格反转的TTM银隼震荡策略TTM-Falcon-Oscillator-Reversal-Strategy-Based-on-Price-Reversion" (TTM scalper indicator).

FMZ source id: 434330

Source
    https://www.fmz.com/strategy/434330 (PineScript v2, FMZ last modified 2023-12-05 15:07:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 179-194), reverse false
    triggerSell = close[1] < close and (close[2] < close[1] or close[3] < close[1]);  triggerBuy = close[1] > close and (close[2] > close[1] or close[3] > close[1])
    buySellSwitch = triggerSell ? 1 : triggerBuy ? 0 : buySellSwitch[1];  clr_s follows it;  clr_s == 0 -> pos -1 (entry short), else pos 1 (entry long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * clr_s changes only when the switch changes, so it equals the switch; both start at 0 (nz), so
      the strategy is short from the first bar, as written. The "sell" trigger goes long and the
      "buy" trigger short, as written. strategy.entry reverses: REVERSAL INTENDED. reverse is false.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-to-close patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434330_ttm_scalper_switch"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reverse": [False, True],
}
DEFAULT_PARAMS = {"reverse": False}


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
    c = bars_df["close"]
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    ts = ((c1 < c) & ((c2 < c1) | (c3 < c1))).to_numpy()
    tb = ((c1 > c) & ((c2 > c1) | (c3 > c1))).to_numpy()
    m = len(ts)
    sw = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if ts[i]:
            q = 1
        elif tb[i]:
            q = 0
        sw[i] = q
    tgt = np.where(sw == 1, 1, -1).astype(np.int8)
    if bool(p["reverse"]):
        tgt = -tgt
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
