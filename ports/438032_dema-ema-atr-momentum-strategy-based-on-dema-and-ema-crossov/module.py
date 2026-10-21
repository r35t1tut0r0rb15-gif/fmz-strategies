"""DEMA 10 crossing under the EMA 25 with high daily volatility, 1-hour bars, short only: from flat, the cross under with the previous broker day's ATR 14 (as a percent of the current close) above the
previous day's EMA 20 of the daily ATR percent goes short. The only exit is gated on a long position, so it is never sent: the first short is held.
Port of FMZ strategy #438032 "DEMA与EMA交叉结合ATR波动率的短期策略Momentum-Strategy-Based-on-DEMA-and-EMA-Crossover-with-ATR-Volatility-Filter" (DEMA/EMA & VOL SHORT).

FMZ source id: 438032

Source
    https://www.fmz.com/strategy/438032 (PineScript v4, FMZ last modified 2024-01-08 14:14:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-255), DEMA 10, EMA 25; ATR timeframe D, ATR 14, MA EMA 20; stop type 5.0 (true: ATR stop), SL multiplier 1; minimum profit 20
    shortSignal = crossunder(dema, ema) and atrp > maFilter and position_size == 0 and not na(atr);  atrp = security(D, atr(14)) / close x 100;  maFilter = security(D, ema(atrp, 20))
    entry short;  exit(Short exit, limit = exitSignal ? close : na, stop = highest(high, 4) - atr, when = position_size > 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: the previous
      broker day's ATR 14 and EMA 20 of the daily ATR percent (daily close), built from the module's own
      bars; the chart's atrp divides that ATR by the current 1-hour close. The exit carries
      when = position_size > 0, which is never true in a short-only script, so no exit is ever placed:
      the first short is held to the end of the data, as written (owed: probably when = position_size < 0).
      Short only: Opposite entries cannot occur. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher-timeframe values from completed days.
    2 generic: PASS, DEMA / EMA crossing and an ATR-percent filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily values.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438032_dema_ema_cross_short_held"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "ema_len": [25, 50],
}
DEFAULT_PARAMS = {"length": 10, "ema_len": 25, "atr_lookback": 14, "ma_length": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _tr(h, lo, c):
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    atr_1h = _rma(_tr(h, lo, c), 14)
    day = broker_day(bars_df.index)
    d = bars_df.groupby(day).agg({"high": "max", "low": "min", "close": "last"})
    d_atr = _rma(_tr(d["high"], d["low"], d["close"]), int(p["atr_lookback"]))
    d_ma = (d_atr / d["close"] * 100).ewm(span=int(p["ma_length"]), adjust=False).mean()
    atr_prev = pd.Series(d_atr.shift(1).reindex(day).to_numpy(), index=c.index)   # last completed day
    ma_prev = pd.Series(d_ma.shift(1).reindex(day).to_numpy(), index=c.index)
    atrp = atr_prev / c * 100
    x_dn = (dema < ema) & (dema.shift(1) >= ema.shift(1))
    sig = (x_dn & (atrp > ma_prev) & atr_1h.notna()).to_numpy()
    m = len(c)
    se = np.zeros(m, dtype=bool)
    hits = np.flatnonzero(sig[:-1]) if m > 1 else np.array([], dtype=int)
    if len(hits):
        se[hits[0]] = True                               # flat only once: the first short is never closed
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
