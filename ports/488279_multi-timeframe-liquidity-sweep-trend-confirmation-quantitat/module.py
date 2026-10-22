"""Sweeps of the previous 20-bar low (high), broker days, with a bias from the day's last 4-hour bar (its high against the 10-day highest of those 4-hour lows): a sweep of the low in a bullish bias goes long, a sweep of the high in a bearish bias goes short, with a stop 1.5 ATR 14 beyond and a target 3 ATR from the signal bar's low (high); reversing.
Port of FMZ strategy #488279 "Multi Timeframe Liquidity Sweep Trend Confirmation Quantitative Trading Strategy" (High-Win-Rate Liquidity AI).

FMZ source id: 488279

Source
    https://www.fmz.com/strategy/488279 (PineScript v5, FMZ last modified 2025-03-26 15:18:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 192-244), high_tf "240"; SL 1.5 ATR; TP 3 ATR; 100 % of equity
    h4_high = security("240", high);  h4_low = security("240", low);  trend = h4_high > highest(h4_low, 10) ? 1 : -1
    low < lowest(low, 20)[1] and trend == 1 -> entry BUY + exit(limit = low + 3 atr, stop = low - 1.5 atr)
    high > highest(high, 20)[1] and trend == -1 -> entry SELL + exit(limit = high - 3 atr, stop = high + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 240-minute request from a daily chart is a lower time frame: its value is the day's last 4-hour
      bar (as #436765), with the 4-hour bars counted from the broker day's start (six per day), built from
      minutes in precompute; the 10-bar highest runs over those daily values. The bracket is set on the
      signal bar from its low / high and sent as fractions of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256). A later same-side signal while held re-sends the
      bracket; the port keeps the opening levels, mark trailing_stop_pending (as #434428). An entry on the
      other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, 20-bar sweeps with a 4-hour bias and an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 4-hour blocks from its start.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488279_sweep20_h4_bias_atr_bracket_reversal"
FAMILY = "liquidity_sweep"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_factor": [1.5, 2.5],
    "tp_factor": [3.0, 5.0],
}
DEFAULT_PARAMS = {"sl_factor": 1.5, "tp_factor": 3.0, "sweep": 20, "bias": 10, "atr_length": 14}


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
    # 4-hour bars counted from each broker day's start (17:00 America/New_York): six per day
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=240))
    h4 = df["high"].groupby([lab, blk]).max()
    l4 = df["low"].groupby([lab, blk]).min()
    day4 = h4.index.get_level_values(0)
    keep = ~day4.duplicated(keep="last")                     # the day's last 4-hour bar
    bars["h4_high"] = pd.Series(h4.to_numpy()[keep], index=day4[keep]).reindex(bars.index).to_numpy()
    bars["h4_low"] = pd.Series(l4.to_numpy()[keep], index=day4[keep]).reindex(bars.index).to_numpy()
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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    trend_up = bars_df["h4_high"] > bars_df["h4_low"].rolling(int(p["bias"])).max()
    n = int(p["sweep"])
    le = (lo < lo.rolling(n).min().shift(1)) & trend_up
    se = (h > h.rolling(n).max().shift(1)) & ~trend_up
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_length"]))
    a, b = atr * float(p["sl_factor"]), atr * float(p["tp_factor"])
    lvl = {"l_sl": lo - a, "l_tp": lo + b, "s_sl": h + a, "s_tp": h - b}
    return le & ~se, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
