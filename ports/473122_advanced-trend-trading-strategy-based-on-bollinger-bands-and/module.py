"""Daily wick rejections of the daily Bollinger 20 / 2 bands, traded on 12-hour bars: after a day whose lower wick is at least its body and pokes under the lower band, a 12-hour high reaching that day's close goes long (if the last daily swing low is under the close); the mirror at the upper band goes short; reversing. The band target and swing stop move every bar and are not ported (pending).
Port of FMZ strategy #473122 "Advanced Trend Trading Strategy Based on Bollinger Bands and Candlestick Patterns" (Trade Entry Detector, based on Wick to Body Ratio when price tests Bollinger Bands).

FMZ source id: 473122

Source
    https://www.fmz.com/strategy/473122 (PineScript v5, FMZ last modified 2024-11-27 14:18:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-195), daily OHLC and BB 20 / 2 from request.security("D"); wick / body >= 1; fill option "Daily Close"; swing levels from pivots (5, 5) of the daily series; size = 1 % of 100000 over the stop distance
    lower wick >= body and daily low < lower band -> long price = daily close;  upper mirror -> short price = daily close
    long price set and high >= it -> (size from close - swing low) entry Long, reset;  short price set and low <= it -> entry Short, reset
    long: exit(limit = daily upper band);  exit(stop = swing low);  short: mirrored  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" requests without lookahead are read as the last broker day completed by the 12-hour bar's
      close (#440503), built in precompute; the swing levels are strict pivots (5, 5) of that daily
      series as seen on the 12-hour bars, kept (var), as written. The order "expiry" is refreshed on
      every bar while a price is set, so it never expires. An entry needs a positive stop distance
      (close over the swing low, or under the swing high); the risk-based size is not ported. The exits
      are re-sent every bar at the current band and swing level, which stops() cannot express (pending,
      mark trailing_stop_pending); positions end at the opposite entry until then. When both entries
      fire on a bar the later (short) call wins (#437773). REVERSAL INTENDED. No sizing code ported. FREQ
      = "12h" from the backtest header (UTC-aligned 12-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, band wick rejections; moving exits described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size (1 % of a 100000 balance) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG473122 (2 members, best partner #473394, Jaccard 0.964); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473122_daily_bb_wick_rejection_12h_entries_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "wick_ratio": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "wick_ratio": 1.0, "mult": 2.0}


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


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    lab = broker_day(df.index)
    d = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    last = pd.Series(df.index, index=df.index).groupby(lab).last()
    n = int(p["length"])
    basis = d["close"].rolling(n).mean()
    dev = float(p["mult"]) * d["close"].rolling(n).std(ddof=0)
    cols = {"d_open": d["open"], "d_high": d["high"], "d_low": d["low"], "d_close": d["close"],
            "d_up": basis + dev, "d_lo": basis - dev}
    day_end = last.to_numpy().astype("datetime64[ns]") + np.timedelta64(1, "m")
    bar_end = bars.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(12, "h")
    k = np.searchsorted(day_end, bar_end, side="right") - 1        # last broker day completed by the close
    kk = np.clip(k, 0, None)
    for name, s in cols.items():
        bars[name] = np.where(k >= 0, s.to_numpy(dtype=float)[kk], np.nan)
    return bars


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    dO, dH, dL, dC = (bars_df[k].to_numpy(dtype=float) for k in ("d_open", "d_high", "d_low", "d_close"))
    d_up, d_lo = bars_df["d_up"].to_numpy(dtype=float), bars_df["d_lo"].to_numpy(dtype=float)
    wr = float(p["wick_ratio"])
    with np.errstate(divide="ignore", invalid="ignore"):
        body = np.abs(dO - dC)
        up_c = ((dH - np.maximum(dO, dC)) / body >= wr) & (dH > d_up)
        lo_c = ((np.minimum(dO, dC) - dL) / body >= wr) & (dL < d_lo)
    ph, pl = _pivot(dH, 1), _pivot(dL, -1)
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sw_h = sw_l = lp = sp = np.nan
    for t in range(m):
        if ph[t]:
            sw_h = dH[t - 5]
        if pl[t]:
            sw_l = dL[t - 5]
        if lo_c[t]:
            lp = dC[t]
        if up_c[t]:
            sp = dC[t]
        if not np.isnan(lp) and lp != 0 and h[t] >= lp:
            if c[t] - (c[t] if np.isnan(sw_l) else sw_l) > 0:
                le[t] = True
            lp = np.nan
        if not np.isnan(sp) and sp != 0 and lo[t] <= sp:
            if (c[t] if np.isnan(sw_h) else sw_h) - c[t] > 0:
                se[t] = True
            sp = np.nan
    le &= ~se                                    # the later (short) call wins on a mixed bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
