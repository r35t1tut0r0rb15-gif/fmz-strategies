"""MACD 5 / 13 / 3 side with RSI 10 over 45 / under 55 and the close beyond a stacked SMA 5 / 20, 2-day bars: the bullish state goes long and the bearish state goes short, each with a 1.2 ATR 10 stop and a 2.5 ATR target from the signal close; reversing.
Port of FMZ strategy #484109 "Dynamic Risk Managed Rapid SMA Crossover Momentum Capture Strategy" (Stock & Options Hyper-Scalper).

FMZ source id: 484109

Source
    https://www.fmz.com/strategy/484109 (PineScript v5, FMZ last modified 2025-02-28 10:29:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-203), SMA 5 / 20; RSI 10 / 55 / 45; MACD 5 / 13 / 3; ATR 10; SL 1.2 ATR; TP 2.5 ATR; risk 0.5 % sizing; 1 % of equity
    macd > signal and rsi > 45 and close > sma5 > sma20 -> entry CALL (long) + exit(stop = close - 1.2 atr, limit = close + 2.5 atr)
    macd < signal and rsi < 55 and close < sma5 < sma20 -> entry PUT (short) + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states and repeat while held, each re-sending the bracket from the new close;
      the port fixes the bracket at the opening signal close and sends it as fractions of the fill open
      (a level at or through it is marketable and closed one bar late, as #458256), mark
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The
      risk-sized quantity is sizing. Bars are blocks of two broker days (17:00 America/New_York) counted
      from 1970-01-01, stamped with their first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, MACD / RSI / SMA stack states with an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: risk-sized quantity and 1 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484109_macd5_13_3_rsi10_sma5_20_stack_state_atr_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_multiplier": [1.2, 2.0],
    "take_profit_multiplier": [2.5, 4.0],
}
DEFAULT_PARAMS = {"stop_loss_multiplier": 1.2, "take_profit_multiplier": 2.5, "days": 2}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    s5, s20 = c.rolling(5).mean(), c.rolling(20).mean()
    r = _rsi(c, 10)

    def ema(x, n):
        return x.ewm(span=n, adjust=False).mean()

    macd = ema(c, 5) - ema(c, 13)
    sig = ema(macd, 3)
    le = (macd > sig) & (r > 45) & (c > s5) & (s5 > s20)
    se = (macd < sig) & (r < 55) & (c < s5) & (s5 < s20)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, 10)
    a, b = atr * float(p["stop_loss_multiplier"]), atr * float(p["take_profit_multiplier"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
