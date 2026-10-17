"""EMA 9 / 21 crosses on the EMA 50 side with RSI 14 in a middle band and a 0.5 % stop / 1 % target, daily
(broker-day) bars: EMA 9 crossing above EMA 21 with the close above EMA 50 and RSI between 40 and 70 goes long; the
mirror (RSI between 30 and 60) goes short.
Port of FMZ strategy #483120 "多重均线交叉与RSI动量联动短线自适应交易策略-Multi-EMA-Crossover-with-RSI-Momentum-Adaptive-Scalping-Strategy" (RSI + EMA Scalping Strategy).

FMZ source id: 483120

Source
    https://www.fmz.com/strategy/483120 (PineScript v5, FMZ last modified 2025-02-21 14:27:45).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 97-123), EMA 9 / 21 / 50, RSI 14, SL 0.5 %, TP 1 %
    long = crossover(ema9, ema21) and close > ema50 and 40 < rsi < 70; entry + exit(stop = close x 0.995,
    limit = close x 1.01); short = crossunder and close < ema50 and 30 < rsi < 60 (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar's close: 0.5 % / 1 % fractions re-based on the fill
      (house rule). A same-side signal while held re-places it: mark trailing_stop_pending; the port keeps the entry's
      bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4).
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984); stops on daily
      bars: coarse_bar_stop. FREQ = "1D" from the backtest header ("Scalping" in the title is a label).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483120_ema9_21_ema50_rsi_band_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.5, 2.0],
    "tp_pct": [1.0, 4.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sl_pct": 0.5, "tp_pct": 1.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e9, e21, e50 = (c.ewm(span=n, adjust=False).mean() for n in (9, 21, 50))
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((e9 > e21) & (e9.shift(1) <= e21.shift(1)) & (c > e50) & (rsi > 40) & (rsi < 70)).astype(bool)
    short_e = ((e9 < e21) & (e9.shift(1) >= e21.shift(1)) & (c < e50) & (rsi < 60) & (rsi > 30)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
