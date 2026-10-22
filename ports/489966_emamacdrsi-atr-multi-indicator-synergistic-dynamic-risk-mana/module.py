"""The close beyond the EMA 50 with the MACD histogram sign and RSI 14 between 50 and 70 (30 and 50), 2-day bars: the long state goes long, the short state goes short; reversing (the per-bar ATR bracket is pending).
Port of FMZ strategy #489966 "多指标协同动态风险管理短线交易策略EMAMACDRSI结合ATR自适应止损止盈技术-Multi-Indicator-Synergistic-Dynamic-Risk-Management-Scalping-Strategy-EMAMACDRSI-with-ATR-Adaptive-Stop-Loss-Take-Profit-Technique" (Scalping 15min: EMA + MACD + RSI + ATR-based SL/TP).

FMZ source id: 489966

Source
    https://www.fmz.com/strategy/489966 (PineScript v5, FMZ last modified 2025-04-10 15:27:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-252), EMA 50; MACD 12 / 26 / 9; RSI 14 / 70 / 30; ATR 14; SL 1 ATR, TP 2 ATR from the current close; 10 % of equity
    close > ema50 and hist > 0 and 50 < rsi < 70 -> entry Long;  mirror -> entry Short
    every bar: exit(stop = close -/+ atr, limit = close +/- 2 atr) for the held side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. The
      alerts are messages only. An entry on the other side reverses (REVERSAL INTENDED). Bars are blocks of
      two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute.
      FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, EMA / MACD / RSI states.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489966_ema50_side_macd_hist_rsi_band_state_reversal_2d"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emaLength": [50, 100],
    "rsiOB": [70, 80],
}
DEFAULT_PARAMS = {"emaLength": 50, "rsiOB": 70, "rsiLength": 14, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    e = ema(p["emaLength"])
    macd = ema(12) - ema(26)
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsiLength"]))
    ob = float(p["rsiOB"])
    le = (c > e) & (hist > 0) & (r > 50) & (r < ob)
    se = (c < e) & (hist < 0) & (r < 50) & (r > 100 - ob)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
