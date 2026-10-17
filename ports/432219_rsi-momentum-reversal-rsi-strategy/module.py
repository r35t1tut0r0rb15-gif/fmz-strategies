"""Noro's fast-RSI dips, long only, broker days: a red bar with a body over a quarter of its EMA 30 and the fast RSI 7
under 30 goes long; a green bar with a body over half of its EMA 30 and the fast RSI over 30 closes it.
Port of FMZ strategy #432219 "基于相对强弱指标RSI策略Momentum-Reversal-RSI-Strategy" (Noro's FRSI Strategy v1.21).

FMZ source id: 432219

Source
    https://www.fmz.com/strategy/432219 (PineScript v3, FMZ last modified 2023-11-15 16:29:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 200-244), fast RSI 7, limit 30, RSI bars 1, body EMA 30
    up = red bar and sps == 0 and fastrsi < 30 and body > ema(body, 30) / 4 -> entry long
    exit = green bar and fastrsi > 30 and body > ema(body, 30) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * sps is re-set to 0 on every bar (sps = 0 is not a var), so "sps == 0" is always true and the
      in-bar sps := 1 / 0 changes nothing. RSI bars = 1, so dnrsi is fastrsi < 30. The fast RSI is the
      source's own (Wilder; 100 with no down move, 0 with no up move).
    * The entry needs a red bar and the exit a green bar, so they never fall on one bar. The date
      window (to 2038) is the author's backtest range: dropped. Long only; Opposite entries cannot
      occur. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and body sizes against their own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND432219 (2 members, best partner #438024, Jaccard 0.734); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432219_noro_frsi_dip_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14],
    "limit": [30, 20],
}
DEFAULT_PARAMS = {"rsi_len": 7, "limit": 30, "body_len": 30}


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


def _fast_rsi(c, n):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(~((up == 0) & (dn != 0)), 0.0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _fast_rsi(c, int(p["rsi_len"]))
    body = (c - o).abs()
    eb = body.ewm(span=int(p["body_len"]), adjust=False).mean()
    lim = float(p["limit"])
    le = ((c < o) & (r < lim) & (body > eb / 4)).astype(bool)
    lx = ((c > o) & (r > lim) & (body > eb / 2)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
