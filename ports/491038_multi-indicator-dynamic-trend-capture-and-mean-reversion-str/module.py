"""EMA 9 / 21 side with the close beyond the SMA 20 and the Bollinger 20 basis and RSI 14 under 60 (over 40), broker days: the long state closes any short and goes long, the short state closes any long and goes short; reversing.
Port of FMZ strategy #491038 "Multi Indicator Dynamic Trend Capture and Mean Reversion Strategy" (Phoenix Pro Strategy).

FMZ source id: 491038

Source
    https://www.fmz.com/strategy/491038 (PineScript v5, FMZ last modified 2025-04-18 09:27:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 179-258), EMA 9 / 21; SMA 20 / 50; RSI 14; BB 20 / 2; pivots / zigzag (plots only)
    ema9 > ema21 and close > sma20 and rsi < 60 and close > basis -> entry Long, close Short;  mirror -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivots and zigzag only plot. The conditions are states; each reverses the other (REVERSAL
      INTENDED). No sizing code. MPL 2.0 source (the notice is kept: Mozilla Public License 2.0,
      © phoenixtradeteam). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA / SMA / RSI / Bollinger states.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_491038_ema9_21_sma20_bb_basis_rsi_state_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emaFastLen": [9, 5],
    "emaSlowLen": [21, 50],
}
DEFAULT_PARAMS = {"emaFastLen": 9, "emaSlowLen": 21, "smaShortLen": 20, "bbLength": 20, "rsiLen": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["emaFastLen"]), adjust=False).mean()
    s = c.ewm(span=int(p["emaSlowLen"]), adjust=False).mean()
    sma = c.rolling(int(p["smaShortLen"])).mean()
    basis = c.rolling(int(p["bbLength"])).mean()
    r = _rsi(c, int(p["rsiLen"]))
    le = (f > s) & (c > sma) & (r < 60) & (c > basis)
    se = (f < s) & (c < sma) & (r > 40) & (c < basis)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
