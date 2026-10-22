"""Trend states 2 % beyond the SMA 50 and SMA 20 / 50 crossings, broker days: a close 2 % above the SMA 50 or the SMA 20 crossing over it goes long, the mirrors go short, each with a 2 % stop and 6 % target from the signal close; reversing.
Port of FMZ strategy #478725 "Adaptive Multi Strategy Dynamic Switching System A Quantitative Trading Strategy Combining Trend Following and Range Oscillation" (Supply & Demand Test 1 - Enhanced).

FMZ source id: 478725

Source
    https://www.fmz.com/strategy/478725 (PineScript v6, FMZ last modified 2025-01-17 16:02:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 73-173), SMA 50 / 20; BB 20 / 2; RSI 14; stop 2 %, target 6 % (trend) / 4 % (range)
    close >= sma50 x 1.02 -> entry Long Trend + exit(2 % / 6 %);  close <= sma50 x 0.98 -> Short Trend;  crossover(sma20, sma50) -> Long MA Crossover + exit;  crossunder -> Short MA Crossover;  range-bound (close == sma50) BB / RSI entries with a 4 % target

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Range-bound" means the close is exactly the SMA 50 (neither above nor below), so the range and RSI
      entries are kept but almost never fire. The trend entries are states and repeat on every bar they
      hold, each re-sending its bracket from that bar's close; with pyramiding 1 a second id on the held
      side is ignored. The opening signal's levels are ported, sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256), and the re-sends are not
      followed (as #434428, mark trailing_stop_pending). On a bar with signals on both sides the later
      call wins (#437773), in the script's order. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, SMA trend states and crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_478725_sma50_trend_band_sma20_cross_pct_bracket_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "band": [0.02, 0.05],
    "tp_trend": [0.06, 0.10],
}
DEFAULT_PARAMS = {"band": 0.02, "tp_trend": 0.06, "tp_range": 0.04, "sl_pct": 0.02}


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
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    c = bars_df["close"]
    slow, fast = c.rolling(50).mean(), c.rolling(20).mean()
    basis = c.rolling(20).mean()
    dev = 2.0 * c.rolling(20).std(ddof=0)
    r = _rsi(c, 14)
    bd = float(p["band"])
    tr_up, tr_dn = c > slow, c < slow
    rng = ~(tr_up | tr_dn) & slow.notna()
    calls = [  # (condition, side, target) in the script's order
        (tr_up & (c >= slow * (1 + bd)), 1, "tp_trend"),
        (tr_dn & (c <= slow * (1 - bd)), -1, "tp_trend"),
        ((fast > slow) & (fast.shift(1) <= slow.shift(1)), 1, "tp_trend"),
        ((fast < slow) & (fast.shift(1) >= slow.shift(1)), -1, "tp_trend"),
        (rng & (c <= (basis - dev) * 0.97), 1, "tp_range"),
        (rng & (c >= (basis + dev) * 1.03), -1, "tp_range"),
        (rng & (r < 30), 1, "tp_range"),
        (rng & (r > 70), -1, "tp_range"),
    ]
    side = pd.Series(0, index=c.index)
    tgt = pd.Series(np.nan, index=c.index)
    for cond, sd, key in calls:
        side = side.where(~cond, sd)
        tgt = tgt.where(~cond, float(p[key]))
    le, se = side == 1, side == -1
    sp = float(p["sl_pct"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tgt), "s_sl": c * (1 + sp), "s_tp": c * (1 - tgt)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
