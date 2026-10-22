"""Weekly-EMA momentum with a caution filter and a ratcheting swing stop, daily bars, long only: from flat, the close above the weekly EMA 20 without caution goes long; a close under the ratcheted 7-bar
swing-low stop (less one ATR(5), or 0.2 ATR in caution) or under the weekly EMA closes.
Port of FMZ strategy #444020 "Bitcoin Momentum Trailing Stop Strategy" (Bitcoin Momentum Strategy (ZenAndTheArtOfTrading)).

FMZ source id: 444020

Source
    https://www.fmz.com/strategy/444020 (PineScript v5, FMZ last modified 2024-03-08 16:20:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 162-223), higher time frame W, EMA 20; ATR 5; trail source low, lookback 7, caution multiplier 0.2; dates (all)
    htfEma = security(W, ema(close, 20))[1] (non-repainting form);  bullish = close > htfEma;  caution = bullish and (highest(high, 7) - low > 1.5 atr or close < ema20)
    bullish and flat and not caution -> entry Buy, trailStop = na;  long: trailStop = max(trailStop, highest(low, 7) - (caution[1] ? 0.2 atr : atr));  close < trailStop or close < htfEma -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() without lookahead is read as the last completed broker week
      (Monday to Friday by broker-day label), built from the module's own bars; the function's [1]
      then shifts it one daily bar, as written. The stop ratchets on the bar close and the exit is a
      bar-close test filled at the next open. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, weekly trend with a caution filter; ratcheting swing stop at the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444020_weekly_ema_momentum_ratchet_swing_stop_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [20, 10],
    "trail_lookback": [7, 14],
}
DEFAULT_PARAMS = {"ema_length": 20, "trail_lookback": 7, "atr_length": 5, "trail_multi": 0.2}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ema_length"])
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk = c.groupby(week).last()
    wema = wk.ewm(span=n, adjust=False).mean().shift(1)    # last completed week
    htf = pd.Series(wema.reindex(week).to_numpy(), index=c.index).shift(1)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_length"]))
    ema = c.ewm(span=n, adjust=False).mean()
    bull = c > htf
    caution = bull & (((h.rolling(7).max() - lo) > atr * 1.5) | (c < ema))
    lb = int(p["trail_lookback"])
    temp = (lo.rolling(lb).max() - np.where(caution.shift(1, fill_value=False), atr * float(p["trail_multi"]), atr)).to_numpy()
    bv, cv_ = bull.to_numpy(), caution.to_numpy()
    cl, hv_ = c.to_numpy(dtype=float), htf.to_numpy()
    m = len(cl)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, trail = False, np.nan
    for i in range(m):
        if bv[i] and not held and not cv_[i]:
            le[i], trail = True, np.nan
        if held and not np.isnan(temp[i]) and (np.isnan(trail) or temp[i] > trail):
            trail = temp[i]
        if held and ((not np.isnan(trail) and cl[i] < trail) or (not np.isnan(hv_[i]) and cl[i] < hv_[i])):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
