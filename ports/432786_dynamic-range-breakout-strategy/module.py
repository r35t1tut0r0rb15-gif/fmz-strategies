"""Noro's lower-band dips, long only, broker days: a low under the lower Bollinger band of the lows (SMA 25 - 2 standard
deviations) goes long; a green bar with a body over half its 10-bar average closes it.
Port of FMZ strategy #432786 "Dynamic Range Breakout Strategy" (Noro's Wizard Strategy v1.0).

FMZ source id: 432786

Source
    https://www.fmz.com/strategy/432786 (PineScript v2, FMZ last modified 2023-12-01 15:00:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 246-289), BB 25 x 2 on the lows, body and colour filters off; martingale-free lot, pyramiding 10
    lower = sma(low, 25) - 2 stdev(low, 25)
    low < lower -> entry long (adds allowed);  close > open and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the body and colour filters off, any bar whose low pierces the band signals. The final
      close_all acts on the position held at the bar's start and leaves the bar flat (C31-C39
      convention), so a green, large-bodied signal bar ends flat. Repeated signals while long are
      adds (pyramiding 10): criterion 4, not ported. The date inputs are the author's window: dropped.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a band of the lows and the body against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, the capital % input, the lot and pyramiding stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430066 (2 members, best partner #430066, Jaccard 0.714); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432786_noro_wizard_band_dip"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [25, 15],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 25, "mult": 2.0, "body_len": 10}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    lower = lo.rolling(n).mean() - float(p["mult"]) * lo.rolling(n).std(ddof=0)
    body = (c - o).abs()
    up = (lo < lower).to_numpy()
    ex = ((c > o) & (body > body.rolling(int(p["body_len"])).mean() / 2)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        if ex[i]:
            pos = 0                                       # the final close_all leaves the bar flat
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
