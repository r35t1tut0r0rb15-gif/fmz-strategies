"""Close beyond the EMA 21 with RSI 14 and MACD-histogram agreement, daily bars, with a 2 % bracket: above with RSI over 50 and a positive histogram goes long unless already long, the mirror goes short;
stop and target 2 % from the fill; reversing.
Port of FMZ strategy #451387 "EMAMACDRSI三重指标动量策略-EMA-MACD-and-RSI-Triple-Indicator-Momentum-Strategy" (2024 (EMA 21, MACD and RSI)).

FMZ source id: 451387

Source
    https://www.fmz.com/strategy/451387 (PineScript v5, FMZ last modified 2024-05-14 15:34:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-133), EMA 21 (EMAs 5 / 10 / 50 / 200 / 1000 plot only); RSI 14 (50); MACD 12 / 26 / 9; bracket 2 % of the signal close
    close > ema21 and rsi > 50 and hist > 0 and position <= 0 -> entry Long, exit(limit = close x 1.02, stop = close x 0.98);  short mirrored with position >= 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries are taken only when not already on that side, so the bracket is never re-sent inside a
      trade: a fixed 2 % of the signal close, ported as fractions of the fill (as #437751). The alert
      text names a broker and XAUUSDm but is only a message. Daily stop module: mark coarse_bar_stop.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA side with RSI and MACD agreement, percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only; the alert text names XAUUSDm as a message only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451387_ema21_side_rsi_hist_two_pct_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [21, 50],
    "bracket": [0.02, 0.04],
}
DEFAULT_PARAMS = {"ema_len": 21, "bracket": 0.02, "rsi_len": 14}


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
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    le = (c > e) & (r > 50) & (hist > 0)
    se = (c < e) & (r < 50) & (hist < 0)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
