export type ChannelID = 'Earth-Core' | 'Earth-Flex' | 'Earth-New' | 'Lunar-ISRU' | 'Emergency' | 'Custom-F';

export type ScenarioType = 'baseline' | 'stress' | 'high_demand' | 'low_demand' | 'geopolitical' | 'custom';

export interface ChannelPlan {
  reserved_capacity: number;
  target_order_volume: number;
}

export interface InvestmentsState {
  zbo_year: number | null;
  isru_enabled: boolean;
  isru_capex_schedule: Record<number, number>;
  earth_new_enabled: boolean;
  earth_new_option_year: number | null;
  earth_new_exercise_year: number | null;
}

export interface CustomChannelConfig {
  enabled: boolean;
  name: string;
  max_capacity: number;
  var_cost: number;
  res_tariff: number;
  take_or_pay: number;
  reliability: number;
}

export interface YearlyBalanceData {
  year: number;
  start_stock: number;
  gross_delivery: number;
  losses: number;
  net_available_inflow: number;
  total_fuel_available: number;
  demand_total: number;
  demand_critical: number;
  served_demand_total: number;
  served_demand_critical: number;
  deficit_total: number;
  deficit_critical: number;
  end_stock: number;
  storage_capacity_max: number;
  is_storage_overflow: boolean;
  overflow_amount: number;
  required_reserve_45d: number;
  is_reserve_satisfied: boolean;
  service_level_total: number;
  service_level_critical: number;
  channel_deliveries: Record<string, number>;
}

export interface YearlyEconomicsData {
  year: number;
  procurement_cost: number;
  reservation_cost: number;
  storage_holding_cost: number;
  zbo_fixed_opex: number;
  isru_fixed_opex: number;
  initial_stock_acquisition_cost: number;
  total_opex: number;
  capex_zbo: number;
  capex_earth_new: number;
  capex_isru: number;
  total_capex: number;
  total_expenditure: number;
  discount_factor: number;
  discounted_expenditure: number;
  channel_payments: Record<string, number>;
}

export interface ConstraintViolationItem {
  year: string;
  rule_code: string;
  rule_name: string;
  expected: string;
  actual: string;
  message: string;
  is_violated: boolean;
}

export interface SummaryKPI {
  is_feasible: boolean;
  total_demand_tons: number;
  total_served_demand_tons: number;
  total_deficit_tons: number;
  average_service_level_total: number;
  average_service_level_critical: number;
  total_gross_delivery_tons: number;
  total_losses_tons: number;
  total_opex_m_cu: number;
  total_capex_m_cu: number;
  total_cost_m_cu: number;
  npv_cost_m_cu: number;
  cost_per_ton_served_m_cu: number;
  discounted_cost_per_ton_served_m_cu: number;
}

export interface SimulationResult {
  scenario_type: string;
  scenario_name: string;
  is_feasible: boolean;
  summary_kpi: SummaryKPI;
  yearly_balance: YearlyBalanceData[];
  yearly_economics: YearlyEconomicsData[];
  violations: ConstraintViolationItem[];
}

export type OptimizerAlgorithmType = 'regulatory' | 'nasa_milp' | 'minimax_robust';

export interface AlgorithmMetadata {
  id: OptimizerAlgorithmType;
  name: string;
  short_name: string;
  foundation: string;
  description: string;
  target_metric: string;
  badge_style: string;
  recommended: boolean;
}

export interface OptimizeResponse {
  algorithm: OptimizerAlgorithmType;
  metadata: AlgorithmMetadata;
  channel_plans: Record<number, Record<string, ChannelPlan>>;
  simulation: SimulationResult;
  comparison_with_regulatory: {
    regulatory_npv: number;
    current_npv: number;
    delta_npv: number;
    savings_pct: number;
  };
}

