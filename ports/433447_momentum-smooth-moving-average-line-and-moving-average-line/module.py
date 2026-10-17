"""EMA 49 / 9 crosses on the side of a dominant ALMA, broker days, as written: the EMA 49 crossing ABOVE the EMA 9 with the
two previous closes above the ALMA 130 goes long (unless the stochastic RSI K is above 75), the EMA 49 crossing below
the EMA 9 with the two previous closes below the ALMA goes short (unless K is under 25). Stochastic-RSI extremes close
positions, and each trade carries a 5.49 % stop and a 3 % target.
Port of FMZ strategy #433447 "Momentum Smooth Moving Average Line and Moving Average Line Crossover Strategy" (ALMA/EMA Strategy).

FMZ source id: 433447

Source
    https://www.fmz.com/strategy/433447 (PineScript v5, FMZ last modified 2023-11-27 17:35:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-277), ALMA 130 / 0.775 / 4.5; EMA 49 (slow) / 9 (fast); stoch RSI 3 / 15 / 14 / 8; TP 3 %, SL 5.49 %
    crossover(ema49, ema9) and close[2] > alma[2] and close[1] > alma[1] -> entry long;  crossunder and below -> entry short
    k > 75 -> cancel the long entry;  k < 25 -> cancel the short entry (same bar)
    crossunder(k, d) and k > 92 -> close long;  crossover(k, d) and k < 8 -> close short;  exit(limit = avg (1 +/- 3 %), stop = avg (1 -/+ 5.49 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the long follows the SLOW EMA crossing above the fast one. strategy.cancel on the
      signal bar withdraws that bar's entry order, so a long needs K <= 75 and a short K >= 25.
    * K = SMA 3 of the 8-bar stochastic of RSI 14, D = SMA 15 of K. The bracket is symmetric: sl_stop
      0.0549, tp_stop 0.03 of the fill. An extreme close on the bar of an opposite entry is left to the
      entry (strategy.entry reverses): REVERSAL INTENDED.
    * Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; stops on daily bars: mark coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, average crosses, an ALMA filter and oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433447_alma_ema_cross_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slow": [49, 30],
    "alma_len": [130, 65],
}
DEFAULT_PARAMS = {"slow": 49, "fast": 9, "alma_len": 130, "alma_offset": 0.775, "alma_sigma": 4.5, "k_s": 3, "d_s": 15,
                  "rsi_len": 14, "stoch_len": 8, "tp_pct": 0.03, "sl_pct": 0.0549}


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


def _alma(x, n, offset, sigma):
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))
    w = w / w.sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    al = _alma(c, int(p["alma_len"]), float(p["alma_offset"]), float(p["alma_sigma"]))
    e1 = c.ewm(span=int(p["slow"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["fast"]), adjust=False).mean()
    x1 = (e1 > e2) & (e1.shift(1) <= e2.shift(1))
    x2 = (e1 < e2) & (e1.shift(1) >= e2.shift(1))
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    sl_ = int(p["stoch_len"])
    rl, rh = r.rolling(sl_).min(), r.rolling(sl_).max()
    k = (100 * (r - rl) / (rh - rl)).rolling(int(p["k_s"])).mean()
    d = k.rolling(int(p["d_s"])).mean()
    above = (c.shift(2) > al.shift(2)) & (c.shift(1) > al.shift(1))
    below = (c.shift(2) < al.shift(2)) & (c.shift(1) < al.shift(1))
    le = (x1 & above & ~(k > 75)).to_numpy()
    se = (x2 & below & ~(k < 25)).to_numpy()
    lx = ((k < d) & (k.shift(1) >= d.shift(1)) & (k > 92)).to_numpy() & ~se
    sx = ((k > d) & (k.shift(1) <= d.shift(1)) & (k < 8)).to_numpy() & ~le
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
