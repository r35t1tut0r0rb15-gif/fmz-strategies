"""Broker days: within the last 4 bars, a 5-bar range of about 5 % of the 45-bar average price whose low is the newest bar and high the oldest (with RSI 23 under 50), or a 2.2 % "correction" in a rising 45-bar SMA, goes long with a stop 2.2 % and a target 5 % (of the average price) from the signal close; the mirrored patterns (RSI over 55, falling SMA) go short; reversing.
Port of FMZ strategy #488249 "Similar Rectangle Height Pattern Quantitative Strategy" (Similar Rectangle Heights - Strategy).

FMZ source id: 488249

Source
    https://www.fmz.com/strategy/488249 (PineScript v5, FMZ last modified 2025-03-26 11:44:39).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 200-370), lookback 45; primary height 5 %, correction 2.2 % of sma(close, 45); widths 5 .. 14 (corrections 2.5 .. 7); RSI 23 (50 / 55); volume off
    bullishPattern(idx): L = lowest(low, 5)[idx], H = highest(high, 5)[idx]; |H - L - primary| <= 0.2 primary; width from the first bar (back from idx) at L to the first bar at or before it at H in 5 .. 14; rsi[idx] < 50
    bullishCorrection(idx): |H - L - correction| <= 0.2 correction; width (first H, then L) in 2.5 .. 7; sma45[idx] > sma45[idx + 5];  bearish versions mirrored
    buySignal = any idx 0 .. 3 of bullishPattern(idx) or (idx > 0 and bullishCorrection(idx)) -> entry Long, exit(stop = close - correction, limit = close + primary);  sellSignal mirrored -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both extremes come from the same 5-bar window, so a "pattern" width of at least 5 needs the window's
      two ends: for the bullish pattern the low on the newest bar and the high on the oldest (a 5-bar
      drop), as written (weird case); the search can run past the window only when an older bar repeats
      the extreme exactly. The heights are percentages of the 45-bar average price, so they scale with
      the instrument. A bar with both a buy and a sell takes the later short. The bracket is sent on
      signal bars as levels from that close: ported as fractions of the fill, exact (1e-6 floor); repeats
      re-send it (not followed: trailing_stop_pending). The volume filter is off by default (held for
      volume, not used). REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent-of-average bracket at the signal close as fractions of the fill.
    2 generic: PASS, range-height pattern matching.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_488249_similar_rectangle_heights_pattern_bracket_reversal"
FAMILY = "chart_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "primary_pct": [5.0, 3.0],
    "corr_pct": [2.2, 1.5],
}
DEFAULT_PARAMS = {"lookback": 45, "primary_pct": 5.0, "corr_pct": 2.2, "min_bars": 5, "max_bars": 14,
                  "rsi_len": 23, "rsi_ob": 55.0, "rsi_os": 50.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _width(a1, v1, a2, v2, base, kmax, look):
    """First bar back from base (0 .. kmax-1) where a1 == v1, then the first bar at or before it where a2 == v2."""
    i0 = None
    for k in range(kmax):
        pos = base - k
        if pos < 0 or k >= look:
            break
        if a1[pos] == v1:
            i0 = k
            break
    if i0 is None:
        return 0
    for j in range(i0, kmax):
        pos = base - j
        if pos < 0 or j >= look:
            break
        if a2[pos] == v2:
            return j - i0 + 1
    return 0


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    nb, kmax, look = int(p["min_bars"]), int(p["max_bars"]), int(p["lookback"])
    avg = c.rolling(look).mean()
    ph = (avg * float(p["primary_pct"]) / 100).to_numpy(dtype=float)
    ch = (avg * float(p["corr_pct"]) / 100).to_numpy(dtype=float)
    r = _rsi(c, int(p["rsi_len"])).to_numpy(dtype=float)
    sma = avg.to_numpy(dtype=float)
    L5, H5 = lo.rolling(nb).min().to_numpy(dtype=float), h.rolling(nb).max().to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hn)
    buy, sell = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    os_, ob_ = float(p["rsi_os"]), float(p["rsi_ob"])
    for t in range(m):
        for idx in range(4):
            b = t - idx
            if b < 0 or np.isnan(L5[b]) or np.isnan(ph[t]):
                continue
            hgt = H5[b] - L5[b]
            if not buy[t]:
                if abs(hgt - ph[t]) <= ph[t] * 0.2 and r[b] < os_ and nb <= _width(ln, L5[b], hn, H5[b], b, kmax, look) <= kmax:
                    buy[t] = True
                elif idx > 0 and abs(hgt - ch[t]) <= ch[t] * 0.2 and b - nb >= 0 and sma[b] > sma[b - nb] \
                        and nb / 2 <= _width(hn, H5[b], ln, L5[b], b, kmax, look) <= kmax / 2:
                    buy[t] = True
            if not sell[t]:
                if abs(hgt - ph[t]) <= ph[t] * 0.2 and r[b] > ob_ and nb <= _width(hn, H5[b], ln, L5[b], b, kmax, look) <= kmax:
                    sell[t] = True
                elif idx > 0 and abs(hgt - ch[t]) <= ch[t] * 0.2 and b - nb >= 0 and sma[b] < sma[b - nb] \
                        and nb / 2 <= _width(ln, L5[b], hn, H5[b], b, kmax, look) <= kmax / 2:
                    sell[t] = True
    buy &= ~sell                              # the later short entry wins on a two-sided bar
    return buy, sell, ph, ch


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _, _ = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, ph, ch = _signals(bars_df, p)
    ix = bars_df.index
    o, c = bars_df["open"], bars_df["close"]
    ph, ch = pd.Series(ph, index=ix), pd.Series(ch, index=ix)
    lf = pd.Series(buy, index=ix).shift(1, fill_value=False)
    sf = pd.Series(sell, index=ix).shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=ix).mask(lf, 1 - (c - ch).shift(1) / o)
            .mask(sf, (c + ch).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=ix).mask(lf, (c + ph).shift(1) / o - 1)
            .mask(sf, 1 - (c - ph).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
