"""Ichimoku breakouts with SMA 50 / 200 and weekly RSI filters, daily bars: the Tenkan over the Kijun with the close over the undisplaced cloud, the SMA 50 over the SMA 200 and the weekly RSI 14 over 70 goes long, the mirror (weekly RSI under 30) goes short; a long closes on a close under the Kijun or the Tenkan under it, a short on the mirror; reversing. The cloud stop re-set on each signal bar is not ported (pending).
Port of FMZ strategy #473236 "Multi Technical Indicator Trend Following Strategy with Ichimoku Cloud Breakout and Stop Loss System" (Ichimoku Strategy with Optional RSI, MA Filters and Alerts).

FMZ source id: 473236

Source
    https://www.fmz.com/strategy/473236 (PineScript v5, FMZ last modified 2024-11-28 15:13:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-205), Tenkan 9, Kijun 26, Senkou B 52 (spans undisplaced; Senkou A = SMA 2 of (Tenkan + Kijun) / 2); SMA 50 / 200; RSI 14 on request.security("W"); date filter always true; stop at the cloud edge of the last signal bar
    ma ok and tenkan > kijun and close > max(spanA, spanB) and weeklyRSI > 70 -> entry Long, stop = min(spans);  the mirror -> entry Short, stop = max(spans)
    long and (close < kijun or tenkan < kijun) -> close Long;  short mirrored;  held: exit(stop = trailingStopLoss)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly request without lookahead is read as the last completed broker week (Monday label,
      #437508), RSI 14 of the weekly closes. Senkou A is the SMA 2 of (Tenkan + Kijun), halved, as
      written. The entry tests are states and each repeat moves the stop to the current cloud edge, which
      stops() cannot express (pending, mark trailing_stop_pending). The closes are bar-close tests that
      give way to an entry on the same bar. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly RSI from completed weeks.
    2 generic: PASS, Ichimoku breakouts with MA and weekly RSI filters; moving cloud stop described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_473236_ichimoku_cloud_ma_weekly_rsi_kijun_exit_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_ob": [70, 60],
    "rsi_os": [30, 40],
}
DEFAULT_PARAMS = {"rsi_ob": 70, "rsi_os": 30, "rsi_len": 14}


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


def _mid(h, lo, n):
    return (h.rolling(n).max() + lo.rolling(n).min()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    tk, kj, sb = _mid(h, lo, 9), _mid(h, lo, 26), _mid(h, lo, 52)
    sa = (tk + kj).rolling(2).mean() / 2
    m50, m200 = c.rolling(50).mean(), c.rolling(200).mean()
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")         # the Monday of the broker week
    wk_close = c.groupby(week).last()
    w_rsi = _rsi(wk_close, int(p["rsi_len"])).shift(1)           # last completed week
    wr = pd.Series(w_rsi.reindex(week).to_numpy(), index=c.index)
    top, bot = np.maximum(sa, sb), np.minimum(sa, sb)
    le = (m50 > m200) & (tk > kj) & (c > top) & (wr > float(p["rsi_ob"]))
    se = (m50 < m200) & (tk < kj) & (c < bot) & (wr < float(p["rsi_os"]))
    lx = ((c < kj) | (tk < kj)) & ~le & ~se
    sx = ((c > kj) | (tk > kj)) & ~le & ~se
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
