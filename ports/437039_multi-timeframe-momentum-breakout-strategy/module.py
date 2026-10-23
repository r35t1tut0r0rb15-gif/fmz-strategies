"""Broker days: the RSI 14 above 63 with the ADX (DMI 14, smoothing 20) above 20 and DI+ above 25 goes long; the RSI under 40 with the ADX above 20 and DI- above 25 goes short; only shorts carry a bracket (1.5 ATR 14 stop, 4 ATR target from the close); reversing.
Port of FMZ strategy #437039 "Multi Timeframe Momentum Breakout Strategy" (KritikSharma Strategy for NIFTY,BNIFTY,NG,CRUDE,WTICrude,BTC,GOLD,SILVER,COPPER).

FMZ source id: 437039

Source
    https://www.fmz.com/strategy/437039 (PineScript v5, FMZ last modified 2023-12-29 16:56:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 172-333), RSI 14; DMI 14 / ADX smoothing 20; ADX 20, DI 25; ATR 14; SL 1.5 ATR, TP 4 ATR
    rsi > 63 and adx > 20 and diplus > 25 -> entry Buy;  rsi < 40 and adx > 20 and diminus > 25 -> entry Sell
    exit("Take Profit/Stop Loss", from_entry = "Buy", stop = close - 1.5 atr, limit = close + 4 atr);  exit("Take Profit/Stop Loss", from_entry = "Sell", stop = close + 1.5 atr, limit = close - 4 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.dmi(adxLength, adxThreshold) passes the threshold 20 as the ADX smoothing, as written. Both
      exits share one id, so the second call (from_entry 'Sell') replaces the first every bar: only shorts
      get the bracket, longs end only by the reversal (as #435894; weird case). The bracket is re-sent
      each bar from the latest close and ATR; the port fixes it at the signal bar as fractions of the fill
      (mark trailing_stop_pending). The high-volume bars, pivots, Fibonacci levels and table only feed
      plots: volume is not used. REVERSAL INTENDED. qty 1 is sizing. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short-only ATR bracket at the signal bar.
    2 generic: PASS, RSI momentum with DMI / ADX confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 unit, not ported.
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

NAME = "fmz_437039_rsi63_40_dmi_adx_short_atr_bracket_reversal"
FAMILY = "adx_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_long": [63.0, 60.0],
    "di_threshold": [25.0, 20.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "adx_len": 14, "adx_smooth": 20, "adx_threshold": 20.0, "di_threshold": 25.0,
                  "rsi_long": 63.0, "rsi_short": 40.0, "atr_len": 14, "sl_atr": 1.5, "tp_atr": 4.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())


def _dmi(bars_df, di_len, adx_smooth):
    """ta.dmi(diLength, adxSmoothing)."""
    h, lo = bars_df["high"], bars_df["low"]
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index).where(dn.notna())
    atr = _rma(_tr(bars_df), di_len)
    plus, minus = 100 * _rma(pdm, di_len) / atr, 100 * _rma(mdm, di_len) / atr
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_smooth)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    plus, minus, adx = _dmi(bars_df, int(p["adx_len"]), int(p["adx_smooth"]))
    r = _rsi(c, int(p["rsi_len"]))
    at, dt = float(p["adx_threshold"]), float(p["di_threshold"])
    buy = (r > float(p["rsi_long"])) & (adx > at) & (plus > dt)
    sell = (r < float(p["rsi_short"])) & (adx > at) & (minus > dt)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy & ~sell, false, sell & ~buy, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    atr = _rma(_tr(bars_df), int(p["atr_len"]))
    a1 = atr.shift(1) / o                               # the signal bar's ATR as a fraction of the fill
    short_fill = se.shift(1, fill_value=False)          # only the 'Sell' entry keeps the shared exit
    sl_f = (float(p["sl_atr"]) * a1).where(short_fill)
    tp_f = (float(p["tp_atr"]) * a1).where(short_fill)
    return {"sl_stop": sl_f, "tp_stop": tp_f}


def portfolio_kwargs(**params):
    return {}
