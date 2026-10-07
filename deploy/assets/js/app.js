/* OutfitWindow 共享运行库：导航激活、会话状态、执行日志 */
"use strict";

const APP = {
  KEYS: { item: "ow_item", req: "ow_requirements", plans: "ow_plans", confirmed: "ow_confirmed_plan", logs: "ow_logs", locked: "ow_locked" },

  initNav(page) {
    document.querySelectorAll(".nav .links a").forEach((a) => {
      if (a.dataset.page === page) a.classList.add("active");
    });
  },

  log(event_type, operation) {
    try {
      const logs = JSON.parse(localStorage.getItem(this.KEYS.logs) || "[]");
      logs.push({
        ts: new Date().toISOString(),
        event_type,
        operation: operation || {},
      });
      localStorage.setItem(this.KEYS.logs, JSON.stringify(logs.slice(-200)));
    } catch (e) { /* ignore */ }
  },

  save(key, val) { localStorage.setItem(key, JSON.stringify(val)); this.log("state_saved", { key }); },
  load(key, fallback = null) {
    try {
      const v = localStorage.getItem(key);
      return v ? JSON.parse(v) : fallback;
    } catch (e) { return fallback; }
  },
  clear(key) { localStorage.removeItem(key); },

  yuan(fen) { return (fen / 100).toFixed(2); },

  // 全景流程入口：从已保存的衣物+需求生成方案并保存
  generatePlansFromState() {
    const item = this.load(this.KEYS.item);
    const req = this.load(this.KEYS.req);
    if (!item || !req) {
      APP.log("generate_failed", { reason: "missing item or requirements" });
      return { ok: false, message: "缺少衣物或需求数据，请先完成录入。" };
    }
    const result = EN.planOutfits({
      anchor: item,
      closetItems: item.closet_mates || [],
      products: DEMO_DATA.products,
      variants: DEMO_DATA.variants,
      req,
    });
    result.plans.forEach((p) => EN.validatePlan(p, req));
    this.save(this.KEYS.plans, { generated_at: new Date().toISOString(), result: { plan_count: result.plan_count, roles_missing: result.roles_missing, eligible_variant_count: result.eligible_variant_count } });
    APP.log("plans_generated", { plan_count: result.plan_count });
    return { ok: result.plan_count > 0, result };
  },

  // 演示锚点衣物（与 Python 测试的 C001 对齐）
  demoAnchor() {
    return {
      item_id: "C001",
      user_id: "u-demo",
      category: "上衣",
      primary_color: "白色",
      pattern: "纯色",
      silhouette: "宽松",
      season_tags: ["春", "夏"],
      style_tags: ["休闲"],
      user_confirmed: true,
      available_status: "available",
      source: "demo",
      image_ref: "",
      closet_mates: [
        { item_id: "C002", category: "下装", primary_color: "深蓝", pattern: "纯色", silhouette: "直筒", season_tags: ["春", "秋"], style_tags: ["休闲"], available_status: "available", image_ref: "" },
        { item_id: "C003", category: "鞋类", primary_color: "白", silhouette: "", season_tags: ["春", "夏", "秋"], style_tags: ["休闲"], available_status: "available", image_ref: "" },
      ],
    };
  },

  demoRequirements() {
    return {
      occasion: "上课与日常通勤",
      temperature_text: "15-20度，秋季",
      budget_fen: 50000,
      size_requirements: { 上衣: "M", 下装: "L", 鞋类: "40" },
      hard: {
        exclude_colors: [],
        exclude_silhouettes: [],
        exclude_categories: [],
        max_budget_fen: 50000,
        locked_items: [],
      },
      soft_preferences: { styles: ["休闲"] },
    };
  },
};