// Map file specifications
const vg_coastal = "js/Coastal_campsites.vg.json";
const vg_city_proximity = "js/city_proximity_map.vg.json";
const vg_facilities = "js/facilities_map.vg.json";
const vg_flow_map = "js/flow_map.vg.json";
const vg_seasonal_migration = "js/seasonal_migration_map.vg.json";

// Chart specifications
const vg_climate = "js/climate_and_camp.vg.json";
const vg_butterfly = "js/butterfly_chart.vg.json";
const vg_lollipop = "js/lollipop_chart.vg.json";
const vg_pyramid = "js/population_pyramid.vg.json";
const vg_sankey = "js/sankey_accommodation.vg.json";
const vg_solo_family = "js/solo_vs_family_accommodation.vg.json";

// Embedding all specifications into their respective HTML containers
vegaEmbed("#vis-coastal", vg_coastal).catch(console.error);
vegaEmbed("#vis-city-proximity", vg_city_proximity).catch(console.error);
vegaEmbed("#vis-facilities", vg_facilities).catch(console.error);
vegaEmbed("#vis-flow-map", vg_flow_map).catch(console.error);
vegaEmbed("#vis-seasonal-migration", vg_seasonal_migration).catch(console.error);

vegaEmbed("#vis-climate", vg_climate).catch(console.error);
vegaEmbed("#vis-butterfly", vg_butterfly).catch(console.error);
vegaEmbed("#vis-lollipop", vg_lollipop).catch(console.error);
vegaEmbed("#vis-pyramid", vg_pyramid).catch(console.error);
vegaEmbed("#vis-sankey", vg_sankey).catch(console.error);
vegaEmbed("#vis-solo-family", vg_solo_family).catch(console.error);