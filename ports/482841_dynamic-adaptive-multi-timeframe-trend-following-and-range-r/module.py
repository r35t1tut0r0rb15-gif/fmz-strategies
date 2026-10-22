"""Ichimoku 9 / 26 / 52 spans (not displaced) as a regime with MACD 12 / 26 / 9 (SMA signal), RSI 14 and a 14 / 3 / 3 Stochastic, 2-day bars: trend longs above both spans, trend shorts below them, range longs / shorts between them, each with a stop 2 ATR 14 beyond the signal bar's low / high; reversing.
Port of FMZ strategy #482841 "Dynamic Adaptive Multi Timeframe Trend Following and Range Reversal Hybrid Strategy" (Refined Ichimoku with MACD and RSI Strategy).

FMZ source id: 482841

Source
    https://www.fmz.com/strategy/482841 (PineScript v6, FMZ last modified 2025-02-20 14:48:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-177), Ichimoku 9 / 26 / 52 (displacement 26 unused); MACD 12 / 26 / 9 with SMA signal; RSI 14; Stochastic 14 / 3 / 3; ATR 14 x 2; MPL 2.0 notice (FIWB)
    trendLong = close >= spanA and close >= spanB and rsi > 55 and hist > 0 and k > d;  trendShort = close <= both and rsi < 45 and hist < 0 and k < d
    rangeLong = spanB < close < spanA and rsi < 30 and k < 20;  rangeShort = spanB < close < spanA and rsi > 70 and k > 80
    each -> entry (its own id) + exit(stop = low - 2 atr / high + 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are used undisplaced, as written (the displacement input feeds nothing). The "Stochastic
      RSI" is the Stochastic of the price, as written. Default pyramiding refuses a second long under
      another id while long (as #441137), and that id's exit then has no position. The conditions are
      states and repeat while held, each re-sending the stop from the new bar's low / high; the port fixes
      the stop at the opening signal bar and sends it as a fraction of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256), mark trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED); a short called on the same bar
      as a long wins (called later, as #437773). Stop module: portfolio_kwargs {} (driver D4). Stops on
      bars longer than 1 hour: mark coarse_bar_stop. No sizing code. The MPL 2.0 notice is kept with the
      verbatim copy (ported, stated). Bars are blocks of two broker days (17:00 America/New_York) counted
      from 1970-01-01, stamped with their first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR stop as a fraction of the fill.
    2 generic: PASS, Ichimoku regime with MACD / RSI / Stochastic filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482841_ichimoku_regime_macd_rsi_stoch_atr2_stop_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 3.0],
    "conversion_length": [9, 7],
}
DEFAULT_PARAMS = {"atr_mult": 2.0, "conversion_length": 9, "base_length": 26, "span_b_length": 52,
                  "macd_fast": 12, "macd_slow": 26, "macd_signal": 9, "rsi_length": 14, "stoch_length": 14,
                  "stoch_k": 3, "stoch_d": 3, "atr_length": 14, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    conv, base = mid(p["conversion_length"]), mid(p["base_length"])
    sa, sb = (conv + base) / 2, mid(p["span_b_length"])
    above = (c >= sa) & (c >= sb)
    below = (c <= sa) & (c <= sb)
    near = (c > sb) & (c < sa)
    trending = above | below
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["macd_signal"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["stoch_length"])
    rng = h.rolling(n).max() - lo.rolling(n).min()
    k = (100 * (c - lo.rolling(n).min()) / rng.where(rng > 0)).rolling(int(p["stoch_k"])).mean()
    d = k.rolling(int(p["stoch_d"])).mean()
    t_long = trending & above & (r > 55) & (hist > 0) & (k > d)
    t_short = trending & below & (r < 45) & (hist < 0) & (k < d)
    r_long = near & (r < 30) & (k < 20)
    r_short = near & (r > 70) & (k > 80)
    se = t_short | r_short
    le = (t_long | r_long) & ~se
    a = float(p["atr_mult"]) * _atr(bars_df, int(p["atr_length"]))
    return le, se, {"l_sl": lo - a, "s_sl": h + a}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    lx = lf & (lvl["l_sl"].shift(1) >= o)      # marketable at the fill: closed one bar late
    sx = sf & (lvl["s_sl"].shift(1) <= o)
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    return {"sl_stop": sl.where(sl > 0)}


def portfolio_kwargs(**params):
    return {}
