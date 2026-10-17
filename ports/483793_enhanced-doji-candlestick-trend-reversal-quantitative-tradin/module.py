"""Doji bars with a candle confirmation, a tiny fixed bracket and a doji close-out, two-day bars: on a doji (body at most
30 % of the range) with a bullish confirmation candle now or on the previous bar the strategy goes long, with a
bearish one short; every doji also closes the position held coming into the bar; each trade has a 5-tick stop and a
target twice as far (as ATR multiples).
Port of FMZ strategy #483793 "增强型十字星烛台趋势反转量化交易策略-Enhanced-Doji-Candlestick-Trend-Reversal-Quantitative-Trading-Strategy" (Enhanced Doji Candle Strategy).

FMZ source id: 483793

Source
    https://www.fmz.com/strategy/483793 (PineScript v5, FMZ last modified 2025-02-27 16:33:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-224), doji body <= 30 % of range, SL 5 ticks, RR 2
    bullishConfirm = close > open and low >= open x 0.99;  bearishConfirm = close < open and high <= open x 1.01
    doji and (bullishConfirm or bullishConfirm[1]) -> entry long + exit(stop = close - 5 ticks, limit = close + 10 ticks)
    doji and (bearishConfirm or bearishConfirm[1]) -> entry short (mirrored);  doji -> close long, close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The doji close-out acts on the position held at the bar's start and never undoes an entry on that bar
      (#430850); both confirmations on one doji: the short, written last, wins. The SMA trend is computed but unused.
    * Criterion 2: on the author's 2-day ETH_USDT (tick 0.01, 2-day ATR about 200) 5 ticks are about 0.00025 Wilder
      ATR(14) (judgement before any backtest): sl_stop = sl_atr x ATR / close of the signal bar, tp_stop = rr x that,
      shifted one bar inside stops() and re-based on the fill.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, tick distances -> ATR multiples; candle proportions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483793_doji_confirm_closeout_bracket"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.00025, 1.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"doji_frac": 0.3, "sl_atr": 0.00025, "rr": 2.0, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    doji = ((c - o).abs() <= (h - lo) * p["doji_frac"]).to_numpy()
    bull = (c > o) & (lo >= o * 0.99)
    bear = (c < o) & (h <= o * 1.01)
    bull_c = (bull | bull.shift(1, fill_value=False)).to_numpy()
    bear_c = (bear | bear.shift(1, fill_value=False)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if doji[i]:
            if bull_c[i]:
                pos = 1
            if bear_c[i]:
                pos = -1
            if start != 0 and pos == start:              # close("Buy") / close("Sell") on every doji
                pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
