"""PowerZone order-block breakouts from flat with a zone-sized bracket, broker days: a bearish candle six bars back
followed by five bullish candles marks a bullish zone (its open to its low); a close above the zone's top goes long
when flat, with a target 1.5 zone heights above the close and a stop one zone height below the zone; the mirror for
bearish zones goes short.
Port of FMZ strategy #488909 "PowerZone交易策略-PowerZone-Trading-Strategy" (PowerZone Trading Strategy).

FMZ source id: 488909

Source
    https://www.fmz.com/strategy/488909 (PineScript v6, FMZ last modified 2025-03-31 17:34:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 146-208), periods 5, threshold 0 %, bodies (no wicks), TP 1.5, SL 1.0
    bull zone = close[6] < open[6] and closes > opens on bars 1..5 and |close[6] - close[1]| / close[6] >= 0 %
    zone high = open[6], low = low[6]; long = bull zone and close > zone high and flat
    -> entry + exit(limit = close + 1.5 x height, stop = zone low - 1.0 x height); bear zones mirrored (high[6] / open[6])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar, from the zone: tp_stop = 1.5 x height / close, sl_stop = (close -
      zone low + height) / close (mirrored for shorts), shifted one bar inside stops(), re-based on the fill.
    * Entries only from flat: simulate() follows the house bracket on bars (from the fill bar), as the desktop's
      flat-only bracket ports. Bull and bear zones cannot both hold on one bar. Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, candle sequences and zone heights.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488909_powerzone_breakout_bracket"
FAMILY = "price_action_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "periods": [5, 3],
    "tp_factor": [1.5, 3.0],
}
DEFAULT_PARAMS = {"periods": 5, "threshold": 0.0, "use_wicks": False, "tp_factor": 1.5, "sl_factor": 1.0}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    n = int(p["periods"])
    ob = n + 1
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dsl, dtp = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - t_)):
                pos = 0
        if i < ob or pos != 0 or i + 1 >= m:
            continue
        rel = abs((c[i - ob] - c[i - 1]) / c[i - ob]) * 100 >= p["threshold"]
        ups = sum(c[i - k] > o[i - k] for k in range(1, n + 1))
        dns = sum(c[i - k] < o[i - k] for k in range(1, n + 1))
        if c[i - ob] < o[i - ob] and ups == n and rel:
            zh = h[i - ob] if p["use_wicks"] else o[i - ob]
            zl = lo[i - ob]
            if c[i] > zh:
                ht = zh - zl
                s, t = (c[i] - (zl - ht * p["sl_factor"])) / c[i], ht * p["tp_factor"] / c[i]
                if s > 0 and t > 0:
                    le[i], dsl[i], dtp[i], pos, entry_i, s_, t_ = True, s, t, 1, i + 1, s, t
                    continue
        if c[i - ob] > o[i - ob] and dns == n and rel:
            zh = h[i - ob]
            zl = lo[i - ob] if p["use_wicks"] else o[i - ob]
            if c[i] < zl:
                ht = zh - zl
                s, t = ((zh + ht * p["sl_factor"]) - c[i]) / c[i], ht * p["tp_factor"] / c[i]
                if s > 0 and t > 0:
                    se[i], dsl[i], dtp[i], pos, entry_i, s_, t_ = True, s, t, -1, i + 1, s, t
    return le, se, dsl, dtp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dsl, dtp = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(dsl, index=idx).shift(1), "tp_stop": pd.Series(dtp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
