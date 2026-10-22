"""Tillson T3 (5, 0.1) against a Twin Optimized Trend Tracker band (VIDYA 5, OTT 0.1 %, band 0.6 %) with Williams %R 3, broker days, long only: T3 above the upper OTT band with %R over -20 buys, T3 below the lower band with %R over -70 closes.
Port of FMZ strategy #478690 "趋势追踪优化双T3指标策略-Optimized-Dual-T3-Trend-Tracking-Strategy" (FON60DK by leventsah).

FMZ source id: 478690

Source
    https://www.fmz.com/strategy/478690 (PineScript v6, FMZ last modified 2025-01-17 14:29:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-225), T3 5 / 0.1; TOTT 5 / 0.1 / coeff 0.006 (both sets equal by default); Williams %R 3
    var = vidya(close, 5) with a 9-bar CMO;  OTT from long / short stop ratchets of var -/+ 0.1 %;  OTTup / dn = OTT x (1 +/- 0.006)
    t3 > OTTup and %R > -20 -> entry Long;  t3 < OTTdn and %R > -70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop follows the VIDYA (restarting from the close whenever its CMO is na), the OTT stop
      ratchets and the trend direction as written (the direction is carried through dir[1]). The buy and
      sell parameter sets are equal by default, so one set is ported. A loop also follows the call
      order: an entry is taken only from flat and a close only from a long (a same-bar entry and close
      from flat leaves the long, from a long closes it). Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, T3 against an OTT band with a Williams %R filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478690_t3_vs_ott_band_williams_r_long"
FAMILY = "trend_tracker"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "t3_length": [5, 10],
    "tott_coeff": [0.006, 0.01],
}
DEFAULT_PARAMS = {"t3_length": 5, "tott_coeff": 0.006, "t3_opt": 0.1, "tott_length": 5, "tott_opt": 0.1,
                  "william_length": 3}


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


def _t3(c, n, a):
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    e4 = e3.ewm(span=n, adjust=False).mean()
    c1 = -a ** 3
    c2 = 3 * a * a + 3 * a ** 3
    c3 = -6 * a * a - 3 * a - 3 * a ** 3
    c4 = 1 + 3 * a + a ** 3 + 3 * a * a
    return c1 * e4 + c2 * e3 + c3 * e2 + c4 * e1


def _vidya(c, n):
    d = c.diff()
    ud = d.clip(lower=0).rolling(9).sum()
    dd = (-d).clip(lower=0).rolling(9).sum()
    tot = ud + dd
    cmo = ((ud - dd) / tot.where(tot != 0)).abs().to_numpy()
    cv = c.to_numpy(dtype=float)
    alpha = 2 / (n + 1)
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        base = cv[i] if np.isnan(prev) else prev
        out[i] = alpha * cmo[i] * cv[i] + (1 - alpha * cmo[i]) * base
        prev = out[i]
    return out


def _ott(mavg, opt):
    m = len(mavg)
    ott = np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    d = 1
    for i in range(m):
        fark = mavg[i] * opt * 0.01
        ls, ss = mavg[i] - fark, mavg[i] + fark
        lsp = ls if np.isnan(ls_prev) else ls_prev
        ssp = ss if np.isnan(ss_prev) else ss_prev
        if mavg[i] > lsp:
            ls = max(ls, lsp)
        if mavg[i] < ssp:
            ss = min(ss, ssp)
        if d == -1 and mavg[i] > ssp:
            d = 1
        elif d == 1 and mavg[i] < lsp:
            d = -1
        mt = ls if d == 1 else ss
        ott[i] = mt * (200 + opt) / 200 if mavg[i] > mt else mt * (200 - opt) / 200
        ls_prev, ss_prev = ls, ss
    return ott


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    t3 = _t3(c, int(p["t3_length"]), float(p["t3_opt"])).to_numpy()
    ott = _ott(_vidya(c, int(p["tott_length"])), float(p["tott_opt"]))
    k = float(p["tott_coeff"])
    w = int(p["william_length"])
    hh, ll = h.rolling(w).max(), lo.rolling(w).min()
    wr = (-100 * (hh - c) / (hh - ll).where(hh != ll)).to_numpy()
    buy = (t3 > ott * (1 + k)) & (wr > -20)
    sell = (t3 < ott * (1 - k)) & (wr > -70)
    m = len(t3)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and pos == 0:
            le[i], nxt = True, 1
        if sell[i] and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
