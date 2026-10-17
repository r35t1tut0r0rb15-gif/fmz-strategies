"""RSI 2 dip buying in the SMA 200 up-trend with an SMA 5 exit, long only, broker days: above the SMA 200, RSI 2 crossing
back above 5 goes long; a close above the SMA 5 closes the trade.
Port of FMZ strategy #488288 "RSI动量反转短期趋势跟踪策略与移动平均线聚合-RSI-Momentum-Reversal-Short-Term-Trend-Following-Strategy-with-Moving-Average-Confluence" (_Rerun's Dip Bonanza).

FMZ source id: 488288

Source
    https://www.fmz.com/strategy/488288 (PineScript v5, FMZ last modified 2025-03-26 16:13:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 204-241), RSI 2 (5), trend SMA 200, exit SMA 5, emergency stop 0 % (off)
    long = close > sma200 and crossover(rsi, 5) -> entry long
    position_size > 0 and close > sma5 -> close
    position_size > 0 and stop % > 0 and close < avg price x (1 - stop %) -> close (off by default)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close tests strategy.position_size, the position held at the bar's start: never on the entry's own bar; on
      a bar with both an entry signal and the exit while held, the trade closes (#430850 state machine).
    * The emergency stop is 0 % by default, so inert as written (not ported).
    * Long only: opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute; FREQ = "1D" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488288_rsi2_dip_sma5_exit"
FAMILY = "rsi_mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_buy": [5.0, 10.0],
    "exit_ma": [5, 10],
}
DEFAULT_PARAMS = {"rsi_len": 2, "rsi_buy": 5.0, "trend_ma": 200, "exit_ma": 5}


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
    rsi = _rsi(c, int(p["rsi_len"]))
    lvl = p["rsi_buy"]
    go = ((c > c.rolling(int(p["trend_ma"])).mean()) & (rsi > lvl) & (rsi.shift(1) <= lvl)).to_numpy()
    out = (c > c.rolling(int(p["exit_ma"])).mean()).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if go[i]:
            pos = 1
        if out[i] and start == 1:
            pos = 0
        le[i] = start == 0 and pos == 1
        lx[i] = start == 1 and pos == 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
