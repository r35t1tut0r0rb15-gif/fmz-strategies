"""Scalping PullBack Tool (JustUncleL): in a Heikin-Ashi EMA 89 / 200 trend with the PAC channel
(EMA 34 of HA high / low / close) on the trend side, a HA candle opening inside and closing back
through the channel after a recent pull-back starts a trade direction; a new direction from
neutral goes long or short.
Port of FMZ strategy #364527 "Scalping PullBack Tool R1.1 by JustUncleL".

Source
    https://www.fmz.com/strategy/364527 (PineScript v4, FMZ last modified 2022-05-20 16:32:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 159-317), PAC 34, EMA 89 / 200, lookback 3, HA candles on
    Trend = ema89 > ema200 and pacL > ema200 ? 1 : ema89 < ema200 and pacU < ema200 ? -1 : 0
    pacExitU = haOpen < pacU and haClose > pacU and barssince(haClose < pacC) <= 3   (L mirrors)
    Buy = Trend == 1 and pacExitU;  Sell = Trend == -1 and pacExitL
    TD := TD == 1 and haClose < pacC ? 0 : TD == -1 and haClose > pacC ? 0
          : TD == 0 and Buy ? 1 : TD == 0 and Sell ? -1 : TD
    TD[1] == 0 and TD == 1 -> entry long; else TD[1] == 0 and TD == -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(heikinashi(...), timeframe.period, x) is the same-period Heikin-Ashi series, built
      from the port's bars. The return of TD to 0 sends no order (the position is held).
    * Fractals, HH/LL labels and the 600 EMA only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_364527_ha_pac_pullback"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pac_len": [21, 34],
    "lookback": [2, 3, 5],
}
DEFAULT_PARAMS = {"pac_len": 34, "fast": 89, "medium": 200, "lookback": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _heikin_ashi(bars):
    """heikinashi(): HA close = ohlc4; HA open = (HA open[1] + HA close[1]) / 2, seeded (open + close) / 2."""
    o, h, l, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + l + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(l, np.minimum(ho, hc))
    return pd.DataFrame({"open": ho, "high": hh, "low": hl, "close": hc}, index=bars.index)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ha = _heikin_ashi(bars_df)
    hc, ho = ha["close"], ha["open"]
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    fast, med = ema(hc, p["fast"]), ema(hc, p["medium"])
    pac_c, pac_l, pac_u = ema(hc, p["pac_len"]), ema(ha["low"], p["pac_len"]), ema(ha["high"], p["pac_len"])
    trend = np.where((fast > med) & (pac_l > med), 1, np.where((fast < med) & (pac_u < med), -1, 0))
    k = int(p["lookback"])
    bs_below = _barssince((hc < pac_c).to_numpy())
    bs_above = _barssince((hc > pac_c).to_numpy())
    exit_u = ((ho < pac_u) & (hc > pac_u)).to_numpy() & (bs_below <= k)
    exit_l = ((ho > pac_l) & (hc < pac_l)).to_numpy() & (bs_above <= k)
    buy, sell = (trend == 1) & exit_u, (trend == -1) & exit_l
    below_c, above_c = (hc < pac_c).to_numpy(), (hc > pac_c).to_numpy()
    m = len(hc)
    td = np.zeros(m)
    for i in range(m):
        prev = td[i - 1] if i else 0.0
        if prev == 1 and below_c[i]:
            td[i] = 0
        elif prev == -1 and above_c[i]:
            td[i] = 0
        elif prev == 0 and buy[i]:
            td[i] = 1
        elif prev == 0 and sell[i]:
            td[i] = -1
        else:
            td[i] = prev
    prev = np.concatenate([[0.0], td[:-1]])
    return _always_in((prev == 0) & (td == 1), (prev == 0) & (td == -1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
