"""Stochastic 14 / 3 / 3 K-D crossings under 20 / over 80 confirmed by the 30-minute Stochastic of the day's last half hour, broker days: the up-cross goes long and the down-cross goes short, each with a 1.7 % target and a 1.7 % stop from the signal close; reversing.
Port of FMZ strategy #482837 "Multi Timeframe Stochastic Oscillator Swing Trading Strategy with Dynamic Take Profit and Stop Loss" (Swing Fairas Oil).

FMZ source id: 482837

Source
    https://www.fmz.com/strategy/482837 (PineScript v5, FMZ last modified 2025-02-20 14:49:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-137), Stochastic K 14, smooth 3, D 3; "30" security; TP / SL 1.7 %
    buy = crossover(k, d) and k < 20 and kHTF < 20 and kHTF > dHTF;  sell = crossunder(k, d) and k > 80 and kHTF > 80 and kHTF < dHTF
    buy -> entry Long + exit(limit = close x 1.017, stop = close x 0.983);  sell -> entry Short + exit(limit = close x 0.983, stop = close x 1.017)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "30" is a LOWER time frame than the daily chart, requested without lookahead: each day gets the
      30-minute K and D of its last 30-minute block (as #436765 / #473411), built in precompute from the
      minutes of the broker day (30-minute blocks from the day's start; the 17:00 New York start is on
      the half-hour grid). dHTF nests kHTF inside a "30" request, so it is the 30-minute D (SMA 3 of the
      30-minute K).
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while held re-sends
      the bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, Stochastic crossings with a 30-minute confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 30-minute blocks from its start; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482837_stoch14_kd_cross_last_30min_confirm_1_7pct_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_length": [14, 9],
    "tp_sl_pct": [1.7, 3.0],
}
DEFAULT_PARAMS = {"k_length": 14, "tp_sl_pct": 1.7, "smooth_k": 3, "d_length": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _stoch_kd(h, lo, c, n, sk, dl):
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(sk).mean()
    return k, k.rolling(dl).mean()


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    day_start = first.loc[bars.index]
    bars.index = pd.DatetimeIndex(day_start.values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    ny = df.index.tz_convert("America/New_York")
    start = (ny + pd.Timedelta(hours=7)).normalize() - pd.Timedelta(hours=7)      # the day's 17:00 New York
    blk = np.asarray((ny - start) // pd.Timedelta(minutes=30))
    key = pd.MultiIndex.from_arrays([lab, blk])
    g = df.groupby(key)
    hb = g.agg({"high": "max", "low": "min", "close": "last"})
    k30, d30 = _stoch_kd(hb["high"], hb["low"], hb["close"], int(p["k_length"]), int(p["smooth_k"]),
                         int(p["d_length"]))
    last = pd.DataFrame({"k": k30, "d": d30}).groupby(level=0).tail(1).droplevel(1)   # the day's last block
    bars["k30"] = last["k"].reindex(day_start.index).to_numpy()
    bars["d30"] = last["d"].reindex(day_start.index).to_numpy()
    return bars


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k, d = _stoch_kd(h, lo, c, int(p["k_length"]), int(p["smooth_k"]), int(p["d_length"]))
    kh, dh = bars_df["k30"], bars_df["d30"]
    le = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20) & (kh < 20) & (kh > dh)
    se = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80) & (kh > 80) & (kh < dh)
    q = float(p["tp_sl_pct"]) / 100
    lvl = {"l_sl": c * (1 - q), "l_tp": c * (1 + q), "s_sl": c * (1 + q), "s_tp": c * (1 - q)}
    return le, se, lvl


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
