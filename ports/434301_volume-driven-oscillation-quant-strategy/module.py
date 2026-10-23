"""HPotter's Klinger volume oscillator (EMA 34 minus EMA 55 of signed volume) above its EMA 13 trigger goes long, below it goes short (held on a tie); broker days, reversing.
Port of FMZ strategy #434301 "Volume driven Oscillation Quant Strategy" (Klinger Volume Oscillator (KVO) (HPotter)).

FMZ source id: 434301

Source
    https://www.fmz.com/strategy/434301 (PineScript v2, FMZ last modified 2023-12-05 11:35:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-181), trigger 13, fast 34, slow 55; reverse off
    xTrend = hlc3 > hlc3[1] ? volume x 100 : -volume x 100;  xKVO = ema(xTrend, 34) - ema(xTrend, 55);  pos = xKVO > ema(xKVO, 13) ? 1 : xKVO < trigger ? -1 : pos[1]
    pos 1 -> entry Long;  pos -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The oscillator is compared with its own EMA, so only the volume's shape matters; the x 100 factor
      cancels. reverse is off. The same Klinger state as the second half of #432845. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume oscillator against its trigger.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Klinger oscillator (signed volume EMAs 34 / 55, trigger 13); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434301_klinger_volume_oscillator_trigger_state_daily_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_x": [34, 20],
    "slow_x": [55, 89],
}
DEFAULT_PARAMS = {"trig_len": 13, "fast_x": 34, "slow_x": 55}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    hlc3 = (h + lo + c) / 3
    xt = pd.Series(np.where(hlc3 > hlc3.shift(1), v * 100, -v * 100), index=c.index)
    kvo = xt.ewm(span=int(p["fast_x"]), adjust=False).mean() - xt.ewm(span=int(p["slow_x"]), adjust=False).mean()
    trig = kvo.ewm(span=int(p["trig_len"]), adjust=False).mean()
    raw = np.where(kvo > trig, 1, np.where(kvo < trig, -1, 0))
    pos = np.zeros(len(raw), dtype=np.int8)
    q = 0
    for i in range(len(raw)):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prv = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prv != 1), index=ix), false,
            pd.Series((pos == -1) & (prv != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
