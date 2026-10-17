"""Optimized Trend Tracker on a VAR average, broker days: the VAR (CMO-weighted) average of length 2 crossing above the
OTT line of two bars ago goes long, crossing below goes short; the OTT is a 1.4 % percent trail around the average.
Port of FMZ strategy #433011 "Multiple Moving Average Dynamic Trend Strategy" (Optimized Trend Tracker (OTTEx)).

FMZ source id: 433011

Source
    https://www.fmz.com/strategy/433011 (PineScript v4, FMZ last modified 2023-11-23 15:40:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-300), OTT period 2, percent 1.4, MA type VAR; support-line crossing signals
    VAR: alpha = 2 / (len + 1) x |CMO 9|, VAR = alpha src + (1 - alpha) VAR[1];  fark = MAvg x 1.4 %
    longStop / shortStop ratchets, dir flips, MT = dir == 1 ? longStop : shortStop;  OTT = MAvg > MT ? MT (200 + p) / 200 : MT (200 - p) / 200
    crossover(MAvg, OTT[2]) -> entry long;  crossunder(MAvg, OTT[2]) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported as written with the percent band (scale-free); lane A's OTT port #361567 (a near
      duplicate, ND361567) used an ATR band on hourly bars. The CMO is 0 when both sums are 0 (nz).
    * strategy.entry reverses: REVERSAL INTENDED. Timerange() is always true. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a percent band around an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND361567 (3 members, best partner #361567, Jaccard 0.711); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433011_ott_var_percent_cross"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [2, 5],
    "percent": [1.4, 3.0],
}
DEFAULT_PARAMS = {"length": 2, "percent": 1.4}


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


def _var_ma(src, length):
    d = src.diff()
    ud = d.clip(lower=0).rolling(9).sum()
    dd = (-d).clip(lower=0).rolling(9).sum()
    cmo = ((ud - dd) / (ud + dd)).replace([np.inf, -np.inf], np.nan).fillna(0).abs().to_numpy()
    s = src.to_numpy(dtype=float)
    alpha = 2 / (length + 1)
    out = np.zeros(len(s))
    prev = 0.0
    for i in range(len(s)):
        k = alpha * cmo[i]
        prev = out[i] = k * s[i] + (1 - k) * prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    mv = _var_ma(bars_df["close"], int(p["length"]))
    pc = float(p["percent"])
    m = len(mv)
    ott = np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    dirn = 1
    for i in range(m):
        fark = mv[i] * pc * 0.01
        ls, ss = mv[i] - fark, mv[i] + fark
        lsp = ls if np.isnan(ls_prev) else ls_prev          # nz(longStop[1], longStop)
        ssp = ss if np.isnan(ss_prev) else ss_prev
        ls = max(ls, lsp) if mv[i] > lsp else ls
        ss = min(ss, ssp) if mv[i] < ssp else ss
        if dirn == -1 and mv[i] > ssp:
            dirn = 1
        elif dirn == 1 and mv[i] < lsp:
            dirn = -1
        mt = ls if dirn == 1 else ss
        ott[i] = mt * (200 + pc) / 200 if mv[i] > mt else mt * (200 - pc) / 200
        ls_prev, ss_prev = ls, ss
    ott2 = np.concatenate(([np.nan, np.nan], ott[:-2]))
    mv1 = np.concatenate(([np.nan], mv[:-1]))
    o21 = np.concatenate(([np.nan], ott2[:-1]))
    with np.errstate(invalid="ignore"):
        up = (mv > ott2) & (mv1 <= o21)
        dn = (mv < ott2) & (mv1 >= o21)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
