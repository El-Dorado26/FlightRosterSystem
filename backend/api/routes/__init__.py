# Routes package
from .flights import router as flights_router
from .flight_crew import router as flight_crew_router
from .cabin_crew import router as cabin_crew_router
from .passengers import router as passengers_router

__all__ = [
    "flights_router",
    "flight_crew_router",
    "cabin_crew_router",
    "passengers_router",
]
