"""Bottom-fishing signals with a fixed bracket, broker days, long only: a MACD bullish divergence (a new 60-bar low with MACD above its 60-bar low) with the last 15 highs under the EMA 99 and the
RSI 14 under 31.1, or a wide red bar entirely under the EMA 99 and the SMA 20, goes long with a 10 % target and a 2 % stop from the signal close.
Port of FMZ strategy #441132 "Bottom Hunter Strategy" (Strategy: MACD Dive).

FMZ source id: 441132

Source
    https://www.fmz.com/strategy/441132 (PineScript v5, FMZ last modified 2024-02-06 09:26:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-198), MACD 12 / 26 / 9; EMA 99; RSI 14 (31.1); BB basis SMA 20 (StdDev unused); target x 1.1, stop x 0.98 of the buy price
    divergence = low < lowest(low[1], 60) and macd > lowest(macd[1], 60);  allHighsBelowEma99 = high[0 .. 14] all <= ema99 (today's);  signal1 = divergence and allHighsBelowEma99 and rsi < 31.1
    signal2 = high < ema99 and (high - low) / low x 100 >= 3 and close < open and high < sma20;  signal1 or signal2 -> buyPrice = close, entry Buy;  exit(limit = buyPrice 1.1, stop = buyPrice 0.98) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set from the signal close: fixed fractions, target 0.10 and stop 0.02, re-based on
      the fill. A later signal while held moves the script's levels (buyPrice is overwritten), which the
      port does not follow. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, divergence, EMA, RSI and range filters with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441132_macd_divergence_bottom_pct_bracket_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.10, 0.05],
    "sl": [0.02, 0.05],
}
DEFAULT_PARAMS = {"tp": 0.10, "sl": 0.02, "fast": 12, "slow": 26, "signal": 9, "rsi_length": 14, "bb_len": 20}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    ema99 = c.ewm(span=99, adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    basis = c.rolling(int(p["bb_len"])).mean()
    div = (lo < lo.shift(1).rolling(60).min()) & (macd > macd.shift(1).rolling(60).min())
    below = h.rolling(15).max() <= ema99
    s1 = div & below & (r < 31.1)
    s2 = (h < ema99) & ((h - lo) / lo * 100 >= 3) & (c < o) & (h < basis)
    sig = (s1 | s2).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = o.to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
