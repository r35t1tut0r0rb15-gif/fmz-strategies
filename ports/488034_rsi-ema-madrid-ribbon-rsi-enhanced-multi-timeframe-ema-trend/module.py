"""Madrid moving-average ribbon counts with RSI extremes and a 0.5 % / 1 % bracket, broker days: when at least 13 of the
18 ribbon EMAs (5 to 90) are "green" against the EMA 100 and RSI 14 is below 30 the strategy goes long; when at least
9 are "red" and RSI is above 70 it goes short; each trade has a 0.5 % target and a 1 % stop.
Port of FMZ strategy #488034 "马德里带状RSI增强型多时框EMA趋势策略-Madrid-Ribbon-RSI-Enhanced-Multi-Timeframe-EMA-Trend-Strategy" (Madrid Ribbon Strategy with Backtesting).

FMZ source id: 488034

Source
    https://www.fmz.com/strategy/488034 (PineScript v5, FMZ last modified 2025-03-24 15:52:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 189-288), EMAs 5..90 step 5 against EMA 100, RSI 14, TP 0.5 %, SL 1 %
    colour: change >= 0 and ma > ref lime; change < 0 and ma > ref maroon; change <= 0 and ma < ref red;
    change >= 0 and ma < ref green; else gray (in this order)
    buy = count(lime or green) >= 13 and rsi < 30;  sell = count(red or maroon) >= 9 and rsi > 70
    entry (qty = 100000 / close) + exit(limit = close x (1 +- 0.5 %), stop = close x (1 -+ 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour chain is evaluated in the source's order (a flat EMA below the reference is red).
    * The bracket is from the signal close, re-based on the fill: sl_stop / tp_stop scalars. A same-side signal while
      held re-places it from the new close: mark trailing_stop_pending; the port keeps the entry's bracket.
    * The EMA / SMA input is a GRID variant. Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from
      the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal close (re-placement marked).
    2 generic: PASS, moving-average slopes and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the cash quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488034_madrid_ribbon_rsi_bracket"
FAMILY = "ma_ribbon"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "use_ema": [True, False],
    "sl_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"use_ema": True, "rsi_len": 14, "green_min": 13, "red_min": 9, "rsi_os": 30, "rsi_ob": 70,
                  "tp_pct": 0.5, "sl_pct": 1.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ma(n):
        return c.ewm(span=n, adjust=False).mean() if p["use_ema"] else c.rolling(n).mean()
    ref = ma(100)
    green = pd.Series(0, index=c.index)
    red = pd.Series(0, index=c.index)
    for n in range(5, 95, 5):
        x = ma(n)
        d = x.diff()
        lime = (d >= 0) & (x > ref)
        maroon = ~lime & (d < 0) & (x > ref)
        rd = ~lime & ~maroon & (d <= 0) & (x < ref)
        gr = ~lime & ~maroon & ~rd & (d >= 0) & (x < ref)
        green += (lime | gr).astype(int)
        red += (rd | maroon).astype(int)
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((green >= p["green_min"]) & (rsi < p["rsi_os"])).astype(bool)
    short_e = ((red >= p["red_min"]) & (rsi > p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
