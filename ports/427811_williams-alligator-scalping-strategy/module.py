"""Bill Williams alligator on Heikin Ashi candles, 4-day bars: with two Heikin Ashi candles of the same
colour and the jaw / teeth / lips (SMAs 13 / 8 / 5 of the Heikin Ashi hl2) fanned out upwards go long,
fanned downwards go short; close once the fan is broken.
Port of FMZ strategy #427811 "Williams Alligator Scalping Strategy".

FMZ source id: 427811

Source
    https://www.fmz.com/strategy/427811 (PineScript v4, FMZ last modified 2023-09-25 17:42:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 227-315), SMA, jaw 13 / teeth 8 / lips 5
    HA close / open / hl2 from security(heikinashi(ticker), timeframe.period, ...)
    dir = 1 when this and the previous HA candle are green, -1 when both red
    long: dir == 1 and jaw < teeth < lips (and jaw < lips); close long when the order breaks
    short: dir == -1 and jaw > teeth > lips; close short when the order breaks
    exits with profit / loss / trail inputs all 0 -> na (no exit orders)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Heikin Ashi candles of the chart's own bars: ha_close = ohlc4, ha_open = mean of the previous
      ha_open and ha_close (first: (open + close) / 2), ha_high / ha_low include them.
    * `ma_type` 1 = SMA (default), 2 = EMA; the WMA, linreg and VWMA options are not ported (VWMA uses
      volume, check 8). The plot offsets do not reach the conditions.
    * The bracket and trail inputs default to 0 (off); the date switch is off.
    * strategy.entry reverses: REVERSAL INTENDED.
    * 4-day bars are blocks of broker days counted from 1970-01-01 (as worker A's 4-day ports),
      stamped with the session start. FREQ = "4D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; Heikin Ashi on the chart's own bars.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (the off bracket stored in original_sizing.txt).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA option is left out.
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427811_alligator_heikin_ashi"
FAMILY = "alligator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "jaw": [13, 21],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"jaw": 13, "teeth": 8, "lips": 5, "ma_type": 1}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=4)


def _heikin_ashi(bars):
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    ho = np.empty_like(hc)
    for i in range(len(hc)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    return ho, hc, (hh + hl) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ho, hc, hl2 = _heikin_ashi(bars_df)
    s = pd.Series(hl2, index=bars_df.index)

    def ma(n):
        n = int(n)
        return s.ewm(span=n, adjust=False).mean() if int(p["ma_type"]) == 2 else s.rolling(n).mean()

    jaw, teeth, lips = ma(p["jaw"]).to_numpy(), ma(p["teeth"]).to_numpy(), ma(p["lips"]).to_numpy()
    green, red = hc > ho, hc < ho
    g1 = np.concatenate(([False], green[:-1]))
    r1 = np.concatenate(([False], red[:-1]))
    d = np.where(green & g1, 1, np.where(red & r1, -1, 0))
    with np.errstate(invalid="ignore"):
        up = (jaw < teeth) & (jaw < lips) & (teeth < lips)
        dn = (jaw > teeth) & (jaw > lips) & (teeth > lips)
        x_long = (jaw > teeth) | (jaw > lips) | (teeth > lips)
        x_short = (jaw < teeth) | (jaw < lips) | (teeth < lips)
    m = len(d)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if d[i] == 1 and up[i]:
            pos = 1
        elif d[i] == -1 and dn[i]:
            pos = -1
        elif pos == 1 and x_long[i]:
            pos = 0
        elif pos == -1 and x_short[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
