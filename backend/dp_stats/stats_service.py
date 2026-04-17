from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from .budget_manager import BudgetManager
from .cache_service import DPResultCache
from .mechanisms import DPParams, privatize_count, privatize_counts_dict, mask_low_freq

# 已知分类，确保即使真实值为 0 也能加噪
KNOWN_TYPES = {'FALLEN', 'STILLNESS', 'NIGHT_ABNORMAL'}
KNOWN_RISKS = {'HIGH', 'MEDIUM', 'LOW'}
KNOWN_STATUSES = {'pending', 'confirmed', 'false_alarm'}


def _ensure_categories(stats: Dict[str, Any]) -> Dict[str, Any]:
    """补全所有已知分类（值为 0），保证每个维度都能被加噪"""
    filled = dict(stats)
    for t in KNOWN_TYPES:
        filled.setdefault('by_type', {}).setdefault(t, 0)
    for r in KNOWN_RISKS:
        filled.setdefault('by_risk', {}).setdefault(r, 0)
    for s in KNOWN_STATUSES:
        filled.setdefault('by_status', {}).setdefault(s, 0)
    return filled


def _scale_to_total(real_counts: dict[str, int], target_total: int) -> dict[str, int]:
    """按真实比例缩放到 target_total，保证各维度求和一致"""
    if target_total == 0 or not real_counts:
        return {k: 0 for k in real_counts}
    real_total = sum(real_counts.values())
    if real_total == 0:
        # 无真实数据时均匀分配
        n = len(real_counts)
        base = target_total // n
        remainder = target_total % n
        return {k: base + (1 if i < remainder else 0) for i, k in enumerate(real_counts)}
    # 按真实比例缩放
    scaled = {k: max(0, round(v * target_total / real_total)) for k, v in real_counts.items()}
    diff = target_total - sum(scaled.values())
    if diff != 0:
        max_key = max(scaled, key=scaled.get)
        scaled[max_key] = max(0, scaled[max_key] + diff)
    return scaled


@dataclass
class StatsService:
    budget_manager: BudgetManager
    cache: DPResultCache

    def get_private_stats(
        self,
        user_id: str,
        query_key: str,
        stats: Dict[str, Any],
        epsilon: float,
        now: datetime,
        check_budget: bool = True,
    ) -> dict:
        """
        对整个统计对象一次性加噪

        Args:
            user_id: 用户 ID
            query_key: 查询键
            stats: 包含 total, by_type, by_risk, by_status 的统计对象
            epsilon: 隐私预算（单次消耗）
            now: 当前时间
            check_budget: 是否检查预算限制（生产环境 True，开发环境 False）

        Returns:
            {"value": 加噪后的 stats, "display": 低频隐藏展示值, "source": "cache" 或 "fresh_dp"}
        """
        # 检查缓存
        cached = self.cache.get(user_id, "stats", query_key, now)
        if cached is not None:
            display = {
                'total': mask_low_freq(cached['total']),
                'by_type': {k: mask_low_freq(v) for k, v in cached['by_type'].items()},
                'by_risk': {k: mask_low_freq(v) for k, v in cached['by_risk'].items()},
                'by_status': {k: mask_low_freq(v) for k, v in cached['by_status'].items()},
            }
            return {"value": cached, "display": display, "source": "cache"}

        # 检查预算（仅生产环境）
        if check_budget:
            today = now.date()
            if not self.budget_manager.can_spend(user_id, epsilon, today):
                raise ValueError("Privacy budget exceeded")

        # 补全所有已知分类后再加噪
        filled = _ensure_categories(stats)
        params = DPParams(epsilon=epsilon, sensitivity=1.0)

        noisy_stats = {}
        noisy_stats['by_type'] = privatize_counts_dict(filled.get('by_type', {}), params)

        # total 由 by_type 加噪值求和，保证总量与主分类一致
        noisy_stats['total'] = sum(noisy_stats['by_type'].values())

        # by_risk 和 by_status 按真实比例缩放至 total，保证各维度一致
        noisy_stats['by_risk'] = _scale_to_total(filled.get('by_risk', {}), noisy_stats['total'])
        noisy_stats['by_status'] = _scale_to_total(filled.get('by_status', {}), noisy_stats['total'])

        # 消耗预算（仅生产环境）
        if check_budget:
            today = now.date()
            self.budget_manager.spend(user_id, epsilon, today)

        self.cache.set(user_id, "stats", query_key, noisy_stats, now)

        # 生成低频隐藏后的展示值
        display_stats = {
            'total': mask_low_freq(noisy_stats['total']),
            'by_type': {k: mask_low_freq(v) for k, v in noisy_stats['by_type'].items()},
            'by_risk': {k: mask_low_freq(v) for k, v in noisy_stats['by_risk'].items()},
            'by_status': {k: mask_low_freq(v) for k, v in noisy_stats['by_status'].items()},
        }

        return {"value": noisy_stats, "display": display_stats, "source": "fresh_dp"}

    def get_private_daily_trend(
        self,
        user_id: str,
        query_key: str,
        daily_data: dict[str, dict[str, int]],
        epsilon: float,
        now: datetime,
        check_budget: bool = True,
    ) -> dict:
        """为每日趋势加噪"""
        cached = self.cache.get(user_id, "trend", query_key, now)
        if cached is not None:
            return {"value": cached, "source": "cache"}

        if check_budget:
            today = now.date()
            if not self.budget_manager.can_spend(user_id, epsilon, today):
                raise ValueError("Privacy budget exceeded")

        params = DPParams(epsilon=epsilon, sensitivity=1.0)
        noisy_daily = {}

        for date_key, type_counts in daily_data.items():
            filled_counts = {t: type_counts.get(t, 0) for t in KNOWN_TYPES}
            noisy_daily[date_key] = privatize_counts_dict(filled_counts, params)

        if check_budget:
            today = now.date()
            self.budget_manager.spend(user_id, epsilon, today)

        self.cache.set(user_id, "trend", query_key, noisy_daily, now)

        return {"value": noisy_daily, "source": "fresh_dp"}
