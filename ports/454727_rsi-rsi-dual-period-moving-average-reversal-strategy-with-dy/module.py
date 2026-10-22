"""Connors-style RSI 2 reversals inside the EMA 400 trend, daily bars: over the EMA 400 and under the EMA 10, the RSI 2 crossing back over 10 goes long with a 1 % stop; under the EMA 400 and over the EMA 10, the RSI 2 crossing back under 90 goes short; the close crossing back over (under) the EMA 10 closes; reversing.
Port of FMZ strategy #454727 "RSI双周期均线反转策略与动态风险管理系统-RSI-Dual-Period-Moving-Average-Reversal-Strategy-with-Dynamic-Risk-Management-System" (Estrategia JSV (RSI 2 with EMA 10 / 400)).

FMZ source id: 454727

Source
    https://www.fmz.com/strategy/454727 (PineScript v5, FMZ last modified 2024-06-21 14:01:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-203), RSI 2, levels 10 / 90; EMA 10 / 400; stop 1 % of the signal close
    close > ema400 and close < ema10 and crossover(rsi2, 10) -> entry Long, exit(stop = close x 0.99);  the mirror -> entry Short, exit(stop = close x 1.01)
    crossover(close, ema10) -> close Long;  crossunder(close, ema10) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed on the signal bar from its close: ported as the fixed fraction 0.01 of the fill
      (as #437751). A repeat signal inside a trade re-issues it from that bar's close, which stops()
      cannot express: the opening level is kept and the module is marked trailing_stop_pending (as
      #434428). A long signal and the short's EMA close on one bar are one reversal (the close finds
      the trade reversed). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark).
    2 generic: PASS, RSI 2 reversals with EMA exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_454727_rsi2_reversal_ema10_400_stop_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [400, 200],
    "sl_pct": [0.01, 0.05],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 400, "sl_pct": 0.01, "rsi_len": 2, "os": 10.0, "ob": 90.0}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es_ = c.ewm(span=int(p["slow"]), adjust=False).mean()
    os_, ob = float(p["os"]), float(p["ob"])
    le = (c > es_) & (c < ef) & (r > os_) & (r.shift(1) <= os_)
    se = (c < es_) & (c > ef) & (r < ob) & (r.shift(1) >= ob)
    c1, f1 = c.shift(1), ef.shift(1)
    lx = (c > ef) & (c1 <= f1) & ~se
    sx = (c < ef) & (c1 >= f1) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
