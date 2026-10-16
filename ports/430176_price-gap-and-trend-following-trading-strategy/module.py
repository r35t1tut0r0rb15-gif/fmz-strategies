"""BroTheJo, broker days: CCI 10 crossing zero (either way) with RSI 14 at or under 35 in the last 4 bars and the whole bar
at or above the EMA 200 goes long; with RSI at or over 65 and the whole bar at or below the EMA goes short; a bar
reaching the EMA 200 +- 1.6 standard deviations closes everything.
Port of FMZ strategy #430176 "Price Gap and Trend Following Trading Strategy" (BroTheJo Strategy).

FMZ source id: 430176

Source
    https://www.fmz.com/strategy/430176 (PineScript v5, FMZ last modified 2023-10-25 18:02:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 173-240), CCI 10, RSI 14 with 35 / 65, EMA 200, bands 1.6 sd
    cross = ta.cross(cci(close, 10), 0)      (either direction; the "up" and "down" crosses are the same test)
    long: cross and rsi <= 35 in bars 0-3 and high >= ema200 and low >= ema200 -> entry long
    short: cross and rsi >= 65 in bars 0-3 and high <= ema200 and low <= ema200 -> entry short
    high >= ema200 + 1.6 stdev(close, 200) or low <= ema200 - 1.6 stdev -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross(cci, 0) and ta.cross(0, cci) are both "crosses zero in either direction": kept as
      written. ta.highest(high, 1) and ta.lowest(low, 1) are the bar's own high and low.
    * close_all acts on the position held at the start of the bar: it wins over an entry on the
      same bar when a position was held (the bar ends flat); from flat the entry stands.
    * The divergence option is off (default). stdev is the population deviation; RSI is Wilder's.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI, RSI levels and standard-deviation bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430176 (2 members, best partner #435969, Jaccard 0.766); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430176_brothejo_cci_rsi_ema200"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [200, 100],
    "band_mult": [1.6, 2.5],
}
DEFAULT_PARAMS = {"cci_len": 10, "rsi_len": 14, "overbought": 65, "oversold": 35, "ema_period": 200, "band_mult": 1.6}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _cci(src, n):
    ma = src.rolling(n).mean()
    dev = src.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (src - ma) / (0.015 * dev.replace(0.0, np.nan))


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    cci = _cci(c, int(p["cci_len"]))
    cross = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    r = _rsi(c, int(p["rsi_len"]))
    os_ago = (r <= p["oversold"]).astype(float).rolling(4, min_periods=1).max() > 0
    ob_ago = (r >= p["overbought"]).astype(float).rolling(4, min_periods=1).max() > 0
    n = int(p["ema_period"])
    mean = c.ewm(span=n, adjust=False).mean()
    sd = c.rolling(n).std(ddof=0)
    up_b, lo_b = mean + sd * p["band_mult"], mean - sd * p["band_mult"]
    le = (cross & os_ago & (h >= mean) & (lo >= mean)).to_numpy()
    se = (cross & ob_ago & (h <= mean) & (lo <= mean)).to_numpy()
    ca = ((h >= up_b) | (lo <= lo_b)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        if ca[i] and start != 0:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
