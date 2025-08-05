from fastapi import APIRouter, HTTPException
from typing import List
import os
import json

from utils.config import load_config

router = APIRouter()
config = load_config("config.yaml")
output_dir = config.get("output_dir", "reports")

@router.get("/results", summary="List all scan reports")
def list_reports() -> List[str]:
    try:
        files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing reports: {str(e)}")

@router.get("/results/{report_name}", summary="Get a specific scan report")
def get_report(report_name: str):
    file_path = os.path.join(output_dir, report_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading report: {str(e)}")