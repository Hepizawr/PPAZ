from flask import Blueprint, jsonify
from services.stats_service import get_summary_stats

stats_bp = Blueprint("stats", __name__)


@stats_bp.get("/summary")
def summary():
    stats = get_summary_stats()
    return jsonify(stats), 200
