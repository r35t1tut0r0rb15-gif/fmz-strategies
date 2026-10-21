"""Low-volatility buys held about six bars, broker days, long only: from flat, the ATR 14 as a fraction of the close under its 70-bar average buys; after more than 5 bars in the trade the long is closed.
Port of FMZ strategy #438022 "Buy Low Volatility VS Buy High Volatility Strategy" (I11L - Better Buy Low Volatility or High Volatility?).

FMZ source id: 438022

Source
    https://www.fmz.com/strategy/438022 (PineScript v5, FMZ last modified 2024-01-08 11:33:58).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 112-145), mode Buy low Volatility; target ratio 1; ATR 14 (average over 70 bars); sell after 5 bars
    ratio = (atr(14) / close) / sma(atr(14) / close, 70);  ratio < 1 -> entry Buy;  bars counted while a trade is open;  count > 5 -> count := 0, exit(Close, limit = close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is a sell limit at the close of the counting bar, active from the next bar: the port reads
      it as a close at the next open (the limit fills at the open when the bar opens at or above it;
      otherwise later in the bar, or not at all: not modelled). The count is raised on every bar with a
      trade open at the bar close and reset when the exit is sent. Long only. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the limit at the close read as a close at the next open.
    2 generic: PASS, ATR ratio and a bar count.
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

NAME = "fmz_438022_low_volatility_buy_timed_exit"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "target_ratio": [1.0, 0.8],
    "hold_bars": [5, 10],
}
DEFAULT_PARAMS = {"target_ratio": 1.0, "hold_bars": 5, "atr_len": 14, "mode": "low"}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["atr_len"])
    atrp = _atr(bars_df, n) / c
    ratio = atrp / atrp.rolling(n * 5).mean()
    tgt = float(p["target_ratio"])
    buy = (ratio < tgt if p["mode"] == "low" else ratio > tgt).to_numpy()
    hold = int(p["hold_bars"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, cnt, pend_e, pend_x = 0, 0, False, False
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        if pos == 1:
            cnt += 1
        if buy[i] and pos == 0 and i + 1 < m:
            le[i], pend_e = True, True
        if cnt > hold:
            cnt = 0
            if pos == 1:
                lx[i], pend_x = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
