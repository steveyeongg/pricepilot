from fastapi import APIRouter
from app.schemas.roi import ROIInput, ROIOutput
from app.services.roi_calculator import simulate_roi

router = APIRouter(prefix="/api/roi", tags=["roi"])


@router.post("/simulate", response_model=ROIOutput)
async def simulate(body: ROIInput):
    """
    Simulate revenue/profit impact of price changes.
    Uses price elasticity of demand to estimate demand at each price point.
    """
    return simulate_roi(body)
