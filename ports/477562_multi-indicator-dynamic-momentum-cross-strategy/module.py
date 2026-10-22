"""A persistent signal state from EMA 5 / 13 / 40 / 55 order and RSI 14, broker days: the state "long" (EMA 5 > 13, EMA 40 > 55, RSI over 50 and its SMA 14) goes long, and the state "short", which as written is EMA 40 above EMA 55 without the long conditions, goes short; reversing.
Port of FMZ strategy #477562 "Multi Indicator Dynamic Momentum Cross Strategy" (EMA Crossover Strategy with RSI Average, Distance, and Signal Persistence).

FMZ source id: 477562

Source
    https://www.fmz.com/strategy/477562 (PineScript v6, FMZ last modified 2025-01-06 14:00:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-225), EMA 5 / 13 / 40 / 55; RSI 14 and its SMA 14; distance windows of 5; RSI 60 / 40 colour states
    neutral = dist(ema5, ema13) < avg of a fresh 5-slot array or ema13 > ema5;  long = ema5 > ema13 and ema40 > ema55 and rsi > 50 and rsi > sma(rsi, 14) and not neutral;  "short" = ema40 > ema55
    close > ema5: long and distUp -> "long", elif short and distUp -> "short", elif neutral, elif rsi > 60 "green", elif rsi < 40 "red" (else kept);  close <= ema5: long, short, green, red, else neutral
    lastSignal "long" -> entry Enter Long;  else "short" -> entry Enter Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The distance arrays are created anew on every bar (four zeros and the current distance), so their
      average is the current distance / 5 and "neutral" reduces to EMA 13 above EMA 5. distUp is the EMA
      40-13 distance growing against the previous bar (true on the first bar). The "short" condition is
      EMA 40 above EMA 55, as written, so the strategy goes short in that up-alignment whenever the long
      conditions fail. A loop keeps the state, which persists above the EMA 5 when no branch applies. The
      entries repeat while the state holds and are ignored on the held side. REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA order / RSI signal state, as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_477562_ema_order_rsi_signal_state_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_avg_length": [14, 28],
    "rsi_mid": [50, 55],
}
DEFAULT_PARAMS = {"rsi_avg_length": 14, "rsi_mid": 50, "rsi_length": 14}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e5, e13, e40, e55 = (c.ewm(span=n, adjust=False).mean() for n in (5, 13, 40, 55))
    r = _rsi(c, int(p["rsi_length"]))
    ra = r.rolling(int(p["rsi_avg_length"])).mean()
    dist = (e5 - e13).abs()
    neutral = ((dist < dist / 5) | (e13 > e5)).to_numpy()
    mid = float(p["rsi_mid"])
    longc = ((e5 > e13) & (e40 > e55) & (r > mid) & (r > ra)).to_numpy() & ~neutral
    shortc = (e40 > e55).to_numpy()
    green, red = (r > 60).to_numpy(), (r < 40).to_numpy()
    d40 = (e40 - e13).abs().to_numpy()
    above = (c > e5).to_numpy()
    m = len(d40)
    state = np.zeros(m, dtype=int)
    st, prev = 0, np.nan
    for i in range(m):
        grow = True if np.isnan(prev) else d40[i] > prev
        if above[i]:
            if longc[i] and grow:
                st = 1
            elif shortc[i] and grow:
                st = 2
            elif neutral[i]:
                st = 3
            elif green[i]:
                st = 4
            elif red[i]:
                st = 5
        else:
            if longc[i]:
                st = 1
            elif shortc[i]:
                st = 2
            elif green[i]:
                st = 4
            elif red[i]:
                st = 5
            else:
                st = 3
        prev = d40[i]
        state[i] = st
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(state == 1, index=ix), false, pd.Series(state == 2, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
