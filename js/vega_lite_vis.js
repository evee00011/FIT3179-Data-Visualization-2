// Map file specifications
const vg_scrolly = "js/scrolly_map.vg.json"; // Pointed to your scrollytelling map specification
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

// Embed options (disables the '...' export/source action menu)
const embedOpt = { actions: false };

// --- 1. Scrollytelling Setup for the Map ---
let coastalView = null;
let currentStep = 1;

vegaEmbed("#vis-coastal", vg_scrolly, embedOpt)
  .then((result) => {
    coastalView = result.view; // Holds active Vega view reference for scrollytelling
  })
  .catch(console.error);

// Observer to track text card steps entering the viewport
const stepObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Highlight current card
        document.querySelectorAll(".step").forEach((el) => el.classList.remove("is-active"));
        entry.target.classList.add("is-active");

        // Read step index (1, 2, etc.)
        const stepNum = Number(entry.target.getAttribute("data-step"));

        if (stepNum && stepNum !== currentStep && coastalView) {
          currentStep = stepNum;
          // Dynamically updates points on the map without redrawing the basemap
          coastalView.signal("story_step", stepNum).runAsync().catch(console.error);
        }
      }
    });
  },
  {
    root: null,
    rootMargin: "-40% 0px -40% 0px", // Fires as card crosses the middle horizontal band of screen
    threshold: 0.1
  }
);

// Attach observer once DOM has loaded
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".step").forEach((stepEl) => {
    stepObserver.observe(stepEl);
  });
});

// --- 2. Embedding all remaining specifications ---
vegaEmbed("#vis-facilities", vg_facilities, embedOpt).catch(console.error);
vegaEmbed("#vis-flow-map", vg_flow_map, embedOpt).catch(console.error);
vegaEmbed("#vis-seasonal-migration", vg_seasonal_migration, embedOpt).catch(console.error);

vegaEmbed("#vis-climate", vg_climate, embedOpt).catch(console.error);
vegaEmbed("#vis-butterfly", vg_butterfly, embedOpt).catch(console.error);
vegaEmbed("#vis-lollipop", vg_lollipop, embedOpt).catch(console.error);
vegaEmbed("#vis-pyramid", vg_pyramid, embedOpt).catch(console.error);
vegaEmbed("#vis-sankey", vg_sankey, embedOpt).catch(console.error);
vegaEmbed("#vis-solo-family", vg_solo_family, embedOpt).catch(console.error);