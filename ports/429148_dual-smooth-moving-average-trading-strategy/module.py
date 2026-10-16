"""NNFX template, 2-day bars: an SSL(8) flip confirmed by the SSL(16) side and the trend-direction-force index
(each allowed one bar late) goes long or short; an SSL(8) or SSL(16) flip against the position closes it (the
per-bar ATR exit is described, not emitted).
Port of FMZ strategy #429148 "Dual Smooth Moving Average Trading Strategy" (NNFX Strategy 3 Indicator Template | jh).

FMZ source id: 429148

Source
    https://www.fmz.com/strategy/429148 (PineScript v3, FMZ last modified 2023-10-13 15:45:58).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 169-353), SSL 8 / 16, TDFI 6 with +/-0.05, ATR 14 (SMA) x 1.5 / 1
    Hlv = close > sma(high,n) ? 1 : close < sma(low,n) ? -1 : Hlv[1]; SSL up / down swap on Hlv
    enterLong = SSL8 flips up and (SSL16 up now or one bar ago) and (TDFI > 0.05 now or one bar ago) -> order L1 long
    enterShort = mirror -> order S1 short; exitLong = SSL8 or SSL16 flips down -> close L1; exitShort mirror
    every bar: exit(L1, stop = close - 1.5 atr, limit = close + 1 atr); exit(S1, stop = close + 1.5 atr, limit = close - 1 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * TDFI (no volume data): mma = ema(close x 1000, 6), smma = ema(mma, 6), tdf = |mma - smma| x
      ((d mma + d smma) / 2)^3, normalised by its highest absolute value over 18 bars.
    * strategy.order adds by quantity; a long order arrives on the same bar as the short's close
      (exitShort coincides with enterLong), so the net effect is a one-bar reversal: REVERSAL INTENDED.
    * The strategy.exit bracket is re-issued on every bar from that bar's close and ATR (stop and
      limit both move each bar): a moving stop that stops() cannot express (rule 2). Not emitted; mark
      trailing_stop_pending, described in PORT_NOTES.
    * `year > 2009` is a backtest window: dropped. The strategy() line is commented out.
    * Multi-day bars are blocks of 2 broker days (17:00 America/New_York) counted from 1970-01-01, each
      stamped with its first minute. FREQ = "2D" from the backtest header (period 2d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket is not emitted (rule 2).
    2 generic: PASS, channel flips and a normalised index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_429148_nnfx_ssl_tdfi"
FAMILY = "ssl_channel"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ssl1": [8, 5],
    "ssl2": [16, 30],
}
DEFAULT_PARAMS = {"ssl1": 8, "ssl2": 16, "lookback": 6, "filter_high": 0.05, "filter_low": -0.05, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _hlv(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up = (c > h.rolling(n).mean()).to_numpy()
    dn = (c < lo.rolling(n).mean()).to_numpy()
    out = np.zeros(len(c), dtype=np.int8)
    q = 0
    for i in range(len(c)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    h1, h2 = _hlv(bars_df, int(p["ssl1"])), _hlv(bars_df, int(p["ssl2"]))
    p1, p2 = np.concatenate(([0], h1[:-1])), np.concatenate(([0], h2[:-1]))
    x1_long, x1_short = (h1 == 1) & (p1 == -1), (h1 == -1) & (p1 == 1)
    x2_long, x2_short = (h2 == 1) & (p2 == -1), (h2 == -1) & (p2 == 1)
    t2_long, t2_short = h2 == 1, h2 == -1
    lb = int(p["lookback"])
    mma = (c * 1000).ewm(span=lb, adjust=False).mean()
    smma = mma.ewm(span=lb, adjust=False).mean()
    aver = ((mma - mma.shift(1)) + (smma - smma.shift(1))) / 2
    tdf = (mma - smma).abs() * aver ** 3
    ntdf = (tdf / tdf.abs().rolling(lb * 3).max()).to_numpy()
    v_long, v_short = ntdf > p["filter_high"], p["filter_low"] > ntdf
    sh = lambda a: np.concatenate(([False], a[:-1]))  # noqa: E731
    enter_long = x1_long & (t2_long | sh(t2_long)) & (v_long | sh(v_long))
    enter_short = x1_short & (t2_short | sh(t2_short)) & (v_short | sh(v_short))
    exit_long = x1_short | x2_short
    exit_short = x1_long | x2_long
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and exit_long[i]:
            pos = 0
        if pos == -1 and exit_short[i]:
            pos = 0
        if enter_long[i]:
            pos = 1
        elif enter_short[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
