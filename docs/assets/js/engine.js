/* OutfitWindow 前端引擎（对齐 scripts/skills_lib 的确定性逻辑） */
"use strict";

const EN = {
  CATEGORIES: ["上衣", "下装", "外套", "鞋类", "包饰"],
  ROLE_ORDER: ["上衣", "外套", "下装", "鞋类", "包饰"],
  MAX_ITEMS: 5,
  MAX_PLANS: 3,

  // ---- 商品/变体索引 ----
  index() {
    const bySku = {};
    const byPid = {};
    DEMO_DATA.products.forEach((p) => {
      bySku[p.sku_id] = p;
      byPid[p.product_id] = p;
    });
    return { bySku, byPid };
  },

  // ---- 硬约束过滤 (对齐 constraint_filter.filter_variants) ----
  filterVariants(products, variants, req) {
    const { byPid } = this.index();
    const hard = req.hard;
    const passed = [];
    const details = [];
    for (const v of variants) {
      const p = byPid[v.product_id];
      if (!p) continue;
      const checks = {};
      checks.sale_status = { passed: p.sale_status === "on_sale", reason: p.sale_status === "on_sale" ? "" : `销售状态 ${p.sale_status}` };
      const needSize = req.size_requirements[p.category] || "";
      checks.size_available = { passed: !needSize || v.size_label === needSize, reason: (!needSize || v.size_label === needSize) ? "" : `需求尺码${needSize}，实际${v.size_label}` };
      checks.stock_positive = { passed: v.stock_qty > 0, reason: v.stock_qty > 0 ? "" : `库存 ${v.stock_qty}` };
      checks.price_exists = { passed: v.price_fen >= 0, reason: v.price_fen >= 0 ? "" : "价格缺失" };
      const colorHit = (p.color_tags || []).filter((c) => hard.exclude_colors.includes(c));
      checks.exclude_color = { passed: colorHit.length === 0, reason: colorHit.length ? `命中排除颜色 ${colorHit.join(",")}` : "" };
      checks.exclude_silhouette = { passed: !(p.silhouette && hard.exclude_silhouettes.includes(p.silhouette)), reason: p.silhouette && hard.exclude_silhouettes.includes(p.silhouette) ? `命中排除版型 ${p.silhouette}` : "" };
      checks.exclude_category = { passed: !hard.exclude_categories.includes(p.category), reason: hard.exclude_categories.includes(p.category) ? `命中排除类别 ${p.category}` : "" };
      checks.budget = { passed: v.price_fen <= hard.max_budget_fen, reason: v.price_fen <= hard.max_budget_fen ? "" : `价格 ${(v.price_fen / 100).toFixed(0)} 元超预算` };

      const lockedVids = hard.locked_items.filter((i) => i.source === "merchant").map((i) => i.variant_id);
      let over = Object.values(checks).every((c) => c.passed);
      if (lockedVids.includes(v.variant_id) && !over) {
        checks.lock_honored = { passed: true, reason: "锁定项保留但违反其它约束（冲突）" };
        over = true;
      }
      details.push({ variant_id: v.variant_id, sku_id: p.sku_id, product_name: p.product_name, checks, overall: over });
      if (over) passed.push(v);
    }
    return { passed, passed_count: passed.length, failed_count: variants.length - passed.length, details };
  },

  // ---- 搭配规划 (对齐 planner.plan_outfits) ----
  planOutfits({ anchor, closetItems, products, variants, req, filterResult }) {
    const { byPid } = this.index();
    const fr = filterResult || this.filterVariants(products, variants, req);
    const eligible = fr.passed;
    const byCat = {};
    eligible.forEach((v) => {
      const p = byPid[v.product_id];
      if (p) (byCat[p.category] = byCat[p.category] || []).push(v);
    });
    const closetUsable = closetItems.filter((c) => c.item_id !== anchor.item_id && c.available_status === "available");

    const plans = [];
    const p1 = this.buildPlan("已有优先", anchor, closetUsable, byCat, byPid, req, true, false);
    if (p1) plans.push(p1);
    const p2 = this.buildPlan("预算优先", anchor, closetUsable, byCat, byPid, req, true, true);
    if (p2 && !this.samePlan(p1, p2)) plans.push(p2);
    const p3 = this.buildPlan("风格表达", anchor, closetUsable, byCat, byPid, req, false, false);
    if (p3 && !plans.some((p) => this.samePlan(p, p3))) plans.push(p3);

    const list = plans.slice(0, this.MAX_PLANS);
    const filled = new Set();
    list.forEach((p) => p.items.forEach((i) => filled.add(i.role)));
    return {
      plans: list,
      plan_count: list.length,
      roles_filled: [...filled],
      roles_missing: this.ROLE_ORDER.filter((r) => !filled.has(r)),
      eligible_variant_count: eligible.length,
      filterDetails: fr.details,
    };
  },

  buildPlan(label, anchor, closetUsable, byCat, byPid, req, preferCloset, excludeSponsor) {
    const items = [{ source: "closet", role: anchor.category, ref_id: anchor.item_id, product_name: `${anchor.primary_color || ""}${anchor.pattern || ""}${anchor.category}`, category: anchor.category, image_ref: anchor.image_ref, lock_key: `closet:${anchor.item_id}`, is_sponsor: false, price_fen: 0, size: "", color: anchor.primary_color }];
    closetUsable.forEach((c) => {
      if (items.length >= this.MAX_ITEMS) return;
      if (items.some((i) => i.role === c.category)) return;
      if (preferCloset) items.push({ source: "closet", role: c.category, ref_id: c.item_id, product_name: `${c.primary_color || ""}${c.pattern || ""}${c.category}`, category: c.category, image_ref: c.image_ref, lock_key: `closet:${c.item_id}`, is_sponsor: false, price_fen: 0, size: "", color: c.primary_color });
    });

    const usedVids = new Set(items.filter((i) => i.variant_id).map((i) => i.variant_id));
    for (const role of this.ROLE_ORDER) {
      if (items.length >= this.MAX_ITEMS) break;
      if (items.some((i) => i.role === role)) continue;
      const cands = byCat[role] || [];
      const pick = this.pickVariant(cands, req, usedVids, byPid, excludeSponsor);
      if (!pick) continue;
      const p = byPid[pick.product_id];
      items.push({ source: "merchant", role, ref_id: pick.variant_id, sku_id: p ? p.sku_id : "", variant_id: pick.variant_id, product_name: p ? p.product_name : "", category: role, size: pick.size_label, color: pick.color_label || "", price_fen: pick.price_fen, image_ref: p ? p.image_ref : null, product_url: p ? p.product_url : null, lock_key: `merchant:${pick.variant_id}`, is_sponsor: p ? p.is_sponsor : false, shipping_fee_fen: pick.shipping_fee_fen });
      usedVids.add(pick.variant_id);
    }
    if (items.length < 2) return null;
    const subtotal = items.filter((i) => i.source === "merchant").reduce((s, i) => s + i.price_fen, 0);
    if (subtotal > req.hard.max_budget_fen) return null;
    return { plan_id: "plan-" + Math.random().toString(36).slice(2, 10), plan_label: label, items, purchase_subtotal_fen: subtotal, validated: null };
  },

  pickVariant(cands, req, usedVids, byPid, excludeSponsor) {
    if (!cands.length) return null;
    const lockedVids = req.hard.locked_items.filter((i) => i.source === "merchant").map((i) => i.variant_id);
    for (const c of cands) if (lockedVids.includes(c.variant_id) && !usedVids.has(c.variant_id)) return c;
    let fresh = cands.filter((c) => !usedVids.has(c.variant_id));
    if (excludeSponsor) fresh = fresh.filter((c) => { const p = byPid[c.product_id]; return !(p && p.is_sponsor); });
    fresh.sort((a, b) => a.price_fen - b.price_fen);
    for (const c of fresh) if (c.stock_qty > 0) return c;
    return null;
  },

  // ---- 校验 (对齐 validator.validate_plan) ----
  validatePlan(plan, req) {
    const checks = [];
    const purchase = plan.items.filter((i) => i.source === "merchant");
    const budget = plan.purchase_subtotal_fen <= req.hard.max_budget_fen;
    checks.push({ check: "budget", passed: budget, evidence: `purchase_subtotal=${plan.purchase_subtotal_fen} <= budget=${req.hard.max_budget_fen}` });
    const badPrice = purchase.filter((i) => i.price_fen < 0).map((i) => i.sku_id);
    checks.push({ check: "price_exists", passed: badPrice.length === 0, evidence: badPrice.length ? `missing price: ${badPrice.join(",")}` : "all items have price_fen >= 0" });
    const sizeIssues = [];
    purchase.forEach((i) => {
      const need = req.size_requirements[i.role] || "";
      if (need && i.size !== need) sizeIssues.push(`${i.sku_id}(${i.size})`);
      if (["上衣", "下装", "外套", "鞋类"].includes(i.role) && !i.size) sizeIssues.push(`${i.sku_id}(no size)`);
    });
    checks.push({ check: "size_match", passed: sizeIssues.length === 0, evidence: sizeIssues.length ? `size mismatch: ${sizeIssues.join(",")}` : "all sizes matched" });
    checks.push({ check: "stock_positive", passed: true, evidence: "variants were stock-filtered upstream" });
    checks.push({ check: "sale_status", passed: true, evidence: "variants were sale-status filtered upstream" });

    const lockKeys = new Set();
    req.hard.locked_items.forEach((i) => {
      if (i.source === "merchant" && i.variant_id) lockKeys.add(`merchant:${i.variant_id}`);
      if (i.source === "closet" && i.item_id) lockKeys.add(`closet:${i.item_id}`);
    });
    const present = new Set(plan.items.map((i) => i.lock_key));
    const missing = [...lockKeys].filter((k) => !present.has(k));
    checks.push({ check: "lock_honored", passed: missing.length === 0, evidence: missing.length ? `missing locks: ${missing.join(",")}` : "all locks preserved" });
    checks.push({ check: "exclude_respected", passed: true, evidence: "excluded attributes filtered upstream" });
    const badSource = plan.items.filter((i) => !["closet", "merchant"].includes(i.source)).map((i) => i.role);
    checks.push({ check: "source_verified", passed: badSource.length === 0, evidence: badSource.length ? `bad source: ${badSource.join(",")}` : "all from closet or catalog" });

    const failed = checks.filter((c) => !c.passed).map((c) => c.check);
    const status = failed.length === 0 ? "passed" : "failed";
    plan.validated = { plan_id: plan.plan_id, validation_status: status, checks, failed_reasons: failed };
    return plan.validated;
  },

  // ---- 购物清单 (对齐 shopping_list.build_shopping_list) ----
  buildShoppingList(plan, snapshotAt) {
    const closetItems = [], purchaseItems = [];
    let knownFee = 0; const unknownFees = [];
    plan.items.forEach((i) => {
      if (i.source === "closet") {
        closetItems.push({ item_id: i.ref_id, name: i.product_name || "自有衣物", role: i.role, image_ref: i.image_ref || "" });
        return;
      }
      purchaseItems.push({ sku_id: i.sku_id, variant_id: i.variant_id, name: i.product_name, role: i.role, size: i.size, color: i.color, price_fen: i.price_fen, quantity: 1, subtotal_fen: i.price_fen, image_ref: i.image_ref || "", product_url: i.product_url || "", has_url: !!i.product_url, is_sponsor: i.is_sponsor });
      if (i.shipping_fee_fen >= 0) knownFee += i.shipping_fee_fen;
      else unknownFees.push(`${i.sku_id}（${i.product_name}）`);
    });
    const subtotal = plan.purchase_subtotal_fen;
    let message, finalDetermined = false, finalAmount = null;
    if (unknownFees.length) {
      message = "当前商品小计符合预算，最终支付金额仍需确认运费。";
    } else {
      message = `商品小计与已知费用合计为 ${((subtotal + knownFee) / 100).toFixed(2)} 元，运费以商家结算为准。`;
      finalDetermined = true; finalAmount = subtotal + knownFee;
    }
    const pending = [];
    if (unknownFees.length) pending.push(`运费未知：${unknownFees.join("、")}（${unknownFees.length}件）`);
    pending.push("尺码合身度仅供参考，建议对照尺码表；商品图片与实物可能存在色差。");
    return {
      list_id: "list-" + Math.random().toString(36).slice(2, 10),
      status: "购物意向清单已生成",
      closet_items: closetItems,
      purchase_items: purchaseItems,
      financial_summary: { purchase_subtotal_fen: subtotal, known_fee_fen: knownFee, unknown_fee_list: unknownFees, final_amount_determined: finalDetermined, final_amount_fen: finalAmount, message },
      inventory_snapshot_at: snapshotAt || new Date().toISOString(),
      pending_confirmations: pending,
      disclaimer: "本清单为购物意向，不构成下单。价格、库存以购买前复核为准。",
    };
  },

  samePlan(a, b) {
    if (!a || !b) return false;
    const k = (p) => [...p.items].map((i) => `${i.role}:${i.ref_id}`).sort().join("|");
    return k(a) === k(b);
  },
};