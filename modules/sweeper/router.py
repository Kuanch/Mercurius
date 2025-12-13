from fastapi import APIRouter, HTTPException
from modules.sweeper.schemas.plan import Plan
from modules.sweeper.executor import preview_plan, execute_plan

router = APIRouter(prefix="/sweeper", tags=["sweeper"])

@router.post("/preview")
def preview(plan: Plan):
    try:
        return preview_plan(plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
def execute(plan: Plan):
    if plan.dry_run:
        raise HTTPException(status_code=400, detail="Set dry_run=false to execute.")
    if not plan.confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to execute.")
    try:
        return execute_plan(plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
