"""SMA 20 / 50 trend state, always in the market's direction, with a 2 ATR stop and a 4 ATR target, broker days: every bar
with the SMA 20 above the SMA 50 is a long entry (below: short); a trade leaves on its bracket or the reversal and is
re-entered on the next bar while the state holds.
Port of FMZ strategy #488152 "多均线趋势追踪与ATR风险管理量化交易策略-Multi-Moving-Average-Trend-Following-with-ATR-Risk-Management-Quantitative-Trading-Strategy" (Khaos Trading Bot).

FMZ source id: 488152

Source
    https://www.fmz.com/strategy/488152 (PineScript v5, FMZ last modified 2025-03-25 14:46:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 156-196), SMA 20 / 50, ATR 14 x 2, RR 2, trail 10 x stopLoss ticks
    sma20 > sma50 -> entry long;  sma20 < sma50 -> entry short (every bar)
    every bar: exit(stop = close -+ 2 ATR, limit = close +- 4 ATR) and exit(trail_price = close,
    trail_offset = stopLoss x 10 x mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every condition bar is an entry (a same-side one is ignored while held); entries reverse (REVERSAL INTENDED).
    * The bracket is re-issued every bar from the current close (moving): fixed at entry, mark trailing_stop_pending
      (sl_stop = atr_mult x ATR / close of the signal bar, tp_stop = rr x that, shifted one bar inside stops(),
      re-based on the fill).
    * The trail (rule 2): activation at the current close re-issued every bar and an offset of stopLoss x 10 x
      mintick ticks (on the author's daily ETH_USDT about 30 ticks, 0.30 USD, a tiny fraction of an ATR); a moving
      activation is not expressible in the house trail: not emitted (same mark).
    * The risk-based lot size is computed but never passed to an order. Stop module: portfolio_kwargs {} (D4). Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar (re-issue and trail marked).
    2 generic: PASS, moving averages and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity and the unused lot size quoted; the bracket ported via stops() and quoted in
      original_sizing.txt.
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

NAME = "fmz_488152_sma20_50_state_atr_bracket"
FAMILY = "ma_trend_state"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 3.0],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "atr_len": 14, "atr_mult": 2.0, "rr": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    false = pd.Series(False, index=bars_df.index)
    return (f > s).astype(bool), false, (f < s).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
