# tv_indicators

Reusable technical indicators for **vectorbt** strategies. They are written to give
the same numbers as **TradingView** (each one follows the Pine Script
built-in, or the published source of the community script it is named after).

Each indicator comes in two forms:

* **Function**: pandas or numpy in, the same type out. Indicators with
  several outputs return a namedtuple.
* **vectorbt class** (`tv_indicators.vbt`): an `IndicatorFactory` class with
  parameter grids, multi-column input and the auto-generated
  `*_crossed_above`, `*_above` and similar helpers.

```python
import tv_indicators as ti
from tv_indicators.vbt import BBANDS, RSI, SUPERTREND
import vectorbt as vbt

bb = ti.bbands(df.close)                     # bb.basis, bb.upper, bb.lower, bb.bandwidth, bb.percent_b
st = ti.supertrend(df.high, df.low, df.close)

# parameter sweep
bb = BBANDS.run(df.close, length=[20, 30], mult=[2.0, 2.5], param_product=True)
entries = bb.close_crossed_below(bb.lower)
exits = bb.close_crossed_above(bb.upper)
pf = vbt.Portfolio.from_signals(df.close, entries, exits)
```

Requirements: `numpy`, `pandas`, `numba` and `vectorbt` (`vectorbt` is only
needed for `tv_indicators.vbt`). `TA-Lib` and `pytest` are only needed for
the tests.

```bash
python -m pytest tv_indicators/tests -q
```

## Indicator list

The names are the vectorbt class names (`tv_indicators.vbt.<NAME>`). Defaults
are TradingView's.

### Bollinger family

| Name | Function | Source | Defaults |
|---|---|---|---|
| BBANDS | `bbands(close, volume=nan, length, mult, ma_type)` | TV built-in *Bollinger Bands* (basis SMA/EMA/SMMA (RMA)/WMA/VWMA; stdev is always population stdev of the source) | 20, 2.0, SMA |
| BB_PERCENT_B | `bb_percent_b` | TV built-in *Bollinger Bands %B* (0..1 scale) | 20, 2.0 |
| BBW | `bbw` | TV built-in *Bollinger BandWidth* (x100), plus the 125-bar highest expansion / lowest contraction lines and a `squeeze` flag (BBW at its 125-bar low) | 20, 2.0, 125, 125 |
| BBTREND | `bbtrend` | TV built-in *BBTrend* (John Bollinger, 2024) | 20, 50, 2.0 |
| BBWP | `bbwp` | *Bollinger Band Width Percentile* [The_Caretaker] | 13, 252, SMA, MA 5 |
| DOUBLE_BBANDS | `double_bbands` | Kathy Lien's Double Bollinger Bands | 20, 1.0, 2.0 |
| SQUEEZE_MOMENTUM | `squeeze_momentum` | *Squeeze Momentum Indicator* [LazyBear], TradingView's most-liked script. `lazybear_compat=True` keeps the original's bug where BB uses `multKC` | 20, 2.0, 20, 1.5 |
| TTM_SQUEEZE | `ttm_squeeze` | *TTM Squeeze Pro* [Beardy_Fred]: BB(20,2) against KC at 1.0/1.5/2.0. `mid_sqz` is the classic John Carter squeeze | 20, 2.0, 1.0, 1.5, 2.0 |

### Moving averages and price sources

| Name | Function | Source |
|---|---|---|
| SMA / EMA / RMA / WMA | `sma`, `ema`, `rma`, `wma` | `ta.sma`, `ta.ema`, `ta.rma`, `ta.wma` |
| VWMA | `vwma(close, volume)` | `ta.vwma` |
| HMA | `hma` | `ta.hma` (`wma(2*wma(n/2) - wma(n), round(sqrt(n)))`) |
| DEMA / TEMA | `dema`, `tema` | TV built-ins |
| ALMA | `alma` | `ta.alma` (9, 0.85, 6) |
| LSMA | `lsma` | `ta.linreg` (25, offset 0) |
| MCGINLEY | `mcginley` | TV built-in *McGinley Dynamic* (14) |
| KAMA | `kama` | Kaufman AMA (not a TV built-in; same as TA-Lib) |
| MA | `ma(close, volume=nan, length, ma_type)` | picks an average by name |
| HL2 / HLC3 / OHLC4 / HLCC4 | `hl2`, `hlc3`, ... | price sources |

### Oscillators

| Name | Function | Source / defaults |
|---|---|---|
| RSI | `rsi` | TV built-in, 14 |
| STOCH | `stoch` → k, d | TV built-in, 14 / 1 / 3 |
| STOCH_RSI | `stoch_rsi` → k, d | TV built-in, 14 / 14 / 3 / 3 |
| MACD | `macd` → macd, signal, hist | TV built-in, 12 / 26 / 9, EMA or SMA for each line |
| CCI | `cci(src)` | TV built-in, 20. TV's default source is `hlc3`, so pass `ti.hlc3(h, l, c)` |
| WILLR | `willr` | Williams %R, 14 |
| MFI | `mfi` | `ta.mfi(hlc3, 14)` |
| ROC / MOM | `roc`, `mom` | 9 / 10 |
| AO | `awesome_oscillator` | 5 / 34 on hl2 |
| TSI | `tsi` → tsi, signal | 25 / 13 / 13 (x100) |
| CMO | `cmo` | TV built-in, 9. Uses plain sums; TA-Lib's CMO uses Wilder smoothing and gives different numbers |
| UO | `ultimate_oscillator` | 7 / 14 / 28 |
| FISHER | `fisher` → fisher, trigger | TV built-in, 9 |
| TRIX | `trix` | TV built-in: `10000 * change(log(ema³))`, 18 |
| WAVETREND | `wavetrend` → wt1, wt2 | *WaveTrend Oscillator* [LazyBear], 10 / 21 / 4 |
| CRSI | `connors_rsi` | TV built-in *Connors RSI*, 3 / 2 / 100 |
| COPPOCK | `coppock` | TV built-in, 10 / 14 / 11 |
| DPO | `dpo` | TV built-in with `isCentered=false` (no look-ahead), 21 |

### Trend and volatility

| Name | Function | Source / defaults |
|---|---|---|
| TR / ATR / NATR | `true_range`, `atr`, `natr` | `ta.tr(true)`, `ta.atr` (RMA 14; `smoothing` can be sma/ema/wma) |
| HV | `historical_volatility` | TV built-in, 10, annual 365 |
| KC | `keltner` | TV built-in *Keltner Channels*: 20, 2.0, EMA, ATR(10) |
| DONCHIAN | `donchian` | TV built-in, 20 |
| ENVELOPE | `envelope` | TV built-in, 20, 10 % |
| SUPERTREND | `supertrend` → supertrend, direction, trend | `ta.supertrend(3, 10)`. `direction` uses TV's convention (-1 = up); `trend` is +1 for up |
| PSAR | `psar` → psar, direction | `ta.sar(0.02, 0.02, 0.2)` |
| DMI / ADX | `dmi` → plus_di, minus_di, adx; `adx` | TV built-in *DMI*, 14 / 14 |
| AROON | `aroon` → up, down, oscillator | TV built-in, 14 |
| ICHIMOKU | `ichimoku` | TV built-in, 9 / 26 / 52 / 26 (see the look-ahead notes below) |
| CHOP | `choppiness` | TV built-in *Choppiness Index*, 14 |
| VORTEX | `vortex` | TV built-in, 14 |
| CHANDELIER_EXIT | `chandelier_exit` | *Chandelier Exit* [everget], 22 / 3.0 / use close |
| UT_BOT | `ut_bot` | *UT Bot Alerts* [QuantNomad], key 1, ATR 10 |
| HEIKIN_ASHI | `heikin_ashi` | Heikin Ashi candles |

### Volume

| Name | Function | Source / defaults |
|---|---|---|
| OBV | `obv` | `ta.cum(sign(change(close)) * volume)` |
| AD | `accdist` | `ta.accdist` |
| CMF | `cmf` | TV built-in, 20 |
| CHAIKIN_OSC | `chaikin_osc` | TV built-in, 3 / 10 |
| PVT | `pvt` | TV built-in |
| EFI | `efi` | Elder Force Index, 13 |
| VWAP_SESSION | `vwap(high, low, close, volume, anchor="D", band_mult)` / `vwap_session(..., session)` | TV built-in *VWAP* on hlc3, with stdev bands. `anchor` is D/W/M/Q/Y. The vbt class takes a `session` id input (`ti.session_ids(index, "D")`) |

## Conventions and accuracy notes

* **Warm-up.** EMA and RMA seed with the SMA of the first `length` values,
  as Pine does. TradingView computes from the first bar of the symbol's
  history, while you compute from the first bar of your data, so any
  recursive indicator (EMA, RSI, ATR, ADX, MACD, Supertrend, ...) differs
  slightly at the start of the data and converges after about
  `4-5 × length` bars. For a precise comparison with a TV chart, load extra
  history before the period you trade.
* **`na` handling** follows Pine: any `na` in a window gives `na`, `x/0`
  gives `na`, and comparisons with `na` are false.
* **Standard deviation** is population stdev (`ta.stdev`, `biased=true`), the
  same as TradingView and TA-Lib. pandas `.std()` defaults to sample stdev
  (`ddof=1`) and does **not** match.
* **No look-ahead**, with one exception: `ichimoku().chikou` is
  `close[t+25]`, which is future data, so never use it in a signal. Use
  `senkou_a` / `senkou_b` (the cloud drawn under the current bar) for
  cloud rules.
* **PSAR** is a direct port of the Pine reference code for `ta.sar`. It
  agrees with TA-Lib on most bars but differs around some reversals,
  because Pine checks for a reversal before clamping SAR to the prior two
  bars' range and TA-Lib clamps first.
* Aroon ties (equal highs) resolve to the most recent bar, as in TA-Lib.

## How it was verified

`tests/test_indicators.py` (34 tests) checks each indicator in one of three ways:

1. Against **TA-Lib** where its formula is the same as TradingView's: SMA,
   EMA, WMA, DEMA, TEMA, LINEARREG, KAMA, BBANDS (SMA, EMA and VWMA basis),
   RSI, STOCH, STOCHRSI, MACD, CCI, WILLR, ROC, MOM, ULTOSC, MFI, TRIX
   (after converting its scale), TRANGE, ATR, NATR, PLUS_DI, MINUS_DI, ADX,
   AROON, AD, OBV and ADOSC. Indicators that only differ in their warm-up
   seed are compared after they converge.
2. Against **bar-by-bar Python ports of the Pine source** for the
   TradingView-only scripts: Supertrend, Chandelier Exit, UT Bot, Fisher,
   BBWP, BBTrend, LazyBear Squeeze, Connors RSI, HMA, ALMA, Keltner,
   Donchian, Ichimoku, VWAP and Heikin Ashi.
3. Every vectorbt class runs, parameter grids work, and the results equal
   the function API.

They have **not** been checked against numbers exported from a TradingView
chart. To spot-check one, export chart data with the indicator on it from
TradingView ("Export chart data") and compare the last few hundred bars.
