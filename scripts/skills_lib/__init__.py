"""skills_lib：OutfitWindow 核心逻辑包。"""

from .models import (
    Product,
    Variant,
    ClosetItem,
    Requirements,
    HardConstraints,
    Plan,
    PlanItem,
    CATEGORIES,
    SCENES,
    DEFAULT_BUDGET_FEN,
)
from .catalog_normalizer import load_catalog
from .constraint_filter import filter_variants
from .planner import plan_outfits
from .validator import validate_plan, validate_all
from .replanner import parse_operation, apply_operation
from .shopping_list import build_shopping_list
from .board_builder import build_board
from .privacy_audit import audit_image
from .garment_card import build_garment_card
from .requirement_parser import parse_requirement, parse_natural_text
from .audit_log import AuditLogger

__all__ = [
    "Product",
    "Variant",
    "ClosetItem",
    "Requirements",
    "HardConstraints",
    "Plan",
    "PlanItem",
    "CATEGORIES",
    "SCENES",
    "DEFAULT_BUDGET_FEN",
    "load_catalog",
    "filter_variants",
    "plan_outfits",
    "validate_plan",
    "validate_all",
    "parse_operation",
    "apply_operation",
    "build_shopping_list",
    "build_board",
    "audit_image",
    "build_garment_card",
    "parse_requirement",
    "parse_natural_text",
    "AuditLogger",
]
