"""Oversold dips or an EMA / MACD up-state, broker days, long only: RSI 14 under 30 with the close under the lower Bollinger band, or the EMA 50 above the EMA 200 with MACD over its signal, buys; RSI over 70 or a close above the upper band closes.
Port of FMZ strategy #482441 "Multi Indicator Dynamic Equilibrium Quantitative Trading System" (ETH/USDT Multi-Indicator Strategy).

FMZ source id: 482441

Source
    https://www.fmz.com/strategy/482441 (PineScript v5, FMZ last modified 2025-02-18 14:44:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-187), RSI 14, 30 / 70; BB 20 / 2; EMA 50 / 200; MACD 12 / 26 / 9; 250 % of equity
    (rsi < 30 and close < lower) or (ema50 > ema200 and macd > signal) -> entry Buy;  rsi > 70 or close > upper -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both are states, so they can hold on one bar; a loop follows the call order: from flat the entry
      stands (the close finds no position), while long the repeat entry is ignored and the close acts.
      Long only. The 250 % of equity size is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oversold dips or EMA / MACD trend state with overbought closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482441_rsi_bb_dip_or_ema_macd_state_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "ema_long": [200, 100],
}
DEFAULT_PARAMS = {"ema_short": 50, "ema_long": 200}


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
    r = _rsi(c, 14)
    basis = c.rolling(20).mean()
    dev = 2 * c.rolling(20).std(ddof=0)
    ef = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = (((r < 30) & (c < basis - dev)) | ((ef > es) & (macd > sig))).to_numpy()
    sell = ((r > 70) | (c > basis + dev)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and pos == 0:
            le[i], nxt = True, 1
        if sell[i] and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
