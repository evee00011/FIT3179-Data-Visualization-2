// =============================================================
// FILE SPECIFICATIONS
// =============================================================
const vg_scrolly            = "js/scrolly_map.vg.json";
const vg_seasonal_migration = "js/seasonal_migration_map.vg.json";
const vg_climate_heatmap    = "js/vis_climate_occupancy_heatmap.vg.json";
const vg_occupation         = "js/vis_occupancy_multiline.vg.json";
const vg_pyramid            = "js/population_pyramid.vg.json";
const vg_flow_map           = "js/flow_map.vg.json";
const vg_sankey             = "js/sankey_accommodation.vg.json";
const vg_ridgeline          = "js/vis_ridgeline_duration.vg.json";
const vg_activities = "js/vis_camp_activities.vg.json";
vegaEmbed("#vis-activities", vg_activities, { actions: false }).catch(console.error);
const vg_lollipop           = "js/lollipop_chart.vg.json";
const vg_dumbbell           = "js/vis_dumbbell_amenities.vg.json";
const vg_upset              = "js/vis_upset_amenities.vg.json";
const vg_radar              = "js/vis_radar_dna.vg.json";

const embedOpt = { actions: false };

// =============================================================
// 1. SCROLLYTELLING SECTION 1: WHERE DO AUSTRALIANS CAMP?
// =============================================================
let coastalView = null;
let currentStep = 1;

vegaEmbed("#vis-coastal", vg_scrolly, embedOpt)
  .then((res) => {
    coastalView = res.view;
    // Explicitly guarantee map starts on Step 1 (pure coastal dots, no city halos)
    coastalView.signal("story_step", 1).runAsync().catch(console.error);
  })
  .catch(console.error);

const stepObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        document.querySelectorAll(".step").forEach((el) => el.classList.remove("is-active"));
        entry.target.classList.add("is-active");

        const stepNum = Number(entry.target.getAttribute("data-step"));
        if (stepNum && stepNum !== currentStep && coastalView) {
          currentStep = stepNum;
          // Smoothly toggle layers: 1 = coastal dots, 2 = city halos & leader lines
          coastalView.signal("story_step", stepNum).runAsync().catch(console.error);
        }
      }
    });
  },
  { root: null, rootMargin: "-30% 0px -30% 0px", threshold: 0.15 }
);

// =============================================================
// 2. SCROLLYTELLING SECTION 2: SEASONAL MIGRATION MAP
// =============================================================
let seasonalView = null;
let currentSeason = "Summer";

vegaEmbed("#vis-seasonal-migration", vg_seasonal_migration, embedOpt)
  .then((res) => {
    seasonalView = res.view;
    seasonalView.signal("season_filter", "Summer").runAsync().catch(console.error);
  })
  .catch(console.error);

const seasonObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        document.querySelectorAll(".step-season").forEach((el) => el.classList.remove("is-active"));
        entry.target.classList.add("is-active");

        const seasonName = entry.target.getAttribute("data-season");
        if (seasonName && seasonName !== currentSeason && seasonalView) {
          currentSeason = seasonName;
          seasonalView.signal("season_filter", seasonName).runAsync().catch(console.error);
        }
      }
    });
  },
  { root: null, rootMargin: "-30% 0px -30% 0px", threshold: 0.15 }
);

// =============================================================
// 3. REMAINING DASHBOARD VISUALISATIONS
// =============================================================
vegaEmbed("#vis-climate-heatmap", vg_climate_heatmap, embedOpt).catch(console.error);
vegaEmbed("#vis-occupation", vg_occupation, embedOpt).catch(console.error);
vegaEmbed("#vis-pyramid", vg_pyramid, embedOpt).catch(console.error);
vegaEmbed("#vis-flow-map", vg_flow_map, { actions: false, renderer: "svg" })
  .catch(console.error);
  vegaEmbed("#vis-sankey", vg_sankey, embedOpt).catch(console.error);
vegaEmbed("#vis-ridgeline", vg_ridgeline, embedOpt).catch(console.error);
vegaEmbed("#vis-activities", vg_activities, embedOpt).catch(console.error);
vegaEmbed("#vis-lollipop", vg_lollipop, embedOpt).catch(console.error);
vegaEmbed("#vis-dumbbell", vg_dumbbell, embedOpt).catch(console.error);
vegaEmbed("#vis-upset", vg_upset, embedOpt).catch(console.error);
vegaEmbed("#vis-radar", vg_radar, embedOpt).catch(console.error);

// =============================================================
// 4. ATTACH OBSERVERS & SCROLL FOCUS FOR REMAINING CHARTS
// =============================================================
document.addEventListener("DOMContentLoaded", () => {
  // Attach scrollytelling observers
  document.querySelectorAll(".step").forEach((el) => stepObserver.observe(el));
  document.querySelectorAll(".step-season").forEach((el) => seasonObserver.observe(el));

  // Focus observer for the remaining standalone charts
  const allSideLayouts = Array.from(document.querySelectorAll(".vis-side-layout"));
  const standaloneCharts = allSideLayouts.filter(
    (el) => !el.classList.contains("coastal-scrolly-layout") && !el.classList.contains("season-scrolly-layout")
  );

  standaloneCharts.forEach((el) => el.classList.add("standalone-chart-section"));

  const chartFocusObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          standaloneCharts.forEach((sec) => sec.classList.remove("is-focused-chart"));
          entry.target.classList.add("is-focused-chart");
        }
      });
    },
    { root: null, rootMargin: "-15% 0px -15% 0px", threshold: 0.15 }
  );

  standaloneCharts.forEach((section) => chartFocusObserver.observe(section));

  if (standaloneCharts.length > 0) {
    standaloneCharts[0].classList.add("is-focused-chart");
  }
});