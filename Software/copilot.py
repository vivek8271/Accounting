from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Callable, Tuple
import logging
import json
import csv
from datetime import datetime

# -----------------------------
# Logging configuration (audit)
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("dashboard_trace")

# -----------------------------
# Data models
# -----------------------------
@dataclass(frozen=True)
class ProductRecord:
    product: str
    inventory: int
    units_sold: int
    revenue: int  # in INR

@dataclass(frozen=True)
class DashboardSummary:
    total_revenue: int
    total_products: int
    stock_available: int
    monthly_growth_percent: float

# -----------------------------
# Sample dataset (replaceable)
# -----------------------------
SUMMARY = DashboardSummary(
    total_revenue=480000,
    total_products=18,
    stock_available=1240,
    monthly_growth_percent=12.4
)

PRODUCTS: List[ProductRecord] = [
    ProductRecord("Cement (UltraTech)", inventory=320, units_sold=180, revenue=90000),
    ProductRecord("TMT Steel",          inventory=210, units_sold=140, revenue=140000),
    ProductRecord("River Sand",         inventory=710, units_sold=460, revenue=250000),
]

# -----------------------------
# Validation utilities
# -----------------------------
def _validate_non_negative(name: str, value: Optional[int]) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")

def _validate_range(name_min: str, name_max: str, min_val: Optional[int], max_val: Optional[int]) -> None:
    if min_val is not None and max_val is not None and min_val > max_val:
        raise ValueError(f"{name_min} cannot be greater than {name_max} (got {min_val} > {max_val})")

# -----------------------------
# Requirement mapping
# -----------------------------
@dataclass
class UserRequirement:
    min_inventory: Optional[int] = None
    max_inventory: Optional[int] = None
    min_units_sold: Optional[int] = None
    max_units_sold: Optional[int] = None
    min_revenue: Optional[int] = None
    max_revenue: Optional[int] = None
    product_contains: Optional[str] = None  # case-insensitive substring
    sort_by: Optional[str] = None           # "inventory" | "units_sold" | "revenue" | "product"
    sort_desc: bool = True
    limit: Optional[int] = None

    def validate(self) -> None:
        _validate_non_negative("min_inventory", self.min_inventory)
        _validate_non_negative("max_inventory", self.max_inventory)
        _validate_non_negative("min_units_sold", self.min_units_sold)
        _validate_non_negative("max_units_sold", self.max_units_sold)
        _validate_non_negative("min_revenue", self.min_revenue)
        _validate_non_negative("max_revenue", self.max_revenue)
        _validate_range("min_inventory", "max_inventory", self.min_inventory, self.max_inventory)
        _validate_range("min_units_sold", "max_units_sold", self.min_units_sold, self.max_units_sold)
        _validate_range("min_revenue", "max_revenue", self.min_revenue, self.max_revenue)
        if self.sort_by and self.sort_by not in {"inventory", "units_sold", "revenue", "product"}:
            raise ValueError(f"Unsupported sort_by: {self.sort_by}")

# -----------------------------
# Query engine
# -----------------------------
def build_predicates(req: UserRequirement) -> List[Callable[[ProductRecord], bool]]:
    preds: List[Callable[[ProductRecord], bool]] = []

    if req.min_inventory is not None:
        preds.append(lambda r, m=req.min_inventory: r.inventory >= m)
    if req.max_inventory is not None:
        preds.append(lambda r, M=req.max_inventory: r.inventory <= M)

    if req.min_units_sold is not None:
        preds.append(lambda r, m=req.min_units_sold: r.units_sold >= m)
    if req.max_units_sold is not None:
        preds.append(lambda r, M=req.max_units_sold: r.units_sold <= M)

    if req.min_revenue is not None:
        preds.append(lambda r, m=req.min_revenue: r.revenue >= m)
    if req.max_revenue is not None:
        preds.append(lambda r, M=req.max_revenue: r.revenue <= M)

    if req.product_contains:
        needle = req.product_contains.lower().strip()
        preds.append(lambda r, n=needle: n in r.product.lower())

    return preds

def apply_query(products: List[ProductRecord], req: UserRequirement) -> List[ProductRecord]:
    req.validate()
    predicates = build_predicates(req)

    # Audit: log incoming requirement
    logger.info(f"Query requested: {json.dumps(asdict(req), ensure_ascii=False)}")

    # Filter
    filtered = []
    for p in products:
        if all(pred(p) for pred in predicates):
            filtered.append(p)

    # Sort
    if req.sort_by:
        key_func = {
            "inventory": lambda r: r.inventory,
            "units_sold": lambda r: r.units_sold,
            "revenue": lambda r: r.revenue,
            "product": lambda r: r.product.lower(),
        }[req.sort_by]
        filtered.sort(key=key_func, reverse=req.sort_desc)

    # Limit
    if req.limit is not None:
        filtered = filtered[:req.limit]

    # Audit: log result summary
    logger.info(f"Query result count: {len(filtered)}")
    return filtered

# -----------------------------
# Aggregations & metrics
# -----------------------------
def compute_metrics(products: List[ProductRecord]) -> Dict[str, Any]:
    total_revenue = sum(p.revenue for p in products)
    total_units = sum(p.units_sold for p in products)
    total_inventory = sum(p.inventory for p in products)
    top_by_revenue = max(products, key=lambda p: p.revenue) if products else None

    metrics = {
        "total_revenue_products": total_revenue,
        "total_units_sold_products": total_units,
        "total_inventory_products": total_inventory,
        "top_product_by_revenue": asdict(top_by_revenue) if top_by_revenue else None,
    }
    logger.info(f"Computed metrics: {json.dumps(metrics, ensure_ascii=False)}")
    return metrics

# -----------------------------
# Export utilities
# -----------------------------
def export_to_json(records: List[ProductRecord]) -> str:
    payload = [asdict(r) for r in records]
    return json.dumps(payload, ensure_ascii=False, indent=2)

def export_to_csv(records: List[ProductRecord]) -> str:
    # Returns CSV string (no filesystem dependency)
    headers = ["product", "inventory", "units_sold", "revenue"]
    rows = [asdict(r) for r in records]
    output_lines = []
    output_lines.append(",".join(headers))
    for row in rows:
        output_lines.append(",".join(str(row[h]) for h in headers))
    return "\n".join(output_lines)

# -----------------------------
# Summary accessors
# -----------------------------
def get_summary() -> Dict[str, Any]:
    summary = asdict(SUMMARY)
    logger.info(f"Summary accessed: {json.dumps(summary, ensure_ascii=False)}")
    return summary

def get_products() -> List[ProductRecord]:
    logger.info(f"Products accessed: {len(PRODUCTS)} records")
    return PRODUCTS.copy()

# -----------------------------
# Example usage (callable)
# -----------------------------
def run_example() -> Tuple[Dict[str, Any], List[ProductRecord], Dict[str, Any], str, str]:
    # Access summary
    summary = get_summary()

    # Build requirement: revenue >= 100000 and inventory >= 200
    req = UserRequirement(
        min_revenue=100000,
        min_inventory=200,
        sort_by="revenue",
        sort_desc=True
    )

    # Apply query
    result = apply_query(get_products(), req)

    # Compute metrics on filtered set
    metrics = compute_metrics(result)

    # Export
    json_payload = export_to_json(result)
    csv_payload = export_to_csv(result)

    return summary, result, metrics, json_payload, csv_payload

if __name__ == "__main__":
    summary, result, metrics, json_payload, csv_payload = run_example()
    print("Business Accounting Dashboard Summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("\nFiltered Product Data:")
    print(json_payload)

    print("\nFiltered Metrics:")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

    print("\nCSV Export:")
    print(csv_payload)
