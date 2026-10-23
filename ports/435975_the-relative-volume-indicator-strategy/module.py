"""Broker days: the RSI 14 crossing over 70 on a bar with relative volume (volume / SMA 14) above 1.5 goes long, closed when the RSI falls under 69; the RSI crossing under 35 on such a bar goes short, closed when the RSI rises over 35; reversing.
Port of FMZ strategy #435975 "The Relative Volume Indicator Strategy" (Relative Volume & RSI Pop (gary_trades)).

FMZ source id: 435975

Source
    https://www.fmz.com/strategy/435975 (PineScript v4, FMZ last modified 2023-12-20 15:12:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 122-159), RSI 14, 70 / 35; RVOL 14, threshold 1.5; exits RSI 69 / 35
    LongCondition = crossover(rsi, 70) and volume / sma(volume, 14) > 1.5 -> entry Long;  rsi < 69 -> close Long
    ShortCondition = crossunder(rsi, 35) and RVOL > 1.5 -> entry Short;  rsi > 35 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Relative volume is the bar's volume over its own SMA 14. A close acts only on a position the bar's
      entries leave unchanged (call order); an entry bar never meets its own side's close test. REVERSAL
      INTENDED. margin settings are sizing. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI breakouts on relative-volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): margin_long 100, margin_short 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the relative volume volume / sma(volume, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435975_rsi_pop_relative_volume_daily_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rvol_threshold": [1.5, 2.0],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_top": 70.0, "rsi_bottom": 35.0, "rvol_len": 14, "rvol_threshold": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    av = v.rolling(int(p["rvol_len"])).mean()
    rv = (v / av.where(av != 0)) > float(p["rvol_threshold"])
    top, bot = float(p["rsi_top"]), float(p["rsi_bottom"])
    long_c = ((r > top) & (r.shift(1) <= top) & rv).to_numpy()
    short_c = ((r < bot) & (r.shift(1) >= bot) & rv).to_numpy()
    close_l = (r < 69).to_numpy()
    close_s = (r > 35).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            le[i], pos = True, 1
        elif short_c[i] and pos != -1:
            se[i], pos = True, -1
        elif pos == 1 and close_l[i]:
            lx[i], pos = True, 0
        elif pos == -1 and close_s[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
