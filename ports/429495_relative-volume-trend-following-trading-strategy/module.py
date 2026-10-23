"""Up bars on above-average volume (over the SMA 5 of volume) in a calm market (2 x ATR 10 above 2 x the 20-bar sd), broker days, long only: such a bar goes long; the low reaching a ratcheting low - 2 ATR trailing line, or a wide bearish engulfing bar in a volatile market, closes.
Port of FMZ strategy #429495 "Relative Volume Trend Following Trading Strategy" ([KL] Relative Volume Strategy).

FMZ source id: 429495

Source
    https://www.fmz.com/strategy/429495 (PineScript v4, FMZ last modified 2023-10-17 16:19:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-256), ATR 10 x 2; BB 20, 2 sd; volume SMA 5; pyramiding 1
    close > open and volume > sma(volume, 5) and 2 atr(10) > 2 stdev(close, 20) -> entry Long
    stop := flat ? low - 2 atr : max(stop, low - 2 atr);  long and low <= stop -> close;  long and close < open and not calm and engulfing and range > 2 atr -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line runs as written, in source order: it ratchets on every bar while long before the
      test, so the exit fires when the low reaches the previous level; the clean-up resets it to 0 while
      flat, so it restarts from the first held bar. The exits are close tests filled at the next open. The
      adds the entry line allows ("adding") are blocked by pyramiding 1. Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based trailing line.
    2 generic: PASS, relative-volume up bars in calm markets with an ATR trailing exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > sma(volume, 5); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); the 2016 start dropped.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429495_relative_volume_up_bar_calm_atr_trailing_line_long"
FAMILY = "volume_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 20],
    "vol_len": [5, 10],
}
DEFAULT_PARAMS = {"atr_len": 10, "vol_len": 5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    atr2 = (_rma(tr, int(p["atr_len"])) * 2).to_numpy()
    sd2 = (2 * c.rolling(20).std(ddof=0)).to_numpy()
    calm = atr2 > sd2
    ent = ((c > o) & (v > v.rolling(int(p["vol_len"])).mean())).to_numpy() & calm
    body = (c - o).abs()
    engulf = ((lo < lo.shift(1)) & (h > h.shift(1)) & (body > body.shift(1))).to_numpy()
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, pend_in, pend_out = False, False, False
    stop = 0.0
    for i in range(m):
        if pend_in:
            held, pend_in = True, False
        if pend_out:
            held, pend_out = False, False
        if not held:
            stop = lv[i] - atr2[i]
        else:
            stop = max(stop, lv[i] - atr2[i])
        if ent[i] and not held and not pend_in and i + 1 < m:
            le[i], pend_in = True, True
        if held:
            if lv[i] <= stop or (cv[i] < ov[i] and not calm[i] and engulf[i] and hv[i] - lv[i] > atr2[i]):
                lx[i], pend_out = True, True
        if not held:
            stop = 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
