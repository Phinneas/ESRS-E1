# Input format

Everything the agents use about the client goes in `inputs/`. Agents read it. They never change it.

With `inputs.format: yaml`, use these files. Leave a key out if you do not have it. Do not write 0 for unknown.

## inputs/company.yaml

```yaml
profile:
  employees: 0
  net_revenue: 0           # in client.yaml currency
  sites: [{name: "", country: "", activity: ""}]
  value_chain: ""          # short description, upstream and downstream
governance:
  climate_oversight_body: ""      # e.g. "Board sustainability committee"
  climate_in_incentives: null     # true | false
  incentive_detail: ""
materiality:
  climate_material: null          # true | false
  method: ""                      # how impacts, risks, opportunities were assessed
  impacts: [{description: "", actual_or_potential: "", time_horizon: ""}]
  risks: [{description: "", type: physical | transition, time_horizon: ""}]
  opportunities: [{description: "", time_horizon: ""}]
transition_plan:
  exists: null                    # true | false
  approved_by: ""
  expected_adoption: ""           # if exists is false
  decarbonisation_levers: [{lever: "", expected_reduction_tco2e: 0, by_year: 0}]
  capex_coal_oil_gas: null        # amount, only if the client has these activities
  locked_in_emissions: ""
  assumptions: ""
  progress: ""
policies: [{name: "", covers: [mitigation, adaptation, energy], scope: "", owner: ""}]
actions: [{name: "", lever: "", status: "", resources: "", expected_reduction_tco2e: 0}]
targets:
  - type: absolute | intensity
    scopes: [1, 2, 3]
    base_year: 0
    base_value_tco2e: 0
    target_year: 0
    target_value_tco2e: 0
    scope2_method: market | location
    science_based: null
    validated_by: ""              # e.g. "SBTi, 2026"
    net_zero_year: null
    residual_neutralisation: ""   # required if net_zero_year is set (E1 AR 11)
resilience:
  scenarios_used: [{name: "", type: high_emission | 1_5c, temperature: ""}]
  scope_of_analysis: ""
  time_horizons: ""
  findings: ""
  uncertainties: ""
internal_carbon_price: [{scheme: "", price_per_tco2e: 0, scope: "", consistency_with_impairment: ""}]
financial_effects:
  assets_at_physical_risk: null
  assets_at_physical_risk_adapted_pct: null
  revenue_at_physical_risk: null
  assets_at_transition_risk: null
  assets_at_transition_risk_mitigated_pct: null
  real_estate_by_energy_class: {}
  revenue_at_transition_risk: null
  opportunities_revenue: null
```

## inputs/emissions.yaml

```yaml
period: ""
boundary: financial_control       # must match client.yaml
gwp_set: AR6                      # IPCC assessment report used
scope1:
  total_tco2e: 0
  eu_ets_tco2e: 0                 # only if the client has EU ETS sources
  by_source: {stationary: 0, mobile: 0, process: 0, fugitive: 0}
scope2:
  location_based_tco2e: 0
  market_based_tco2e: 0
scope3:
  screening_note: ""              # how all 15 categories were screened (E1 AR 24(b))
  categories:                     # significant ones only
    - number: 1
      name: Purchased goods and services
      tco2e: 0
      method: spend | activity | supplier_specific | hybrid
      cloud_and_data_centres_tco2e: null   # subset of category 1, if applicable
biogenic_co2_tco2e: null
consolidated_group_split:         # E1-8 para 30(c)
  scope1_consolidated: 0
  scope1_other: 0
  scope2_consolidated: 0
  scope2_other: 0
removals: [{project: "", tco2e: 0, method: "", reversals_tco2e: 0}]
carbon_credits:
  cancelled_tco2e: 0
  purchased_not_cancelled_tco2e: 0
  standards: []                   # e.g. ["Verra VCS", "Gold Standard"]
  nature_based_pct: null
  planned_future_cancellations_tco2e: 0
comparative:
  year: 0
  scope1_tco2e: 0
  scope2_location_tco2e: 0
  scope2_market_tco2e: 0
  scope3_tco2e: 0
```

In `emissions.mode: calculated`, add `inputs/activity.csv` with columns
`scope,category,activity,quantity,unit,factor,factor_unit,factor_source,gas`.

## inputs/energy.yaml

```yaml
unit: MWh
fossil_total: 0
nuclear_total: 0
renewable_total: 0
fossil_breakdown:                 # only if high_climate_impact_sector is true (E1 para 27)
  coal: 0
  oil: 0
  natural_gas: 0
  other_fossil: 0
  purchased_fossil: 0
production:                       # E1 para 28
  renewable: 0
  non_renewable: 0
```

## inputs/claims.yaml (optional)

Public climate claims the client already makes or wants to make, so the reviewer can test them.

```yaml
- text: ""
  where: ""                       # website, product label, report
  evidence: ""                    # file in inputs/ that supports it
```
