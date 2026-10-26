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
const vg_activities         = "js/vis_camp_activities.vg.json";
const vg_lollipop           = "js/lollipop_chart.vg.json";
const vg_dumbbell           = "js/vis_dumbbell_amenities.vg.json";
const vg_upset              = "js/vis_upset_amenities.vg.json";
const vg_radar              = "js/vis_radar_dna.vg.json";

const embedOpt = { actions: false };

// =============================================================
// 1. SCROLLYTELLING SECTION 1: WHERE DO AUSTRALIANS CAMP? (UNCHANGED)
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
}, { root: null, rootMargin: "-35% 0px -35% 0px", threshold: 0.1 });

// =============================================================
// 2. SCROLLYTELLING SECTION 2: SEASONAL MIGRATION MAP (UNCHANGED)
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
      document.querySelectorAll(".step-season").forEach((el) => el.classList.remove("is-active"));
      entry.target.classList.add("is-active");

      const seasonName = entry.target.getAttribute("data-season");
      if (seasonName && seasonName !== currentSeason && seasonalView) {
        currentSeason = seasonName;
        seasonalView.signal("season_filter", seasonName).runAsync().catch(console.error);
      }
    }
  });
}, { root: null, rootMargin: "-35% 0px -35% 0px", threshold: 0.1 });

// =============================================================
// 3. REMAINING DASHBOARD VISUALISATIONS
// =============================================================
vegaEmbed("#vis-climate-heatmap", vg_climate_heatmap, embedOpt).catch(console.error);
vegaEmbed("#vis-occupation", vg_occupation, embedOpt).catch(console.error);
vegaEmbed("#vis-pyramid", vg_pyramid, embedOpt).catch(console.error);
vegaEmbed("#vis-flow-map", vg_flow_map, embedOpt).catch(console.error);
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
  // 1. Observe the original two scrollytelling sections
  document.querySelectorAll(".step").forEach((el) => stepObserver.observe(el));
  document.querySelectorAll(".step-season").forEach((el) => seasonObserver.observe(el));

  // 2. Select only the standalone charts (excluding the first 2 scrolly charts)
  const allSideLayouts = Array.from(document.querySelectorAll(".vis-side-layout"));
  // First section is index 0, seasonal scrolly is the one with class .season-scrolly-layout
  const standaloneCharts = allSideLayouts.filter(
    (el, idx) => idx !== 0 && !el.classList.contains("season-scrolly-layout")
  );

  // Add the class so CSS applies the isolated viewport focus to them
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
    {
      root: null,
      rootMargin: "-20% 0px -20% 0px", // Illuminates as soon as it enters comfortable viewing range
      threshold: 0.15
    }
  );

  standaloneCharts.forEach((section) => chartFocusObserver.observe(section));

  // Ensure whichever is first visible is activated immediately
  if (standaloneCharts.length > 0) {
    standaloneCharts[0].classList.add("is-focused-chart");
  }
});