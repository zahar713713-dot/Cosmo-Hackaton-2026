import React from 'react';
import type { InvestmentsState } from '../types';
import { ShieldCheck, Moon, Globe, DollarSign, Calendar } from 'lucide-react';

interface InvestmentControlsProps {
  investments: InvestmentsState;
  onChange: (updated: InvestmentsState) => void;
}

export const InvestmentControls: React.FC<InvestmentControlsProps> = ({ investments, onChange }) => {
  const toggleZbo = (checked: boolean) => {
    onChange({
      ...investments,
      zbo_year: checked ? investments.zbo_year || 2036 : null,
    });
  };

  const setZboYear = (year: number) => {
    onChange({
      ...investments,
      zbo_year: year,
    });
  };

  const toggleIsru = (checked: boolean) => {
    onChange({
      ...investments,
      isru_enabled: checked,
    });
  };

  const toggleEarthNew = (checked: boolean) => {
    onChange({
      ...investments,
      earth_new_enabled: checked,
      earth_new_option_year: checked ? 2035 : null,
      earth_new_exercise_year: checked ? 2036 : null,
    });
  };

  return (
    <section className="bg-[#0a0a0c] rounded-2xl border border-neutral-800 p-5 mb-6 shadow-2xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 border-b border-neutral-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-[#ccff00] text-black">
            <DollarSign className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;капитальные затраты capex&gt;</span>
            </div>
            <h2 className="text-base font-black uppercase tracking-wider text-white">
              ИНВЕСТИЦИОННЫЕ ВОРОТА И СТРАТЕГИЧЕСКИЕ РЕШЕНИЯ
            </h2>
            <p className="text-xs text-neutral-400 font-mono">
              Управление модернизацией ZBO, лунной добычей ISRU и опционом Earth-New
            </p>
          </div>
        </div>
        <span className="text-[11px] text-neutral-500 font-mono hidden sm:inline">&lt;критерий 9: инвестиции&gt;</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-stretch">
        {/* 1. ZBO Modernization */}
        <div
          className={`h-full min-h-[220px] p-5 rounded-2xl border transition-all flex flex-col justify-between ${
            investments.zbo_year !== null
              ? 'bg-[#0f110c] border-[#ccff00]/60 shadow-lg shadow-[#ccff00]/5'
              : 'bg-[#0c0c0e] border-neutral-800 opacity-70'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;шлюз 01 // хранилище&gt;</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={investments.zbo_year !== null}
                  onChange={(e) => toggleZbo(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#ccff00] peer-checked:after:bg-black"></div>
              </label>
            </div>

            <div className="flex items-center gap-2.5 mb-2">
              <div className="p-2 rounded-lg bg-neutral-900 text-[#ccff00] border border-neutral-800">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-black uppercase tracking-wider text-white">ZBO-МОДЕРНИЗАЦИЯ</h3>
                <span className="text-[10px] text-[#ccff00] font-mono">CAPEX: 180 млн // OPEX: +12 млн/год</span>
              </div>
            </div>

            <p className="text-xs text-neutral-400 mt-3 leading-relaxed">
              Снижает потери оборота с <b className="text-white">4.5% до 1.2%</b> и расширяет емкость баков с{' '}
              <b className="text-white">70 до 120 тонн</b>. Критично для прохождения стресс-теста (норма ≤2%).
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between text-xs font-mono">
            <span className="text-neutral-500 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#ccff00]" /> Год ввода:
            </span>
            {investments.zbo_year !== null ? (
              <select
                value={investments.zbo_year}
                onChange={(e) => setZboYear(Number(e.target.value))}
                className="bg-black border border-neutral-700 text-[#ccff00] font-black text-xs rounded-full px-3 py-1 font-mono focus:outline-none focus:border-[#ccff00]"
              >
                {[2036, 2037, 2038, 2039, 2040].map((y) => (
                  <option key={y} value={y}>
                    {y} ГОД
                  </option>
                ))}
              </select>
            ) : (
              <span className="text-neutral-600 font-bold">НЕ ЗАПЛАНИРОВАН</span>
            )}
          </div>
        </div>

        {/* 2. Lunar-ISRU Pilot */}
        <div
          className={`h-full min-h-[220px] p-5 rounded-2xl border transition-all flex flex-col justify-between ${
            investments.isru_enabled
              ? 'bg-[#0e0c14] border-purple-500/60 shadow-lg shadow-purple-950/20'
              : 'bg-[#0c0c0e] border-neutral-800 opacity-70'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;шлюз 02 // лунная база&gt;</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={investments.isru_enabled}
                  onChange={(e) => toggleIsru(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-500 peer-checked:after:bg-black"></div>
              </label>
            </div>

            <div className="flex items-center gap-2.5 mb-2">
              <div className="p-2 rounded-lg bg-neutral-900 text-purple-400 border border-neutral-800">
                <Moon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-black uppercase tracking-wider text-white">LUNAR-ISRU (ЛУНА)</h3>
                <span className="text-[10px] text-purple-400 font-mono">CAPEX: 1 250 млн // Ввод с 2038 г.</span>
              </div>
            </div>

            <p className="text-xs text-neutral-400 mt-3 leading-relaxed">
              Добыча топлива из лунного полярного льда. Потенциал <b className="text-white">120 т/год</b> по себестоимости{' '}
              <b className="text-[#ccff00]">3.0 млн/т</b> без платы за бронь. OPEX: +70 млн/год.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between text-xs font-mono">
            <span className="text-neutral-500">График траншей:</span>
            <span className={investments.isru_enabled ? 'text-purple-300 font-bold' : 'text-neutral-600 font-bold'}>
              {investments.isru_enabled ? '250 (35) + 500 (36) + 500 (37)' : 'НЕ ФИНАНСИРУЕТСЯ'}
            </span>
          </div>
        </div>

        {/* 3. Earth-New Option */}
        <div
          className={`h-full min-h-[220px] p-5 rounded-2xl border transition-all flex flex-col justify-between ${
            investments.earth_new_enabled
              ? 'bg-[#0a110d] border-emerald-500/60 shadow-lg shadow-emerald-950/20'
              : 'bg-[#0c0c0e] border-neutral-800 opacity-70'
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] text-neutral-500 font-mono">&lt;шлюз 03 // поставщик C&gt;</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={investments.earth_new_enabled}
                  onChange={(e) => toggleEarthNew(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-neutral-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500 peer-checked:after:bg-black"></div>
              </label>
            </div>

            <div className="flex items-center gap-2.5 mb-2">
              <div className="p-2 rounded-lg bg-neutral-900 text-emerald-400 border border-neutral-800">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-black uppercase tracking-wider text-white">EARTH-NEW (ОПЦИОН)</h3>
                <span className="text-[10px] text-emerald-400 font-mono">90 млн опцион + 270 млн ввод = 360 млн</span>
              </div>
            </div>

            <p className="text-xs text-neutral-400 mt-3 leading-relaxed">
              Новая коммерческая РН: мощность <b className="text-white">130 т/год</b> по цене <b className="text-white">7.1 млн/т</b>{' '}
              (бронь 0.30, TOP 50%). Страховочное плечо при задержке запуска Lunar-ISRU.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between text-xs font-mono">
            <span className="text-neutral-500">Статус контракта:</span>
            <span className={investments.earth_new_enabled ? 'text-emerald-400 font-bold' : 'text-neutral-600'}>
              {investments.earth_new_enabled ? 'АКТИВЕН С 2038 ГОДА' : 'НЕ ЗАКОНТРАКТОВАН'}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};


