import React from 'react';
import type { ScenarioType } from '../types';
import { RotateCcw, FileSpreadsheet, Sparkles, ShieldAlert, TrendingUp, Globe2, SlidersHorizontal } from 'lucide-react';

interface HeaderProps {
  currentScenario: ScenarioType;
  onSelectScenario: (scen: ScenarioType) => void;
  onReset: () => void;
  onExport: (format: 'xlsx' | 'csv') => void;
  onOpenCustomization: () => void;
  isExporting: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentScenario,
  onSelectScenario,
  onReset,
  onExport,
  onOpenCustomization,
  isExporting,
}) => {
  return (
    <header className="bg-[#050507] border-b border-white/10 px-6 py-5 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto">
        {/* Top Micro-labels matching reference */}
        <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400 mb-3 border-b border-zinc-850 pb-2">
          <div className="flex items-center gap-4">
            <span className="text-[#ccff00]">&lt;orbital_depot&gt;</span>
            <span>Цислунарная транспортная система</span>
            <span className="hidden sm:inline">&lt;horizons: 2035–2040&gt;</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full border border-[#ccff00]/60 text-[#ccff00] font-mono text-[10px] tracking-wider uppercase">
              sys: otu-1 // active
            </span>
          </div>
        </div>

        {/* Hero Title row matching ANCHO WEB SCHOOL reference */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black uppercase tracking-tight text-white leading-none">
              ТОПЛИВНЫЙ КОСМОКОНТУР <span className="text-[#ccff00]">(2035)</span>
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1.5 font-medium max-w-xl">
              Система оперативного планирования поставок, материального баланса, инвестиций и стресс-тестов цислунарного узла
            </p>
          </div>

          {/* Action Buttons styled as rounded pills from the reference */}
          <div className="flex items-center flex-wrap gap-2.5">
            <button
              onClick={onReset}
              className="px-4 py-2 rounded-full bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-bold uppercase tracking-wider border border-zinc-700 transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#ccff00]" />
              Сброс ТЗ
            </button>

            <button
              onClick={onOpenCustomization}
              className="px-4 py-2 rounded-full bg-zinc-900 hover:bg-zinc-800 text-white text-xs font-bold uppercase tracking-wider border border-[#ccff00]/40 hover:border-[#ccff00] transition flex items-center gap-1.5"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-[#ccff00]" />
              Кастомизация (+2045)
            </button>

            <button
              onClick={() => onExport('xlsx')}
              disabled={isExporting}
              className="px-5 py-2.5 rounded-full bg-white hover:bg-zinc-200 text-black text-xs font-black uppercase tracking-wider shadow-lg shadow-white/10 transition flex items-center gap-2 active:scale-95 disabled:opacity-50"
            >
              <FileSpreadsheet className="w-4 h-4 text-black" />
              {isExporting ? 'Экспорт...' : 'FREE Экспорт XLSX'}
            </button>
          </div>
        </div>

        {/* Scenario Pill Navigation Bar */}
        <div className="mt-4 pt-3 border-t border-zinc-850 flex items-center gap-2 overflow-x-auto pb-1">
          <span className="text-[11px] font-mono uppercase text-zinc-400 tracking-wider mr-1">
            Сценарии:
          </span>

          <button
            onClick={() => onSelectScenario('baseline')}
            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider transition-all flex items-center gap-1.5 ${
              currentScenario === 'baseline'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/25 ring-2 ring-[#ccff00]'
                : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Базовый план
          </button>

          <button
            onClick={() => onSelectScenario('stress')}
            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider transition-all flex items-center gap-1.5 ${
              currentScenario === 'stress'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/25 ring-2 ring-[#ccff00]'
                : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            Обязательный стресс-тест
          </button>

          <button
            onClick={() => onSelectScenario('high_demand')}
            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider transition-all flex items-center gap-1.5 ${
              currentScenario === 'high_demand'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/25 ring-2 ring-[#ccff00]'
                : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            Высокий спрос
          </button>

          <button
            onClick={() => onSelectScenario('geopolitical')}
            className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider transition-all flex items-center gap-1.5 ${
              currentScenario === 'geopolitical'
                ? 'bg-[#ccff00] text-black shadow-md shadow-[#ccff00]/25 ring-2 ring-[#ccff00]'
                : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
            }`}
          >
            <Globe2 className="w-3.5 h-3.5" />
            Геополитический шок (+5)
          </button>
        </div>
      </div>
    </header>
  );
};
