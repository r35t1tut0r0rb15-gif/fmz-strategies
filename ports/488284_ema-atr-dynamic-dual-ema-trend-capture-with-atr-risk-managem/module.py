"""EMA 9 / 15 crosses confirmed by the close with a 1 ATR stop and a 1.5 R target, broker days: EMA 9 crossing above
EMA 15 with the close above both goes long; the mirror goes short; each trade has a stop 1 ATR from the signal close
and a target 1.5 times as far.
Port of FMZ strategy #488284 "动态双EMA趋势捕捉与ATR风控量化策略-Dynamic-Dual-EMA-Trend-Capture-with-ATR-Risk-Management-Quantitative-Strategy" (9 & 15 EMA Scalping Strategy).

FMZ source id: 488284

Source
    https://www.fmz.com/strategy/488284 (PineScript v5, FMZ last modified 2025-03-26 15:44:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 175-205), EMA 9 / 15, ATR 14 x 1.0, RR 1.5
    buy = crossover(ema9, ema15) and close > ema9 and close > ema15;  sell mirrored
    entry + exit(stop = close -+ 1 ATR, limit = close +- 1.5 x 1 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = rr x that, shifted one bar
      inside stops() and re-based on the fill (house rule).
    * A same-side signal while held (a second cross after an unconfirmed opposite cross) re-places the bracket: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, EMAs and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488284_ema9_15_cross_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.0, 2.0],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 15, "atr_len": 14, "sl_mult": 1.0, "rr": 1.5}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > f) & (c > s)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < f) & (c < s)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
