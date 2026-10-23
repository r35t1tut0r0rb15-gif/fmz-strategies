"""Hourly bars, 10:00-13:00 bar opens (exchange time, UTC for the header's venue): an EMA 9 / 21 crossing in the direction of the same EMAs, or a close crossing the session VWAP after a wick through it with RSI 14 on that side of 50, with ATR 14 at most 1 % of the close and RSI between 50 and 70 (30 and 50 for shorts) goes long (short); the trailing exit cannot be expressed and is pending; reversing.
Port of FMZ strategy #488146 "多时间框架趋势动量与VWAP反弹交叉量化策略-Multi-Timeframe-Trend-Momentum-and-VWAP-Rebound-Crossover-Quantitative-Strategy" (HDFC Bank 95% Accuracy Intraday Strategy).

FMZ source id: 488146

Source
    https://www.fmz.com/strategy/488146 (PineScript v5, FMZ last modified 2025-03-25 14:25:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 257-335), EMA 9 / 21 (and the "60" security of them on the 1-hour chart: the same values); session VWAP of hlc3; RSI 14; ATR 14 <= 1 % of the close; window 10:00-14:00 with minute 0; trail 0.5 %
    longCondition = (crossover(ema9, ema21) and bullTrend1H or crossover(close, vwap) and lowest(low, 2) < vwap and bullTrend1H and rsi > 50) and atr / close x 100 <= 1 and 50 < rsi < 70 and inTradeWindow -> entry Long  (short mirrored)
    in a trade: trailStop := max(trailStop, entry - (high - entry) x 0.5 %);  exit(trail_points = (entry - trailStop) / mintick, trail_offset = the same)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "1-hour" security on the header's 1-hour chart is the chart's own EMAs. The window test needs
      minute 0 and an hour from 10 to 13 (hour 14 fails its minute < 0 test), on the venue's UTC clock.
      The block that redeclares the conditions at 12:00 creates new local names and changes nothing. The
      exit is a trailing stop whose activation and offset both equal the gap between the entry and a
      level that ratchets from 0.5 % under the entry toward it (and above it when the bar's high is under
      the entry); the house trail cannot express it, so it is not ported and only the opposite entry ends
      a trade (mark trailing_stop_pending, as #444344). ta.vwap(hlc3) restarts each session: the house
      session is the broker day (17:00 America/New_York). The title names HDFC Bank; the rules are
      generic. REVERSAL INTENDED. 100 % of equity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trailing exit pending.
    2 generic: PASS, EMA crossings and VWAP bounces in a low-volatility window.
    3 crypto-exchange-only: no (exchange pair in the header only (HDFC Bank named in the title)).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: window 10:00-13:00 bar opens on the venue's UTC clock; VWAP on the broker day.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488146_ema_cross_vwap_bounce_window_trail_pending_1h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_pct": [1.0, 2.0],
    "fast": [9, 12],
}
DEFAULT_PARAMS = {"atr_pct": 1.0, "fast": 9, "slow": 21, "start_h": 10, "end_h": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    ix = bars_df.index
    utc = ix.tz_convert("UTC")
    hr, mn = utc.hour.to_numpy(), utc.minute.to_numpy()
    sh, eh = int(p["start_h"]), int(p["end_h"])
    window = pd.Series((hr >= sh) & (hr <= eh) & (mn == 0) & ((hr != eh) | (mn < 0)), index=ix)
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    bull, bear = f > s, f < s
    day = broker_day(ix)
    src = (h + lo + c) / 3
    vw = (src * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    r = _rsi(c, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    calm = atr / c * 100 <= float(p["atr_pct"])
    x_up = (f > s) & (f.shift(1) <= s.shift(1)) & bull
    x_dn = (f < s) & (f.shift(1) >= s.shift(1)) & bear
    b_up = (c > vw) & (c.shift(1) <= vw.shift(1)) & (lo.rolling(2).min() < vw) & bull & (r > 50)
    b_dn = (c < vw) & (c.shift(1) >= vw.shift(1)) & (h.rolling(2).max() > vw) & bear & (r < 50)
    buy = (x_up | b_up) & calm & (r > 50) & (r < 70) & window
    sell = (x_dn | b_dn) & calm & (r < 50) & (r > 30) & window
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
