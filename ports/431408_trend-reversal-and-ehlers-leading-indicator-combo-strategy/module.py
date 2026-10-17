"""HPotter combo, 1-hour bars: the 123 reversal and the daily Ehlers leading indicator sign (EMA 7 minus EMA 14 of the daily
hl2, minus its own EMA 7) must agree; both long holds a long, both short holds a short, any disagreement closes
everything.
Port of FMZ strategy #431408 "Trend Reversal and Ehlers Leading Indicator Combo Strategy" (Combo Backtest 123 Reversal & D_ELI (Ehlers Leading Indicator)).

FMZ source id: 431408

Source
    https://www.fmz.com/strategy/431408 (PineScript v4, FMZ last modified 2023-11-07 16:10:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 136-205), 123 reversal stoch 14 / 1 / 3, level 50; ELI 7
    xHL2 = security(tickerid, 'D', hl2); d = ema(xHL2, 7) - ema(xHL2, 14); nRes = d - ema(d, 7)
    posELI = nRes > 0 ? 1 : nRes < 0 ? -1 : pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', hl2) without lookahead is read as the last completed broker day's hl2 (17:00
      America/New_York), built inside simulate() from the port's own bars; the source's value on the
      last bar of a day already includes that day (one bar earlier): stated approximation (as
      #429383). The EMAs run over the chart's bars of that series, as written.
    * "Trade reverse" defaults to false and is fixed. strategy.entry reverses: REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, a stochastic and an EMA difference.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426888 (31 members, best partner #432231, Jaccard 0.702); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily hl2 (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431408_combo_123_daily_eli"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "eli_len": [7, 14],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50, "eli_len": 7}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    pos1 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    lab = broker_day(bars_df.index)
    dh = h.groupby(lab).max().shift(1)                             # the last completed broker day
    dl = lo.groupby(lab).min().shift(1)
    x = pd.Series(((dh + dl) / 2).reindex(lab).to_numpy(), index=c.index).dropna()
    L = int(p["eli_len"])
    e = x.ewm(span=L, adjust=False).mean() - x.ewm(span=2 * L, adjust=False).mean()
    res = (e - e.ewm(span=L, adjust=False).mean()).reindex(c.index)
    pos2 = _hold((res > 0).to_numpy(), (res < 0).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
