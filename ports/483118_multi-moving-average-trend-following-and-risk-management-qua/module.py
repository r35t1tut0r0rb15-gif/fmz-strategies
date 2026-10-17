"""EMA 50 above EMA 200 for more than 10 bars with RSI 14 above 50 and ADX above 20, long only, with a 1.5 ATR
trailing stop that starts after 1.5 ATR of profit, daily (broker-day) bars.
Port of FMZ strategy #483118 "多重均线趋势追踪与风控优化量化交易策略-Multi-Moving-Average-Trend-Following-and-Risk-Management-Quantitative-Trading-Strategy" (High-Return Trend Strategy (Final)).

FMZ source id: 483118

Source
    https://www.fmz.com/strategy/483118 (PineScript v6, FMZ last modified 2025-02-21 14:22:42).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-135), EMA 50 / 200, RSI 14 > 50, DMI 14 / 14, ADX > 20, ATR 14
    long = ema50 > ema200 and rsi > 50 and adx > 20 and barssince(ema50 <= ema200) > 10 -> entry long
    exit(trail_points = 1.5 ATR, trail_offset = 1.5 ATR) on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail arguments are ticks given ATR price distances: read as price distances (as #427592) and ported as the
      house trail {"type": "volatility", "atr_n": 14, "k": 1.5, "anchor": "high_low", "activate_after": 0.11};
      stated approximation: the 1.5-ATR activation becomes an 11 % gain (1.5 daily ATR on the author's Binance
      DOGE_USDT, daily ATR about 7 % in 2024-2025), as #489284. No fixed stop or target (longStopLoss is never used).
    * barssince of a condition that never held is na: no entry, as written. Every bar in the condition is an entry
      signal (same-side ignored while held). ADX as Pine's ta.dmi (as #426579).
    * The risk-based qty is sizing: not ported. Long only; the source has no shorts. Stop module: portfolio_kwargs {}
      (D4). Daily bars are broker days stamped with their first minute (as #430984); stops on daily bars:
      coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trail a house trail (approximation stated).
    2 generic: PASS, moving averages, RSI, ADX and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported; the trail via stops().
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483118_ema50_200_rsi_adx_long_atr_trail"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_k": [1.5, 3.0],
    "adx_min": [20.0, 25.0],
}
DEFAULT_PARAMS = {"long_ema": 200, "short_ema": 50, "rsi_len": 14, "rsi_buy": 50.0, "atr_len": 14, "adx_min": 20.0,
                  "confirm_bars": 10, "trail_k": 1.5, "trail_activate": 0.11}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = None
    for i, v in enumerate(cond):
        if v:
            last = i
        if last is not None:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    _, _, adx = _adx_pine(bars_df, 14, 14)
    since = _barssince((es <= el).to_numpy())
    confirmed = np.where(np.isnan(since), False, since > int(p["confirm_bars"]))
    long_e = ((es > el) & (rsi > p["rsi_buy"]) & (adx > p["adx_min"])).to_numpy() & confirmed
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(long_e, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
