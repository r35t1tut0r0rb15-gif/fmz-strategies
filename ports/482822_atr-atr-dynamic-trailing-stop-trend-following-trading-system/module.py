"""UT Bot ATR trailing line (key 1.1, ATR 200) crossings with an EMA 50 side, broker days: the close crossing up through the line above the EMA goes long, crossing down below it goes short; reversing.
Port of FMZ strategy #482822 "ATR动态追踪止损的趋势跟踪交易系统-ATR-Dynamic-Trailing-Stop-Trend-Following-Trading-System" (Enhanced UT Bot with Long & Short Trades).

FMZ source id: 482822

Source
    https://www.fmz.com/strategy/482822 (PineScript v5, FMZ last modified 2025-02-20 14:53:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-201), key value 1.1; ATR 200; EMA 50; ROI close 100 %; 100 % of equity
    xATRTrailingStop: the UT Bot ratchet of close -/+ 1.1 atr(200);  buy = crossover(close, line) and close > ema50;  sell = crossunder(close, line) and close < ema50
    buy and position <= 0 -> entry Buy;  sell and position > 0 -> close Buy;  sell and position >= 0 -> entry Sell;  buy and position < 0 -> close Sell
    profit on the close >= 20 % -> exit stop at entry;  >= 50 % -> stop at entry x 1.30 and close("Partial Profit", 50 %);  >= 80 % -> stop at entry x 1.60;  >= 100 % -> close("Full Exit at 100% ROI")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The UT Bot line follows the source's nz() reads (na while the ATR 200 is warming up). Each signal
      enters its side from flat or reverses the other: REVERSAL INTENDED.
    * The ROI ladder moves the stop to break-even, then +30 %, then +60 % in steps keyed on the close's
      profit, which stops() cannot express (lock_in takes one fixed gain): mark trailing_stop_pending, no
      stop ported (as 433572). strategy.close("Partial Profit") and strategy.close("Full Exit at 100% ROI")
      name ids that are never entered, so they close nothing (Pine closes by entry id), as written.
    * The 100 % of equity size is sizing. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ROI stop ladder pending.
    2 generic: PASS, ATR trailing-line crossings with an EMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482822_ut_bot1_1_atr200_ema50_side_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key_value": [1.1, 2.0],
    "atr_period": [200, 100],
}
DEFAULT_PARAMS = {"key_value": 1.1, "atr_period": 200, "ema_period": 50}


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
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["key_value"]) * _atr(bars_df, int(p["atr_period"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        x = ts[i - 1] if i >= 1 else np.nan
        if np.isnan(x):
            x = cv[i] - nl[i]                 # na while the ATR is warming up
        p1 = ts[i - 1] if i >= 1 and not np.isnan(ts[i - 1]) else 0.0     # nz(x[1])
        s1 = cv[i - 1] if i >= 1 else np.nan
        if cv[i] > p1 and s1 > p1:
            x = max(p1, cv[i] - nl[i]) if not np.isnan(nl[i]) else np.nan
        elif cv[i] < p1 and s1 < p1:
            x = min(p1, cv[i] + nl[i]) if not np.isnan(nl[i]) else np.nan
        else:
            x = (cv[i] - nl[i]) if cv[i] > p1 else (cv[i] + nl[i])
        ts[i] = x
    line = pd.Series(ts, index=c.index)
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    le = (c > line) & (c.shift(1) <= line.shift(1)) & (c > e)
    se = (c < line) & (c.shift(1) >= line.shift(1)) & (c < e)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
