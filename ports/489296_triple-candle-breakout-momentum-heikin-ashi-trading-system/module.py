"""Heikin-Ashi turns, broker days: after three red HA candles and a green one, a bar whose high breaks that green candle's HA high goes long, closed when a later red HA candle's low is broken; the mirror goes short.
Port of FMZ strategy #489296 "Triple Candle Breakout Momentum Heikin Ashi Trading System" (Heikin-Ashu Strategy).

FMZ source id: 489296

Source
    https://www.fmz.com/strategy/489296 (PineScript v6, FMZ last modified 2025-04-03 11:17:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 261-340), Heikin-Ashi; 3-candle streaks; flags and levels (var)
    3 red + green -> first_green_high := ha_high (else nz(previous));  ha_high[1] == first_green_high and high > it -> entry Long
    after the entry, the first red HA candle's ha_low is kept;  long_active and low < it -> close Long;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The HA candles, kept levels and active flags are followed in a loop, as written: the kept green high
      starts at 0 (nz), so a long needs the very next bar to break it. The flags, not the position, gate the
      exits, and an entry on the other side reverses (REVERSAL INTENDED). No sizing code. MPL 2.0 source
      (the notice is kept: Mozilla Public License 2.0, © YashEzio). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin-Ashi streak breakouts with candle-low exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489296_heikin_ashi_3streak_breakout_candle_exit_reversal"
FAMILY = "heikin_ashi"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "streak": [3, 2, 4],
}
DEFAULT_PARAMS = {"streak": 3}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    hc = (o + h + lo + c) / 4
    ho = np.full(m, np.nan)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    red, green = hc < ho, hc > ho
    k = int(p["streak"])
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    fgh = fre = frl = fge = np.nan
    la = sa = False
    for i in range(m):
        run_r = i >= k and all(red[i - j] for j in range(1, k + 1)) and green[i]
        run_g = i >= k and all(green[i - j] for j in range(1, k + 1)) and red[i]
        fgh = hh[i] if run_r else (0.0 if np.isnan(fgh) else fgh)
        lb = i >= 1 and hh[i - 1] == fgh and h[i] > fgh
        frl = np.nan if lb else (hl[i] if red[i] and np.isnan(frl) else frl)
        la = True if lb else la
        lex = la and not np.isnan(frl) and lo[i] < frl
        if lex:
            la = False
        fre = hl[i] if run_g else (0.0 if np.isnan(fre) else fre)
        sb = i >= 1 and hl[i - 1] == fre and lo[i] < fre
        fge = np.nan if sb else (hh[i] if green[i] and np.isnan(fge) else fge)
        sa = True if sb else sa
        sex = sa and not np.isnan(fge) and h[i] > fge
        if sex:
            sa = False
        le[i], lx[i], se[i], sx[i] = lb, lex, sb, sex
    idx = bars_df.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~se), S(se), S(sx & ~le)


def portfolio_kwargs(**params):
    return {}
