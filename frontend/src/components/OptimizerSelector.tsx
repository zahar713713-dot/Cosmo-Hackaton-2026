import React from 'react';
import type { OptimizerAlgorithmType, AlgorithmMetadata } from '../types';
import { Cpu, Rocket, ShieldCheck, Check, Sparkles, TrendingDown, BookOpen } from 'lucide-react';

interface OptimizerSelectorProps {
  currentAlgorithm: OptimizerAlgorithmType;
  algorithms: AlgorithmMetadata[];
  onSelectAlgorithm: (algo: OptimizerAlgorithmType) => void;
  savingsPct?: number;
  isOptimizing?: boolean;
}

export const OptimizerSelector: React.FC<OptimizerSelectorProps> = ({
  currentAlgorithm,
  algorithms,
  onSelectAlgorithm,
  savingsPct = 11.8,
  isOptimizing = false,
}) => {
  const activeMeta = algorithms.find((a) => a.id === currentAlgorithm) || algorithms[0];

  const getAlgorithmIcon = (id: OptimizerAlgorithmType) => {
    switch (id) {
      case 'nasa_milp':
        return <Rocket className="w-4 h-4 text-[#ccff00]" />;
      case 'minimax_robust':
        return <ShieldCheck className="w-4 h-4 text-purple-400" />;
      default:
        return <Cpu className="w-4 h-4 text-white" />;
    }
  };

  return (
    <section className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 mb-6 shadow-2xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 border-b border-neutral-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-[#ccff00] text-black">
            <Cpu className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;мульти-ядерная оптимизация // критерии 18–20&gt;</span>
            </div>
            <h2 className="text-base font-black uppercase tracking-wider text-white">
              МАТЕМАТИЧЕСКИЕ ЯДРА ПЛАНИРОВАНИЯ И ОПТИМИЗАЦИИ
            </h2>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-neutral-500 hidden md:inline">АКТИВНОЕ ЯДРО:</span>
          <span className="px-3 py-1 rounded-full bg-neutral-900 border border-neutral-700 text-[#ccff00] font-black text-xs">
            {activeMeta?.short_name || 'NASA MILP'}
          </span>
        </div>
      </div>

      {/* 3 Algorithm Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        {algorithms.map((algo) => {
          const isSelected = currentAlgorithm === algo.id;
          return (
            <button
              key={algo.id}
              onClick={() => onSelectAlgorithm(algo.id)}
              className={`p-4 rounded-xl border text-left transition-all relative flex flex-col justify-between ${
                isSelected
                  ? 'bg-[#0f110c] border-[#ccff00] shadow-lg shadow-[#ccff00]/10 ring-1 ring-[#ccff00]/50'
                  : 'bg-[#070709] border-neutral-800 hover:border-neutral-700 hover:bg-[#0c0c0e]'
              }`}
            >
              <div className="w-full">
                {/* Top Badge */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    {getAlgorithmIcon(algo.id)}
                    <span className="text-xs font-black uppercase tracking-wider text-white">
                      {algo.short_name}
                    </span>
                  </div>
                  {algo.recommended ? (
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-[#ccff00] text-black font-black uppercase">
                      ★ Целевой
                    </span>
                  ) : algo.id === 'regulatory' ? (
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-300 font-bold uppercase">
                      ТЗ Базовый
                    </span>
                  ) : (
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-purple-900/60 text-purple-300 font-bold uppercase border border-purple-500/40">
                      Живучесть
                    </span>
                  )}
                </div>

                {/* Target Metric */}
                <p className="text-[11px] text-neutral-400 font-medium leading-snug my-2">
                  {algo.target_metric}
                </p>
              </div>

              {/* Footer Selection Indicator */}
              <div className="mt-3 pt-2 border-t border-neutral-800/80 flex items-center justify-between text-[10px] font-mono w-full">
                <span className={isSelected ? 'text-[#ccff00] font-bold flex items-center gap-1' : 'text-neutral-500'}>
                  {isSelected ? (
                    <>
                      <Check className="w-3 h-3 text-[#ccff00]" /> ВЫБРАНО ДЛЯ РАСЧЕТА
                    </>
                  ) : (
                    'ВЫБРАТЬ ЯДРО'
                  )}
                </span>
                {algo.id === 'nasa_milp' && (
                  <span className="text-[#ccff00] font-bold flex items-center gap-0.5">
                    <TrendingDown className="w-3 h-3" /> LCC -{savingsPct.toFixed(1)}%
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Algorithm Scientific Context Strip */}
      {activeMeta && (
        <div className="p-3.5 rounded-xl bg-[#0f0f12] border border-neutral-800 text-xs font-mono flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <div className="p-1.5 rounded-lg bg-neutral-900 border border-neutral-700 text-neutral-400 shrink-0 mt-0.5">
              <BookOpen className="w-3.5 h-3.5 text-[#ccff00]" />
            </div>
            <div>
              <div className="text-[10px] text-neutral-500 uppercase tracking-wide">
                НАУЧНО-ТЕХНИЧЕСКАЯ ОСНОВА: <span className="text-white font-bold">{activeMeta.foundation}</span>
              </div>
              <p className="text-[11px] text-neutral-300 mt-0.5 leading-relaxed">
                {activeMeta.description}
              </p>
            </div>
          </div>

          <div className="shrink-0 flex items-center gap-2 self-end md:self-center">
            {isOptimizing ? (
              <span className="px-4 py-1.5 rounded-full bg-neutral-900 border border-neutral-700 text-neutral-400 text-xs font-mono animate-pulse">
                РАСЧЕТ ЯДРА...
              </span>
            ) : (
              <span className="px-3.5 py-1.5 rounded-full bg-[#ccff00]/10 border border-[#ccff00]/40 text-[#ccff00] text-xs font-mono font-bold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#ccff00]" /> ПЛАН СИНХРОНИЗИРОВАН
              </span>
            )}
          </div>
        </div>
      )}
    </section>
  );
};
