"""EMA 5 / 20, MACD(12, 26, 20) and RSI-signal agreement, daily bars: the close above both EMAs with the MACD over its signal and the RSI 14 over its EMA 20 holds long, all reversed holds short; reversing.
Port of FMZ strategy #443246 "MACDRSI与EMA策略MACD-RSI-and-EMA-Strategy" (MACD,RSI & EMA strategy with MA+PSAR by MAM).

FMZ source id: 443246

Source
    https://www.fmz.com/strategy/443246 (PineScript v4, FMZ last modified 2024-03-01 12:23:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-193), EMA 5 / 20; MACD 12 / 26, signal 20; RSI 14, signal EMA 20; SMA 5 / 10 / 50 / 200 and PSAR (plots only)
    long = close > ema5 and close > ema20 and macd > signal and rsi > ema(rsi, 20) -> entry Buy;  short = all reversed -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are level tests, refused while held. The SMAs and the PSAR only plot.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA, MACD and RSI agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443246_ema_macd_rsi_signal_agreement_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len2": [20, 50],
    "rsi_signal_len": [20, 9],
}
DEFAULT_PARAMS = {"ema_len2": 20, "rsi_signal_len": 20, "ema_len1": 5, "macd_fast": 12, "macd_slow": 26,
                  "macd_signal": 20, "rsi_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1 = c.ewm(span=int(p["ema_len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema_len2"]), adjust=False).mean()
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    ms = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    rs = r.ewm(span=int(p["rsi_signal_len"]), adjust=False, ignore_na=True).mean()
    le = (c > e1) & (c > e2) & (macd > ms) & (r > rs)
    se = (c < e1) & (c < e2) & (macd < ms) & (r < rs)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
