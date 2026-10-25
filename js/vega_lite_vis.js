// =============================================================
// FILE SPECIFICATIONS
// =============================================================
const vg_scrolly              = "js/scrolly_map.vg.json";
const vg_seasonal_migration   = "js/seasonal_migration_map.vg.json";
const vg_facilities           = "js/facilities_map.vg.json";
const vg_flow_map             = "js/flow_map.vg.json";
const vg_climate              = "js/climate_and_camp.vg.json";
const vg_butterfly            = "js/butterfly_chart.vg.json";
const vg_lollipop             = "js/lollipop_chart.vg.json";
const vg_pyramid              = "js/population_pyramid.vg.json";
const vg_sankey               = "js/sankey_accommodation.vg.json";
const vg_solo_family          = "js/solo_vs_family_accommodation.vg.json";
const vg_occupation           = "js/vis_occupancy_multiline.vg.json"
const vg_activities         = "js/vis_camp_activities.vg.json"
const vg_dumbbell = "js/vis_dumbbell_amenities.vg.json";


const embedOpt = { actions: false };

// =============================================================
// 1. SCROLLYTELLING SECTION 1: WHERE DO AUSTRALIANS CAMP?
// =============================================================
let coastalView = null;
let currentStep = 1;

vegaEmbed("#vis-coastal", vg_scrolly, embedOpt)
  .then((res) => {
    coastalView = res.view;
  })
  .catch(console.error);

const stepObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      document.querySelectorAll(".step").forEach((el) => el.classList.remove("is-active"));
      entry.target.classList.add("is-active");

      const stepNum = Number(entry.target.getAttribute("data-step"));
      if (stepNum && stepNum !== currentStep && coastalView) {
        currentStep = stepNum;
        coastalView.signal("story_step", stepNum).runAsync().catch(console.error);
      }
    }
  });
}, { root: null, rootMargin: "-40% 0px -40% 0px", threshold: 0.1 });

// =============================================================
// 2. SCROLLYTELLING SECTION 2: SEASONAL MIGRATION MAP
// =============================================================
let seasonalView = null;
let currentSeason = "Summer";

vegaEmbed("#vis-seasonal-migration", vg_seasonal_migration, embedOpt)
  .then((res) => {
    seasonalView = res.view;
  })
  .catch(console.error);

const seasonObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      // Highlight current card
      document.querySelectorAll(".step-season").forEach((el) => el.classList.remove("is-active"));
      entry.target.classList.add("is-active");

      // Read season name (Summer, Autumn, Winter, Spring)
      const seasonName = entry.target.getAttribute("data-season");

      if (seasonName && seasonName !== currentSeason && seasonalView) {
        currentSeason = seasonName;
        // Dynamically updates the dots and sizes without reloading the map!
        seasonalView.signal("season_filter", seasonName).runAsync().catch(console.error);
      }
    }
  });
}, { root: null, rootMargin: "-40% 0px -40% 0px", threshold: 0.1 });

// Attach both observers once the DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".step").forEach((el) => stepObserver.observe(el));
  document.querySelectorAll(".step-season").forEach((el) => seasonObserver.observe(el));
});

// =============================================================
// 3. REMAINING DASHBOARD VISUALISATIONS
// =============================================================
vegaEmbed("#vis-facilities", vg_facilities, embedOpt).catch(console.error);
vegaEmbed("#vis-flow-map", vg_flow_map, embedOpt).catch(console.error);
vegaEmbed("#vis-climate", vg_climate, embedOpt).catch(console.error);
vegaEmbed("#vis-butterfly", vg_butterfly, embedOpt).catch(console.error);
vegaEmbed("#vis-lollipop", vg_lollipop, embedOpt).catch(console.error);
vegaEmbed("#vis-pyramid", vg_pyramid, embedOpt).catch(console.error);
vegaEmbed("#vis-sankey", vg_sankey, embedOpt).catch(console.error);
vegaEmbed("#vis-solo-family", vg_solo_family, embedOpt).catch(console.error);
vegaEmbed("#vis-occupation", vg_occupation, embedOpt).catch(console.error);
vegaEmbed("#vis-activities", vg_activities, embedOpt).catch(console.error);


vegaEmbed("#vis-dumbbell", vg_dumbbell, { actions: false })
  .catch(console.error);