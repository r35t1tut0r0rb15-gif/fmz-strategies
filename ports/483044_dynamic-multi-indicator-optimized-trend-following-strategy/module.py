"""Ichimoku cloud side with the MACD histogram, the last completed week's close-vs-SMA 50 and a Bollinger 20 / 2 width over 0.02, 2-day bars: above the cloud with the weekly trend up goes long, below with it down goes short, each with a 1.5 ATR 14 stop from the signal close; reversing.
Port of FMZ strategy #483044 "Dynamic Multi Indicator Optimized Trend Following Strategy" (Momentum Edge Strategy - 1D BTC Optimized).

FMZ source id: 483044

Source
    https://www.fmz.com/strategy/483044 (PineScript v6, FMZ last modified 2025-02-21 10:46:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-137), ATR 14 x 1.5; BB width threshold 0.02; Ichimoku 9 / 26 / 52 (undisplaced); MACD 12 / 26 / 9; weekly close > SMA 50; MPL 2.0 notice (FIWB)
    long = close above spanA and spanB and hist > -0.05 and security("W", close > sma(close, 50)) and bbWidth > 0.02 -> entry Long + exit(stop = close - 1.5 atr)
    short = close below both spans and hist < 0 and not weekly trend and bbWidth > 0.02 -> entry Short + exit(stop = close + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the histogram test "> -0.05" is a price amount; read at the header's ETH_USDT prices
      (about 3000) as -0.05 / 3000 = -1.667e-05 of the close (as #440456 reads price units). The stop's
      squeeze branch (lowest / highest of 14 bars) cannot occur with the width filter on entry.
    * The weekly security has no lookahead: each 2-day bar reads the weekly value of the last broker week
      (Monday label) completed by the bar's last broker day (a week completes with its Friday), built in
      precompute from the minutes (as #440503); a week ends with its Friday broker day and a weekend
      broker day (crypto) opens the next week, so no week is read before its last day. The spans are used
      undisplaced, as written.
    * The conditions are states and repeat while held, each re-sending the stop from the new close; the
      port fixes the stop at the opening signal close and sends it as a fraction of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256), mark
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. The MPL 2.0 notice is kept with the verbatim copy (ported, stated). Bars are blocks of
      two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute.
      FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop as a fraction of the fill.
    2 generic: ADAPT, the -0.05 histogram level read as a fraction of the close at the header's prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone); broker weeks end Friday 17:00 New York.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483044_ichimoku_side_macd_weekly_sma50_bbwidth_atr_stop_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_multiplier": [1.5, 2.5],
    "bb_width_threshold": [0.02, 0.05],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.5, "bb_width_threshold": 0.02, "atr_length": 14, "hist_level": -1.667e-05,
                  "weekly_sma": 50, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    days = int(p["days"])
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    key = np.asarray((lab - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    last_lab = pd.Series(lab, index=df.index).groupby(key).max()
    # weekly closes by broker week ending with its Friday label (a weekend label opens the next week),
    # each week keyed by its Monday, and the weekly trend close > SMA 50
    def week_key(d):
        d2 = d + pd.Timedelta(days=2)
        return d2 - pd.to_timedelta(d2.weekday, unit="D")

    wk = week_key(lab)
    wclose = pd.Series(df["close"].to_numpy(), index=wk).groupby(level=0).last()
    wsma = wclose.rolling(int(p["weekly_sma"])).mean()
    wtrend = (wclose > wsma).astype(float).where(wsma.notna())
    ll = pd.DatetimeIndex(last_lab.loc[bars.index].values)
    kll = week_key(ll)
    done = kll.where(ll.weekday == 4, kll - pd.Timedelta(days=7))      # last week completed by the bar
    pos = wtrend.index.searchsorted(done, side="right") - 1
    vals = np.where(pos >= 0, wtrend.to_numpy()[np.clip(pos, 0, None)], np.nan)
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    bars["w_trend"] = vals
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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(n).max() + lo.rolling(n).min()) / 2

    sa, sb = (mid(9) + mid(26)) / 2, mid(52)
    above, below = (c > sa) & (c > sb), (c < sa) & (c < sb)

    def ema(x, n):
        return x.ewm(span=n, adjust=False).mean()

    macd = ema(c, 12) - ema(c, 26)
    hist = macd - ema(macd, 9)
    w = bars_df["w_trend"]
    basis, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    width = (4 * sd) / basis
    thr = float(p["bb_width_threshold"])
    le = above & (hist > float(p["hist_level"]) * c) & (w == 1) & (width > thr)
    se = below & (hist < 0) & (w == 0) & (width > thr)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atr_length"])) * float(p["atr_multiplier"])
    return le & ~se, se, {"l_sl": c - a, "s_sl": c + a}


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
