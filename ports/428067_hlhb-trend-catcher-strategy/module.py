"""HLHB trend catcher, broker days: EMA 5 crossing EMA 10 on the same bar as RSI 10 crossing 50, with
ADX(14) at or above 25, goes long (both up) or short (both down); each trade has a take-profit and a
stop in points.
Port of FMZ strategy #428067 "HLHB Trend Catcher Strategy" (Hucklekiwi Pip HLHB Trend-Catcher System).

FMZ source id: 428067

Source
    https://www.fmz.com/strategy/428067 (PineScript v3, FMZ last modified 2023-09-28 11:44:04).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 198-320), EMA 5 / 10, RSI 10, ADX 14 >= 25, TP 400 / SL 150 points
    long = crossover(ema5, ema10) and crossover(rsi10, 50) and adx >= 25; short mirrors
    exit(profit = 400, loss = 150, trail_points = 150) ticks; close_all Friday at or after 16:00

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tick distances become tp_atr / sl_atr x Wilder ATR(14) of the signal bar (as
      fractions of its close, shifted one bar inside stops(), re-based on the fill). On the source's
      daily BTC (tick 0.1) 40 / 15 USD is about 0.04 / 0.015 ATR (the author wrote them as FX pips);
      the grid adds wider values. Decision owed: the intended distances.
    * trail_points without trail_offset arms no trailing stop (as #427894): not ported.
    * The Friday 16:00 close cannot fire on the daily header chart (the daily bar's hour is 0): not
      ported.
    * ADX as written (rma of tr, fixnan). Stop module: portfolio_kwargs {} (driver D4);
      REVERSAL INTENDED.
    * Daily bars are broker days; stops on daily bars: mark coarse_bar_stop. FREQ = "1D".

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the weekly close is not ported.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428067_hlhb_trend_catcher"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.04, 2.0],
    "sl_atr": [0.015, 1.0],
    "adx_min": [25, 20],
}
DEFAULT_PARAMS = {"ema_fast": 5, "ema_slow": 10, "rsi_len": 10, "adx_min": 25, "adx_len": 14, "di_len": 14,
                  "tp_atr": 0.04, "sl_atr": 0.015, "atr_length": 14}


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


def _fixnan(x):
    """Pine fixnan: an na value takes the last non-na value of the same series (past only)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _tr(bars):
    pc = bars["close"].shift(1)
    return pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                     axis=1).max(axis=1, skipna=False)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    d = c.diff()
    k = int(p["rsi_len"])
    ru, rd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + ru / rd)).where(ru != 0, 0.0).where(rd != 0, 100.0).where(ru.notna() & rd.notna())
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    n = int(p["di_len"])
    trr = _rma(_tr(bars_df), n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    ok = adx >= p["adx_min"]
    long_e = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (rsi > 50) & (rsi.shift(1) <= 50) & ok).astype(bool)
    short_e = ((ef < es) & (ef.shift(1) >= es.shift(1)) & (rsi < 50) & (rsi.shift(1) >= 50) & ok).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _rma(_tr(bars_df), int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
