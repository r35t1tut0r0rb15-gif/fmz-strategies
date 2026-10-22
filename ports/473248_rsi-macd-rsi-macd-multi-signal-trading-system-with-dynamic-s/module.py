"""MACD 6 / 13 / 7 crossings at RSI 14 extremes, daily bars: a MACD cross up with the RSI under 35 goes long, a cross down with the RSI over 70 goes short; reversing. The 300 / 600-tick bracket re-sent every bar from the latest close is not ported (pending).
Port of FMZ strategy #473248 "RSI-MACD多重信号交易系统结合动态止盈止损策略-RSI-MACD-Multi-Signal-Trading-System-with-Dynamic-Stop-Management" (Scalping XAU/USD m5 (Protected)).

FMZ source id: 473248

Source
    https://www.fmz.com/strategy/473248 (PineScript v5, FMZ last modified 2024-11-28 15:47:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-142), RSI 14, 35 / 70; MACD 6 / 13 / 7; lot 1; stop 300, target 600 ticks from the current close
    rsi < 35 and crossover(macd, signal) -> entry Compra;  rsi > 70 and crossunder -> entry Venda
    long: exit(stop = close - 300 ticks, limit = close + 600 ticks);  short mirrored  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The title names XAU/USD 5-minute scalping; the backtest header's daily bars are followed. The
      bracket is re-sent on every bar from that bar's close, so its levels move after entry: stops()
      cannot express a level re-set every bar, so it is kept pending (as #438034, mark
      trailing_stop_pending); positions end at the opposite entry until then. The fixed lot is not
      ported. REVERSAL INTENDED. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings at RSI extremes; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only (XAU/USD named in the title)).
    4 signals only: fixed lot stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473248_macd6_13_7_cross_rsi_extremes_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_os": [35, 30],
    "rsi_ob": [70, 65],
}
DEFAULT_PARAMS = {"rsi_os": 35, "rsi_ob": 70, "rsi_len": 14}


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
    macd = c.ewm(span=6, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=7, adjust=False).mean()
    le = (r < float(p["rsi_os"])) & (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (r > float(p["rsi_ob"])) & (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
