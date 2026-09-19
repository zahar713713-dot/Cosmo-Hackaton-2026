import React, { useState } from 'react';
import type { ChannelPlan, InvestmentsState, YearlyBalanceData } from '../types';
import { Sliders, AlertCircle, Clock, Zap, Shield } from 'lucide-react';

interface PlanningSlidersProps {
  channelPlans: Record<number, Record<string, ChannelPlan>>;
  investments: InvestmentsState;
  yearlyBalance: YearlyBalanceData[];
  onChange: (updatedPlans: Record<number, Record<string, ChannelPlan>>) => void;
}

export const PlanningSliders: React.FC<PlanningSlidersProps> = ({
  channelPlans,
  investments,
  yearlyBalance,
  onChange,
}) => {
  const years = Object.keys(channelPlans).map(Number).sort((a, b) => a - b);
  const [selectedYear, setSelectedYear] = useState<number>(2035);
  const [prevChannelStates, setPrevChannelStates] = useState<Record<string, { order: number; res: number }>>({});

  const currentPlans = channelPlans[selectedYear] || {};
  const currentBalance = yearlyBalance.find((b) => b.year === selectedYear);

  const channelsConfig = [
    {
      id: 'Earth-Core',
      name: 'EARTH-CORE',
      code: 'КАНАЛ A',
      sub: 'Базовый контракт // Гарантированное земное плечо',
      maxCap: 190.0,
      varPrice: 6.2,
      resTariff: 0.45,
      topRatio: 0.7,
      isAvailable: true,
      leadTime: '12 мес.',
      badgeStyle: 'bg-[#ccff00]/10 border-[#ccff00]/40 text-[#ccff00]',
    },
    {
      id: 'Earth-Flex',
      name: 'EARTH-FLEX',
      code: 'КАНАЛ B',
      sub: 'Гибкое земное плечо // Без обязательства Take-or-Pay',
      maxCap: 110.0,
      varPrice: 8.9,
      resTariff: 0.15,
      topRatio: 0.0,
      isAvailable: true,
      leadTime: '4 мес.',
      badgeStyle: 'bg-neutral-800 border-neutral-700 text-white',
    },
    {
      id: 'Earth-New',
      name: 'EARTH-NEW',
      code: 'КАНАЛ C',
      sub: 'Новый коммерческий поставщик // Опцион + Ввод',
      maxCap: 130.0,
      varPrice: 7.1,
      resTariff: 0.3,
      topRatio: 0.5,
      isAvailable: investments.earth_new_enabled && selectedYear >= 2038,
      leadTime: '18–24 мес.',
      badgeStyle: 'bg-emerald-950/60 border-emerald-500 text-emerald-400',
    },
    {
      id: 'Lunar-ISRU',
      name: 'LUNAR-ISRU',
      code: 'КАНАЛ D',
      sub: 'Добыча из лунного полярного льда // Нулевой тариф брони',
      maxCap: 120.0,
      varPrice: 3.0,
      resTariff: 0.0,
      topRatio: 0.0,
      isAvailable: investments.isru_enabled && selectedYear >= 2038,
      leadTime: '1–2 мес.',
      badgeStyle: 'bg-purple-950/60 border-purple-500 text-purple-300',
    },
    {
      id: 'Emergency',
      name: 'EMERGENCY',
      code: 'КАНАЛ E',
      sub: 'Аварийный экспресс-канал // Срочные поставки',
      maxCap: 80.0,
      varPrice: 13.8,
      resTariff: 0.35,
      topRatio: 0.0,
      isAvailable: true,
      leadTime: '6 недель',
      badgeStyle: 'bg-amber-950/60 border-amber-500 text-amber-300',
    },
  ];

  const updateOrder = (channelId: string, orderVal: number) => {
    const updated = { ...channelPlans };
    const curYearPlans = { ...updated[selectedYear] };
    const curCh = curYearPlans[channelId] || { reserved_capacity: orderVal, target_order_volume: orderVal };

    const newRes = Math.max(curCh.reserved_capacity, orderVal);
    curYearPlans[channelId] = {
      reserved_capacity: newRes,
      target_order_volume: orderVal,
    };
    updated[selectedYear] = curYearPlans;
    onChange(updated);
  };

  const updateReservation = (channelId: string, resVal: number) => {
    const updated = { ...channelPlans };
    const curYearPlans = { ...updated[selectedYear] };
    const curCh = curYearPlans[channelId] || { reserved_capacity: resVal, target_order_volume: 0 };

    const newOrder = Math.min(curCh.target_order_volume, resVal);
    curYearPlans[channelId] = {
      reserved_capacity: resVal,
      target_order_volume: newOrder,
    };
    updated[selectedYear] = curYearPlans;
    onChange(updated);
  };

  const toggleMaxOrder = (channelId: string, maxCap: number, curOrder: number, curRes: number) => {
    const key = `${selectedYear}_${channelId}_order`;
    const isCurrentlyMax = Math.abs(curOrder - maxCap) < 0.01;

    if (isCurrentlyMax && prevChannelStates[key]) {
      const prev = prevChannelStates[key];
      const updated = { ...channelPlans };
      const curYearPlans = { ...updated[selectedYear] };
      curYearPlans[channelId] = {
        target_order_volume: prev.order,
        reserved_capacity: prev.res,
      };
      updated[selectedYear] = curYearPlans;
      onChange(updated);
    } else {
      setPrevChannelStates((prev) => ({
        ...prev,
        [key]: { order: curOrder, res: curRes },
      }));
      updateOrder(channelId, maxCap);
    }
  };

  const toggleMaxReservation = (channelId: string, maxCap: number, curOrder: number, curRes: number) => {
    const key = `${selectedYear}_${channelId}_res`;
    const isCurrentlyMax = Math.abs(curRes - maxCap) < 0.01;

    if (isCurrentlyMax && prevChannelStates[key]) {
      const prev = prevChannelStates[key];
      const updated = { ...channelPlans };
      const curYearPlans = { ...updated[selectedYear] };
      curYearPlans[channelId] = {
        target_order_volume: prev.order,
        reserved_capacity: prev.res,
      };
      updated[selectedYear] = curYearPlans;
      onChange(updated);
    } else {
      setPrevChannelStates((prev) => ({
        ...prev,
        [key]: { order: curOrder, res: curRes },
      }));
      updateReservation(channelId, maxCap);
    }
  };

  return (
    <section className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 mb-6 shadow-2xl">
      {/* Header & Year Selector */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-5 border-b border-neutral-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-[#ccff00] text-black">
            <Sliders className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;управление поставками&gt;</span>
            </div>
            <h2 className="text-base font-black uppercase tracking-wider text-white">
              ГОДОВОЕ ПЛАНИРОВАНИЕ ЗАКУПОК И БРОНИРОВАНИЯ
            </h2>
            <p className="text-xs text-neutral-400 font-mono">
              Оперативный выбор отбора топлива и резервирования по 5 каналам доставки
            </p>
          </div>
        </div>

        {/* Year Pills (Brutalist style) */}
        <div className="flex items-center gap-1.5 p-1.5 bg-[#050507] rounded-full border border-neutral-800 overflow-x-auto max-w-full touch-pan-x scrollbar-none w-full sm:w-auto">
          {years.map((y) => (
            <button
              key={y}
              onClick={() => setSelectedYear(y)}
              className={`px-3.5 py-1 rounded-full text-xs font-black font-mono transition-all uppercase whitespace-nowrap shrink-0 ${
                selectedYear === y
                  ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/20'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
              }`}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Year Overview Strip */}
      {currentBalance && (
        <div className="mb-5 grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-3 p-3 sm:p-3.5 rounded-2xl bg-[#0f0f12] border border-neutral-800 text-xs font-mono">
          <div className="bg-[#070709] border border-neutral-800/80 rounded-xl p-3 text-center flex flex-col items-center justify-between">
            <span className="text-neutral-500 text-[10px] uppercase">&lt;спрос года&gt;</span>
            <div className="text-lg font-black text-white my-1">
              {currentBalance.demand_total.toFixed(1)} <span className="text-xs font-normal text-neutral-400">Т</span>
            </div>
            <span className="text-[10px] text-neutral-400">Критический: {currentBalance.demand_critical.toFixed(1)} т</span>
          </div>

          <div className="bg-[#070709] border border-neutral-800/80 rounded-xl p-3 text-center flex flex-col items-center justify-between">
            <span className="text-neutral-500 text-[10px] uppercase">&lt;заказ / потери&gt;</span>
            <div className="text-lg font-black text-[#ccff00] my-1">
              {currentBalance.gross_delivery.toFixed(1)} <span className="text-xs font-normal text-neutral-400">Т</span>
            </div>
            <span className="text-[10px] text-neutral-400">Потери: {currentBalance.losses.toFixed(1)} т</span>
          </div>

          <div className="bg-[#070709] border border-neutral-800/80 rounded-xl p-3 text-center flex flex-col items-center justify-between">
            <span className="text-neutral-500 text-[10px] uppercase">&lt;остаток на конец&gt;</span>
            <div
              className={`text-lg font-black my-1 ${
                currentBalance.is_storage_overflow ? 'text-[#ff2a5f]' : 'text-white'
              }`}
            >
              {currentBalance.end_stock.toFixed(1)} <span className="text-xs font-normal text-neutral-400">Т</span>
            </div>
            <span className="text-[10px] text-neutral-400">Вместимость: {currentBalance.storage_capacity_max} т</span>
          </div>

          <div className="bg-[#070709] border border-neutral-800/80 rounded-xl p-3 text-center flex flex-col items-center justify-between">
            <span className="text-neutral-500 text-[10px] uppercase">&lt;уровень сервиса&gt;</span>
            <div
              className={`text-lg font-black my-1 ${
                currentBalance.deficit_total > 0 ? 'text-[#ff2a5f] animate-pulse' : 'text-[#ccff00]'
              }`}
            >
              {(currentBalance.service_level_total * 100).toFixed(1)}%
            </div>
            <span className="text-[10px] text-neutral-400">
              {currentBalance.deficit_total > 0 ? `Дефицит: ${currentBalance.deficit_total.toFixed(1)} т` : 'Дефицит: 0 т'}
            </span>
          </div>
        </div>
      )}

      {/* Striped Channel Rows (Cyber-Brutalist design) */}
      <div className="space-y-3">
        {channelsConfig.map((ch) => {
          const plan = currentPlans[ch.id] || { reserved_capacity: 0, target_order_volume: 0 };
          const topThreshold = ch.topRatio * plan.reserved_capacity;
          const isTopPenalized = plan.target_order_volume < topThreshold && plan.reserved_capacity > 0;
          const isOrderMax = Math.abs(plan.target_order_volume - ch.maxCap) < 0.01;
          const isResMax = Math.abs(plan.reserved_capacity - ch.maxCap) < 0.01;

          return (
            <div
              key={ch.id}
              className={`p-4 rounded-xl border transition-all ${
                !ch.isAvailable
                  ? 'bg-[#0a0a0c] border-neutral-900 opacity-40'
                  : isTopPenalized
                  ? 'bg-[#140f08] border-amber-500/50'
                  : 'bg-[#0e0e11] border-neutral-800/90 hover:border-neutral-700'
              }`}
            >
              {/* Row Header */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2.5 mb-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-[10px] font-black font-mono px-2.5 py-0.5 rounded-full border ${ch.badgeStyle}`}>
                    {ch.code}
                  </span>
                  <span className="text-sm font-black uppercase tracking-wider text-white">{ch.name}</span>
                  <span className="text-xs text-neutral-400 font-medium hidden sm:inline">{ch.sub}</span>
                </div>

                <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs font-mono">
                  <span className="text-neutral-400">
                    Тариф: <b className="text-white">{ch.varPrice}</b> млн/т
                  </span>
                  <span className="text-neutral-600 hidden sm:inline">|</span>
                  <span className="text-neutral-400">
                    Бронь: <b className="text-white">{ch.resTariff}</b> млн/т
                  </span>
                  <span className="text-neutral-600 hidden sm:inline">|</span>
                  <span className="text-neutral-400">
                    TOP: <b className="text-[#ccff00]">{ch.topRatio * 100}%</b>
                  </span>
                  <span className="text-neutral-600 hidden sm:inline">|</span>
                  <span className="text-neutral-400 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-neutral-500" /> {ch.leadTime}
                  </span>
                </div>
              </div>

              {!ch.isAvailable ? (
                <div className="py-2.5 px-3.5 rounded-xl bg-[#0e0e11] border border-neutral-800 text-xs font-mono flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2 text-neutral-400">
                    <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>
                      {ch.id === 'Earth-New' && !investments.earth_new_enabled && (
                        <>
                          Канал C не законтрактован. Включите тумблер в карточке <b className="text-emerald-400">«EARTH-NEW (ОПЦИОН)»</b> в блоке инвестиций выше.
                        </>
                      )}
                      {ch.id === 'Earth-New' && investments.earth_new_enabled && selectedYear < 2038 && (
                        <>
                          Канал C законтрактован (цикл создания 18–24 мес.). Поставки доступны <b className="text-white">с 2038 года</b>.
                        </>
                      )}
                      {ch.id === 'Lunar-ISRU' && !investments.isru_enabled && (
                        <>
                          Лунная добыча отключена. Активируйте карточку <b className="text-purple-400">«LUNAR-ISRU»</b> в блоке инвестиций выше.
                        </>
                      )}
                      {ch.id === 'Lunar-ISRU' && investments.isru_enabled && selectedYear < 2038 && (
                        <>
                          Развертывание лунной инфраструктуры (2035–2037). Доступ к топливу открывается <b className="text-white">с 2038 года</b>.
                        </>
                      )}
                    </span>
                  </div>
                  {((ch.id === 'Earth-New' && investments.earth_new_enabled && selectedYear < 2038) ||
                    (ch.id === 'Lunar-ISRU' && investments.isru_enabled && selectedYear < 2038)) && (
                    <button
                      onClick={() => setSelectedYear(2038)}
                      className="text-[11px] font-bold text-black bg-[#ccff00] hover:bg-[#b3e600] px-3 py-1 rounded-full shrink-0 transition"
                    >
                      Перейти к 2038 году →
                    </button>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
                  {/* Order Volume Slider & Numeric Stepper */}
                  <div className="p-3 rounded-lg bg-[#070709] border border-neutral-850">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-mono text-neutral-400 flex items-center gap-1.5">
                        <Zap className="w-3.5 h-3.5 text-[#ccff00]" />
                        Фактический отбор:
                      </span>
                      <div className="flex items-center gap-1 bg-[#050507] p-1 rounded-lg border border-neutral-800">
                        <button
                          type="button"
                          onClick={() => updateOrder(ch.id, Math.max(0, Math.round((plan.target_order_volume - 5) * 10) / 10))}
                          className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Уменьшить на 5 т"
                        >
                          -5
                        </button>
                        <button
                          type="button"
                          onClick={() => updateOrder(ch.id, Math.max(0, Math.round((plan.target_order_volume - 1) * 10) / 10))}
                          className="w-5 h-5 flex items-center justify-center text-xs font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Уменьшить на 1 т"
                        >
                          -
                        </button>
                        <div className="flex items-center">
                          <input
                            type="number"
                            min={0}
                            max={ch.maxCap}
                            step="any"
                            value={Number(plan.target_order_volume.toFixed(1))}
                            onChange={(e) => {
                              const val = parseFloat(e.target.value);
                              if (!isNaN(val)) {
                                const clamped = Math.max(0, Math.min(ch.maxCap, val));
                                updateOrder(ch.id, Math.round(clamped * 10) / 10);
                              }
                            }}
                            className="w-14 h-6 text-center text-xs font-mono font-black bg-neutral-950 border border-[#ccff00]/40 focus:border-[#ccff00] focus:ring-1 focus:ring-[#ccff00] text-[#ccff00] rounded outline-none px-1 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                          />
                          <span className="text-[10px] font-mono text-neutral-400 ml-1">т</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => updateOrder(ch.id, Math.min(ch.maxCap, Math.round((plan.target_order_volume + 1) * 10) / 10))}
                          className="w-5 h-5 flex items-center justify-center text-xs font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Увеличить на 1 т"
                        >
                          +
                        </button>
                        <button
                          type="button"
                          onClick={() => updateOrder(ch.id, Math.min(ch.maxCap, Math.round((plan.target_order_volume + 5) * 10) / 10))}
                          className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Увеличить на 5 т"
                        >
                          +5
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleMaxOrder(ch.id, ch.maxCap, plan.target_order_volume, plan.reserved_capacity)}
                          className={`px-1.5 py-0.5 text-[10px] font-mono font-black rounded border transition ml-0.5 active:scale-95 ${
                            isOrderMax
                              ? 'bg-[#ccff00] text-black border-[#ccff00] shadow-sm shadow-[#ccff00]/30'
                              : 'bg-[#ccff00]/15 hover:bg-[#ccff00]/25 text-[#ccff00] border-[#ccff00]/40'
                          }`}
                          title={isOrderMax ? 'Повторный клик вернет значение до нажатия MAX' : 'Установить максимальный отбор (повторный клик вернет прежнее значение)'}
                        >
                          MAX
                        </button>
                      </div>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={ch.maxCap}
                      step={0.5}
                      value={plan.target_order_volume}
                      onChange={(e) => updateOrder(ch.id, Number(e.target.value))}
                      className="w-full accent-[#ccff00] cursor-pointer h-3 sm:h-2.5 bg-neutral-800 rounded-lg touch-manipulation my-1"
                    />
                    <div className="flex justify-between text-[10px] text-neutral-500 font-mono mt-1">
                      <span>0 т</span>
                      <span>Предел: {ch.maxCap} т/год</span>
                    </div>
                  </div>

                  {/* Reservation Slider & Numeric Stepper */}
                  <div className="p-3 rounded-lg bg-[#070709] border border-neutral-850">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <span className="text-xs font-mono text-neutral-400 flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5 text-white" />
                        Бронь мощности:
                      </span>
                      <div className="flex items-center gap-1 bg-[#050507] p-1 rounded-lg border border-neutral-800">
                        <button
                          type="button"
                          onClick={() => updateReservation(ch.id, Math.max(0, Math.round((plan.reserved_capacity - 5) * 10) / 10))}
                          className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Уменьшить на 5 т"
                        >
                          -5
                        </button>
                        <button
                          type="button"
                          onClick={() => updateReservation(ch.id, Math.max(0, Math.round((plan.reserved_capacity - 1) * 10) / 10))}
                          className="w-5 h-5 flex items-center justify-center text-xs font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Уменьшить на 1 т"
                        >
                          -
                        </button>
                        <div className="flex items-center">
                          <input
                            type="number"
                            min={0}
                            max={ch.maxCap}
                            step="any"
                            value={Number(plan.reserved_capacity.toFixed(1))}
                            onChange={(e) => {
                              const val = parseFloat(e.target.value);
                              if (!isNaN(val)) {
                                const clamped = Math.max(0, Math.min(ch.maxCap, val));
                                updateReservation(ch.id, Math.round(clamped * 10) / 10);
                              }
                            }}
                            className="w-14 h-6 text-center text-xs font-mono font-black bg-neutral-950 border border-neutral-700 focus:border-white focus:ring-1 focus:ring-white text-white rounded outline-none px-1 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                          />
                          <span className="text-[10px] font-mono text-neutral-400 ml-1">т</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => updateReservation(ch.id, Math.min(ch.maxCap, Math.round((plan.reserved_capacity + 1) * 10) / 10))}
                          className="w-5 h-5 flex items-center justify-center text-xs font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Увеличить на 1 т"
                        >
                          +
                        </button>
                        <button
                          type="button"
                          onClick={() => updateReservation(ch.id, Math.min(ch.maxCap, Math.round((plan.reserved_capacity + 5) * 10) / 10))}
                          className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-neutral-900 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded border border-neutral-800 transition active:scale-95"
                          title="Увеличить на 5 т"
                        >
                          +5
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleMaxReservation(ch.id, ch.maxCap, plan.target_order_volume, plan.reserved_capacity)}
                          className={`px-1.5 py-0.5 text-[10px] font-mono font-black rounded border transition ml-0.5 active:scale-95 ${
                            isResMax
                              ? 'bg-white text-black border-white shadow-sm shadow-white/30'
                              : 'bg-white/15 hover:bg-white/25 text-white border-white/40'
                          }`}
                          title={isResMax ? 'Повторный клик вернет значение до нажатия MAX' : 'Установить максимальную бронь (повторный клик вернет прежнее значение)'}
                        >
                          MAX
                        </button>
                      </div>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={ch.maxCap}
                      step={0.5}
                      value={plan.reserved_capacity}
                      onChange={(e) => updateReservation(ch.id, Number(e.target.value))}
                      className="w-full accent-white cursor-pointer h-3 sm:h-2.5 bg-neutral-800 rounded-lg touch-manipulation my-1"
                    />
                    <div className="flex justify-between text-[10px] text-neutral-500 font-mono mt-1">
                      <span>Порог TOP: {topThreshold.toFixed(1)} т</span>
                      {isTopPenalized ? (
                        <span className="text-amber-400 flex items-center gap-1 font-semibold">
                          <AlertCircle className="w-3 h-3" /> Оплата за {topThreshold.toFixed(1)} т (Take-or-Pay)
                        </span>
                      ) : (
                        <span className="text-neutral-500">Штрафов нет</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};

