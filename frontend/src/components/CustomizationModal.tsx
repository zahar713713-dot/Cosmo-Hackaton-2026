import React from 'react';
import type { CustomChannelConfig } from '../types';
import { X, SlidersHorizontal } from 'lucide-react';

interface CustomizationModalProps {
  isOpen: boolean;
  onClose: () => void;
  extendedHorizon: boolean;
  onToggleExtendedHorizon: (enabled: boolean) => void;
  customChannel: CustomChannelConfig;
  onUpdateCustomChannel: (cfg: CustomChannelConfig) => void;
  discountRate: number;
  onUpdateDiscountRate: (rate: number) => void;
}

export const CustomizationModal: React.FC<CustomizationModalProps> = ({
  isOpen,
  onClose,
  extendedHorizon,
  onToggleExtendedHorizon,
  customChannel,
  onUpdateCustomChannel,
  discountRate,
  onUpdateDiscountRate,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-3 sm:p-4 overflow-y-auto">
      <div className="bg-[#0c0c0e] border border-neutral-800 rounded-2xl max-w-xl w-full p-4 sm:p-6 shadow-2xl relative max-h-[92vh] overflow-y-auto my-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full bg-neutral-900 text-neutral-400 hover:text-white border border-neutral-800 transition"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6 border-b border-neutral-800 pb-4">
          <div className="p-2 rounded-xl bg-[#ccff00] text-black">
            <SlidersHorizontal className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <span className="text-[10px] text-neutral-500 font-mono">&lt;критерий 20: расширяемость&gt;</span>
            <h2 className="text-base font-black uppercase tracking-wider text-white">
              МАСШТАБИРУЕМОСТЬ И ПАРАМЕТРЫ
            </h2>
          </div>
        </div>

        {/* 1. Extended Horizon up to 2045 */}
        <div className="p-4 rounded-xl bg-[#070709] border border-neutral-800 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;горизонт планирования&gt;</span>
              <h3 className="text-xs font-black uppercase tracking-wider text-white mt-0.5">
                Расширение сетки до 2045 года (11 лет)
              </h3>
              <p className="text-[11px] text-neutral-400 mt-1">
                Добавляет в расчетную сетку годы 2041–2045 с экстраполяцией спроса и инвестиций.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={extendedHorizon}
                onChange={(e) => onToggleExtendedHorizon(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#ccff00] peer-checked:after:bg-black"></div>
            </label>
          </div>
          <div className="mt-2 text-[10px] font-mono text-[#ccff00]">
            {extendedHorizon ? 'АКТИВЕН ГОРИЗОНТ: 2035–2045 ГГ.' : 'БАЗОВЫЙ ГОРИЗОНТ: 2035–2040 ГГ.'}
          </div>
        </div>

        {/* 2. Custom Channel F */}
        <div className="p-4 rounded-xl bg-[#070709] border border-neutral-800 mb-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <span className="text-[10px] text-neutral-500 font-mono">&lt;динамический поставщик&gt;</span>
              <h3 className="text-xs font-black uppercase tracking-wider text-white mt-0.5">
                Подключение синтетического «Канала F»
              </h3>
              <p className="text-[11px] text-neutral-400 mt-1">
                Проверка масштабируемости через конфигурацию (без изменения ядра).
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={customChannel.enabled}
                onChange={(e) => onUpdateCustomChannel({ ...customChannel, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#ccff00] peer-checked:after:bg-black"></div>
            </label>
          </div>

          {customChannel.enabled && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3 pt-3 border-t border-neutral-800 text-xs font-mono">
              <div>
                <label className="text-[10px] text-neutral-400">Название:</label>
                <input
                  type="text"
                  value={customChannel.name}
                  onChange={(e) => onUpdateCustomChannel({ ...customChannel, name: e.target.value })}
                  className="w-full mt-1 bg-black border border-neutral-700 rounded px-2.5 py-1 text-white text-xs"
                />
              </div>
              <div>
                <label className="text-[10px] text-neutral-400">Мощность (т):</label>
                <input
                  type="number"
                  value={customChannel.max_capacity}
                  onChange={(e) => onUpdateCustomChannel({ ...customChannel, max_capacity: Number(e.target.value) })}
                  className="w-full mt-1 bg-black border border-neutral-700 rounded px-2.5 py-1 text-white text-xs"
                />
              </div>
              <div>
                <label className="text-[10px] text-neutral-400">Тариф (млн/т):</label>
                <input
                  type="number"
                  step="0.1"
                  value={customChannel.var_cost}
                  onChange={(e) => onUpdateCustomChannel({ ...customChannel, var_cost: Number(e.target.value) })}
                  className="w-full mt-1 bg-black border border-neutral-700 rounded px-2.5 py-1 text-white text-xs"
                />
              </div>
            </div>
          )}
        </div>

        {/* 3. Discount rate */}
        <div className="p-4 rounded-xl bg-[#070709] border border-neutral-800">
          <div className="flex items-center justify-between text-xs mb-2 font-mono">
            <span className="text-white font-bold">Ставка дисконтирования (r):</span>
            <span className="text-[#ccff00] font-black text-sm">{(discountRate * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min={0.02}
            max={0.2}
            step={0.01}
            value={discountRate}
            onChange={(e) => onUpdateDiscountRate(Number(e.target.value))}
            className="w-full accent-[#ccff00] cursor-pointer h-2 bg-neutral-800 rounded-lg mt-1"
          />
          <div className="flex justify-between text-[10px] text-neutral-500 font-mono mt-1">
            <span>2%</span>
            <span>Базовая норма: 8% (ТЗ)</span>
            <span>20%</span>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-full bg-[#ccff00] text-black font-black uppercase text-xs hover:bg-[#b8e600] transition shadow-lg shadow-[#ccff00]/20"
          >
            Применить параметры
          </button>
        </div>
      </div>
    </div>
  );
};

