"""Wide-range oversold bars bought with a 0.2 % target and an ATR trail, long only as written, two-day bars: a bar
whose range exceeds 0.5 % of its low with RSI 14 below 30 goes long; the trade takes a 0.2 % target, or a trail one
ATR(10) behind the best price once 0.1 % in profit (the short side can never fire as written).
Port of FMZ strategy #489656 "动态ATR网格回撤捕捉量化交易策略-Dynamic-ATR-Grid-Pullback-Capture-Quantitative-Trading-Strategy" (Smart Grid Scalping (Pullback) Strategy[BullByte]).

FMZ source id: 489656

Source
    https://www.fmz.com/strategy/489656 (PineScript v6, FMZ last modified 2025-04-07 13:47:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 165-206), ATR 10, grid factor 0.2, target 0.2 %, no-trade zone 0.5 %, RSI 14
    grid[i] = close + (i + 1) x 0.2 x ATR, i = 0..14
    long = close < grid[0] and (high - low) / low > 0.5 % and rsi < 30   (close < grid[0] is always true)
    short = close > grid[14] and (high - low) / high > 0.5 % and rsi > 70   (close > close + 3 ATR: never true)
    every bar in a trade: exit(limit = close x (1 +- 0.2 %), trail_price = close x (1 +- 0.1 %), trail_offset = ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the grid test is always true for longs and never true for shorts: long only.
    * The target is re-placed at every bar's close (a moving level): mark trailing_stop_pending; the port fixes it
      at 0.2 % of the fill (tp_stop scalar).
    * The trail: trail_offset takes ticks, the author passes the ATR price distance, read as a price distance (as
      #427592); activation at 0.1 % above the current close (re-placed every bar). Ported natively (mark
      trailing_stop): {"type": "volatility", "atr_n": 10, "k": 1.0, "anchor": "high_low", "activate_after": 0.001}.
      Stated approximation: the activation measured from the fill instead of each bar's close.
    * Every condition bar is an entry (a same-side entry while held is ignored). Stop module: portfolio_kwargs {} (D4).
    * FREQ = "2D" from the backtest header (period 2d): two-day bars built from broker days in fixed blocks of two
      broker-day dates counted from 1970-01-01 (block phase: decision owed), as #426509: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; moving target fixed at entry (mark); the trail a house trail.
    2 generic: PASS, ATR multiples, percentages and an oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489656_wide_range_oversold_target_trail_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "profit_target": [0.002, 0.01],
    "no_trade_zone": [0.005, 0.02],
}
DEFAULT_PARAMS = {"atr_len": 10, "profit_target": 0.002, "no_trade_zone": 0.005, "rsi_len": 14, "trail_k": 1.0,
                  "trail_activate": 0.001}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    long_c = (((h - lo) / lo > p["no_trade_zone"]) & (rsi < 30)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["profit_target"]),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
