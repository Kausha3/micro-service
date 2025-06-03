"""
Inventory Service for Lead-to-Lease Chat Concierge

This module provides apartment unit inventory management with realistic
simulation features including:
- Diverse unit types (studio to 4-bedroom)
- Randomized availability to simulate real-world scenarios
- Unit reservation and tracking
- Mock data that represents a typical apartment complex

In production, this would integrate with property management systems
like Yardi, RealPage, or AppFolio.

Author: Augment Agent
Version: 1.0.0
"""

from models import Unit
from typing import Optional, List
import random
import logging

logger = logging.getLogger(__name__)


class InventoryService:
    """
    Intelligent inventory service with realistic apartment unit simulation.

    Features:
    - Comprehensive unit variety (studio through 4-bedroom)
    - Randomized availability (15% unavailability rate)
    - Unit reservation tracking
    - Realistic pricing and square footage

    In production, this would connect to property management systems
    for real-time inventory data.
    """

    def __init__(self):
        """Initialize with diverse mock inventory data."""
        self.units = self._create_mock_inventory()
        logger.info(f"Initialized inventory with {len(self.units)} units")

    def _create_mock_inventory(self) -> List[Unit]:
        """
        Create realistic mock inventory data.

        Returns:
            List[Unit]: Comprehensive list of apartment units
        """
        return [
            # Studio units - Entry level
            Unit(unit_id="S104", beds=0, baths=1.0, sqft=450, rent=1500, available=True),
            Unit(unit_id="S207", beds=0, baths=1.0, sqft=500, rent=1600, available=True),
            Unit(unit_id="S310", beds=0, baths=1.0, sqft=475, rent=1550, available=True),

            # 1-bedroom units - Most popular
            Unit(unit_id="A101", beds=1, baths=1.0, sqft=650, rent=1800, available=True),
            Unit(unit_id="A205", beds=1, baths=1.0, sqft=700, rent=1900, available=True),
            Unit(unit_id="A308", beds=1, baths=1.5, sqft=750, rent=2000, available=True),
            Unit(unit_id="A412", beds=1, baths=1.0, sqft=675, rent=1850, available=True),

            # 2-bedroom units - Family friendly
            Unit(unit_id="B301", beds=2, baths=2.0, sqft=950, rent=2400, available=True),
            Unit(unit_id="B402", beds=2, baths=2.0, sqft=1000, rent=2500, available=True),
            Unit(unit_id="B503", beds=2, baths=2.5, sqft=1100, rent=2700, available=True),
            Unit(unit_id="B604", beds=2, baths=2.0, sqft=975, rent=2450, available=True),

            # 3-bedroom units - Spacious options
            Unit(unit_id="C501", beds=3, baths=2.5, sqft=1200, rent=3200, available=True),
            Unit(unit_id="C602", beds=3, baths=2.5, sqft=1250, rent=3300, available=False),  # Pre-reserved
            Unit(unit_id="C703", beds=3, baths=3.0, sqft=1350, rent=3500, available=True),
            Unit(unit_id="C804", beds=3, baths=2.5, sqft=1225, rent=3250, available=True),

            # 4-bedroom units - Premium options
            Unit(unit_id="D801", beds=4, baths=3.0, sqft=1600, rent=4200, available=True),
            Unit(unit_id="D902", beds=4, baths=3.5, sqft=1750, rent=4500, available=True),
            Unit(unit_id="D1003", beds=4, baths=3.0, sqft=1650, rent=4300, available=True),
        ]

    def check_inventory(self, beds: int, preferred_unit_id: Optional[str] = None) -> Optional[Unit]:
        """
        Check for available units with specified bedroom count.

        Implements realistic availability simulation with 15% unavailability rate
        to demonstrate real-world scenarios where units may not be available.

        Args:
            beds (int): Number of bedrooms requested (0-4)
            preferred_unit_id (Optional[str]): If provided, try to return this specific unit

        Returns:
            Optional[Unit]: Available unit matching criteria, or None if unavailable
        """
        # Find all units matching bedroom criteria
        available_units = [
            unit for unit in self.units
            if unit.beds == beds and unit.available
        ]

        if not available_units:
            logger.info(f"No {beds}-bedroom units available")
            return None

        # If a preferred unit is specified and available, return it (skip randomization)
        if preferred_unit_id:
            preferred_unit = next(
                (unit for unit in available_units if unit.unit_id == preferred_unit_id),
                None
            )
            if preferred_unit:
                logger.info(f"Found preferred unit: {preferred_unit.unit_id}")
                return preferred_unit

        # Simulate realistic unavailability (15% chance) only for new searches
        # This demonstrates the "no availability" conversation flow
        if random.random() < 0.15:
            logger.info(f"Simulating unavailability for {beds}-bedroom units")
            return None

        # Return the first available unit for consistency within a session
        # This ensures the same unit is offered consistently
        selected_unit = available_units[0]
        logger.info(f"Found available unit: {selected_unit.unit_id}")
        return selected_unit

    def get_all_available_units(self) -> List[Unit]:
        """
        Get all currently available units.

        Returns:
            List[Unit]: All units marked as available
        """
        available = [unit for unit in self.units if unit.available]
        logger.info(f"Retrieved {len(available)} available units")
        return available

    def reserve_unit(self, unit_id: str) -> bool:
        """
        Reserve a unit by marking it as unavailable.

        This simulates the booking process where a unit becomes
        unavailable after a tour is confirmed.

        Args:
            unit_id (str): Unique unit identifier to reserve

        Returns:
            bool: True if successfully reserved, False if not found or already reserved
        """
        for unit in self.units:
            if unit.unit_id == unit_id and unit.available:
                unit.available = False
                logger.info(f"Successfully reserved unit: {unit_id}")
                return True

        logger.warning(f"Failed to reserve unit: {unit_id} (not found or already reserved)")
        return False

    def get_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        """
        Get unit details by unit ID.

        Args:
            unit_id (str): Unique unit identifier

        Returns:
            Optional[Unit]: Unit details if found, None otherwise
        """
        for unit in self.units:
            if unit.unit_id == unit_id:
                return unit
        return None


# Global service instance for application use
inventory_service = InventoryService()
