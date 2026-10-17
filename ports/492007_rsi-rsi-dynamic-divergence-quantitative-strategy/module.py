"""RSI 14 regular divergences with a swing (or ATR) bracket, broker days: a confirmed RSI pivot low (5 / 5) whose
price low undercuts the previous pivot's while the RSI is higher goes long; the bearish mirror goes short; each
trade has a stop beyond the 20-bar swing (1 % margin) and a target at twice the risk.
Port of FMZ strategy #492007 "RSI动态背离量化策略-RSI-Dynamic-Divergence-Quantitative-Strategy" (RSI Divergence Strategy - AliferCrypto).

FMZ source id: 492007

Source
    https://www.fmz.com/strategy/492007 (PineScript v6, FMZ last modified 2025-04-25 14:57:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 123-211), RSI 14, pivots 5 / 5, 5-60 bars between pivots, Swing method
    bull = pivotlow(rsi, 5, 5) and low[5] < low at the previous pivot low and rsi[5] > rsi there, in range
    bear = pivothigh(rsi, 5, 5) and high[5] > high at the previous pivot high and rsi[5] < rsi there, in range
    entry long on bull, short on bear (strategy.entry reverses)
    while long: stop = lowest(low, 20) x (1 - 1 %) (ATR method: entry - 1.5 x ATR(14)), target = entry + 2 x risk;
    shorts mirrored; strategy.exit(stop, limit) re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivotlow / pivothigh(rsi, 5, 5): the RSI 5 bars back strictly below (above) the 5 before and the 5 after
      (ties are not pivots), known 5 bars later (as #430850). "In range" is barssince(pivot)[1], 5 to 60.
    * The RSI is the source's own formula (Wilder rma of the up / down changes; 100 when down is 0, 0 when up is 0).
    * The stop and target are re-computed every bar in the source (the swing window rolls, the ATR changes): a
      moving bracket, mark trailing_stop_pending. The port fixes both at the SIGNAL bar: sl_stop = the distance
      from that bar's close to its swing level (or 1.5 ATR), tp_stop = 2 x that, shifted one bar inside stops() and
      re-based on the fill price. (In Pine the bracket is first placed at the fill bar's close.)
    * The two sides' stop distances differ: stops() takes each bar's side from its signal.
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after their right bars; bracket fixed at the signal bar (mark).
    2 generic: PASS, RSI divergences, swing levels with a percentage margin, ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_492007_rsi_divergence_swing_bracket"
FAMILY = "macd_divergence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "method": ["Swing", "ATR"],
    "lb": [5, 3],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lb": 5, "range_lower": 5, "range_upper": 60, "method": "Swing",
                  "swing_look": 20, "swing_margin_pct": 1.0, "rr_swing": 2.0, "atr_len": 14, "atr_mult": 1.5,
                  "rr_atr": 2.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def _regular_div(found, osc, price, rb, lo_rng, hi_rng, bullish):
    """Regular divergence at confirmed pivots, as valuewhen(found, x[rb], 1) and barssince(found)[1]."""
    m = len(osc)
    out = np.zeros(m, dtype=bool)
    prev_o = prev_p = np.nan
    last = -1                                  # the last bar t' with found[t'] before the current bar
    for t in range(m):
        if found[t]:
            o_now, p_now = osc[t - rb], price[t - rb]
            gap = (t - 1) - last if last >= 0 else np.inf     # barssince(found)[1]
            if lo_rng <= gap <= hi_rng and not np.isnan(prev_o):
                out[t] = (p_now < prev_p and o_now > prev_o) if bullish else (p_now > prev_p and o_now < prev_o)
            prev_o, prev_p = o_now, p_now
            last = t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ov = _rsi(c, int(p["rsi_len"])).to_numpy(dtype=float)
    lb = int(p["lb"])
    pl, ph = _pivots(ov, lb, lb, False), _pivots(ov, lb, lb, True)
    lo_r, hi_r = int(p["range_lower"]), int(p["range_upper"])
    bull = _regular_div(pl, ov, lo.to_numpy(dtype=float), lb, lo_r, hi_r, True)
    bear = _regular_div(ph, ov, h.to_numpy(dtype=float), lb, lo_r, hi_r, False)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    # a bar cannot be both an RSI pivot low and a pivot high (strict comparisons)
    return pd.Series(bull, index=idx), false, pd.Series(bear, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    long_e, _, short_e, _ = simulate(bars_df, **params)
    if p["method"] == "Swing":
        m = p["swing_margin_pct"] / 100
        n = int(p["swing_look"])
        d_long = 1 - lo.rolling(n).min() * (1 - m) / c
        d_short = h.rolling(n).max() * (1 + m) / c - 1
        rr = p["rr_swing"]
    else:
        d_long = d_short = p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / c
        rr = p["rr_atr"]
    dist = d_long.where(long_e, d_short.where(short_e))   # the signal bar's side
    return {"sl_stop": dist.shift(1), "tp_stop": (rr * dist).shift(1)}


def portfolio_kwargs(**params):
    return {}
