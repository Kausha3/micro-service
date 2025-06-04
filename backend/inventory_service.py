"""
Inventory Service for Lead-to-Lease Chat Concierge

A comprehensive apartment unit inventory management service that provides realistic
simulation of apartment availability and booking for the Lead-to-Lease Chat Concierge.

## Core Features
- **Diverse Unit Portfolio**: Studio through 4-bedroom apartments with realistic pricing
- **Availability Simulation**: 15% unavailability rate to demonstrate real-world scenarios
- **Unit Reservation System**: Track and manage unit bookings and availability
- **Realistic Data**: Market-rate pricing, square footage, and amenity variations
- **Flexible Querying**: Search by bedroom count, specific unit ID, or availability

## Unit Types and Pricing Structure
- **Studio Units**: 450-500 sq ft, $1,500-1,600/month (Entry-level options)
- **1-Bedroom Units**: 650-750 sq ft, $1,800-2,000/month (Most popular)
- **2-Bedroom Units**: 950-1,100 sq ft, $2,400-2,700/month (Family-friendly)
- **3-Bedroom Units**: 1,200-1,350 sq ft, $3,200-3,500/month (Spacious living)
- **4-Bedroom Units**: 1,600-1,750 sq ft, $4,200-4,500/month (Premium options)

## Availability Simulation
Implements realistic availability patterns:
- **85% Base Availability**: Most units available for immediate booking
- **15% Unavailability Rate**: Simulates real-world scenarios (maintenance, occupied, etc.)
- **Consistent Session Behavior**: Same unit offered consistently within a conversation
- **Preferred Unit Handling**: Bypasses randomization for specific unit requests

## Production Integration
In production environments, this service would integrate with:
- **Property Management Systems**: Yardi, RealPage, AppFolio, Entrata
- **Real-time Availability APIs**: Live inventory data from PMS
- **Pricing Engines**: Dynamic pricing based on market conditions
- **Maintenance Systems**: Unit availability based on maintenance schedules

## Business Logic
- **Lead Qualification**: Matches prospects with appropriate unit types
- **Booking Workflow**: Reserves units upon tour confirmation
- **Inventory Tracking**: Maintains accurate availability status
- **Alternative Suggestions**: Offers similar units when preferred options unavailable
"""

import logging
import random
from typing import List, Optional

from models import Unit

logger = logging.getLogger(__name__)


class InventoryService:
    """
    Intelligent inventory service with realistic apartment unit simulation.

    This service manages the complete apartment inventory lifecycle for the Lead-to-Lease
    Chat Concierge, providing realistic simulation of apartment availability, pricing,
    and booking workflows.

    ## Key Responsibilities
    - **Inventory Management**: Maintain comprehensive apartment unit database
    - **Availability Checking**: Real-time availability queries with realistic simulation
    - **Unit Reservation**: Handle booking and reservation workflows
    - **Data Consistency**: Ensure consistent unit information across conversations
    - **Business Logic**: Implement realistic availability patterns and pricing

    ## Simulation Features
    - **Realistic Unavailability**: 15% of units randomly unavailable to simulate real-world scenarios
    - **Consistent Behavior**: Same unit offered consistently within a conversation session
    - **Preferred Unit Handling**: Direct unit requests bypass availability simulation
    - **Market-Rate Pricing**: Realistic rent prices based on bedroom count and square footage

    ## Unit Portfolio
    The service maintains a diverse portfolio of 15 apartment units:
    - 3 Studio units (0 bed): Entry-level pricing for budget-conscious renters
    - 4 One-bedroom units: Most popular option for singles and couples
    - 4 Two-bedroom units: Family-friendly options with varied layouts
    - 2 Three-bedroom units: Spacious options for larger families
    - 2 Four-bedroom units: Premium options for maximum space

    ## Production Considerations
    In production environments, this service would:
    - Connect to property management system APIs (Yardi, RealPage, AppFolio)
    - Implement real-time availability updates
    - Handle complex pricing rules and lease terms
    - Integrate with maintenance and occupancy systems
    - Support multiple properties and unit types

    Attributes:
        units (List[Unit]): Complete inventory of apartment units
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
            Unit(
                unit_id="S104", beds=0, baths=1.0, sqft=450, rent=1500, available=True
            ),
            Unit(
                unit_id="S207", beds=0, baths=1.0, sqft=500, rent=1600, available=True
            ),
            Unit(
                unit_id="S310", beds=0, baths=1.0, sqft=475, rent=1550, available=True
            ),
            # 1-bedroom units - Most popular
            Unit(
                unit_id="A101", beds=1, baths=1.0, sqft=650, rent=1800, available=True
            ),
            Unit(
                unit_id="A205", beds=1, baths=1.0, sqft=700, rent=1900, available=True
            ),
            Unit(
                unit_id="A308", beds=1, baths=1.5, sqft=750, rent=2000, available=True
            ),
            Unit(
                unit_id="A412", beds=1, baths=1.0, sqft=675, rent=1850, available=True
            ),
            # 2-bedroom units - Family friendly
            Unit(
                unit_id="B301", beds=2, baths=2.0, sqft=950, rent=2400, available=True
            ),
            Unit(
                unit_id="B402", beds=2, baths=2.0, sqft=1000, rent=2500, available=True
            ),
            Unit(
                unit_id="B503", beds=2, baths=2.5, sqft=1100, rent=2700, available=True
            ),
            Unit(
                unit_id="B604", beds=2, baths=2.0, sqft=975, rent=2450, available=True
            ),
            # 3-bedroom units - Spacious options
            Unit(
                unit_id="C501", beds=3, baths=2.5, sqft=1200, rent=3200, available=True
            ),
            Unit(
                unit_id="C602", beds=3, baths=2.5, sqft=1250, rent=3300, available=False
            ),  # Pre-reserved
            Unit(
                unit_id="C703", beds=3, baths=3.0, sqft=1350, rent=3500, available=True
            ),
            Unit(
                unit_id="C804", beds=3, baths=2.5, sqft=1225, rent=3250, available=True
            ),
            # 4-bedroom units - Premium options
            Unit(
                unit_id="D801", beds=4, baths=3.0, sqft=1600, rent=4200, available=True
            ),
            Unit(
                unit_id="D902", beds=4, baths=3.5, sqft=1750, rent=4500, available=True
            ),
            Unit(
                unit_id="D1003", beds=4, baths=3.0, sqft=1650, rent=4300, available=True
            ),
        ]

    def check_inventory(
        self, beds: int, preferred_unit_id: Optional[str] = None
    ) -> Optional[Unit]:
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
            unit for unit in self.units if unit.beds == beds and unit.available
        ]

        if not available_units:
            logger.info(f"No {beds}-bedroom units available")
            return None

        # If a preferred unit is specified and available, return it (skip randomization)
        if preferred_unit_id:
            preferred_unit = next(
                (unit for unit in available_units if unit.unit_id == preferred_unit_id),
                None,
            )
            if preferred_unit:
                logger.info(f"Found preferred unit: {preferred_unit.unit_id}")
                return preferred_unit

        # Simulate realistic unavailability (15% chance) only for new searches
        # This demonstrates the "no availability" conversation flow
        # nosec B311 - Using random for demo simulation, not cryptographic purposes
        if random.random() < 0.15:  # nosec B311
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

    def get_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        """
        Get a specific unit by its ID.

        Args:
            unit_id (str): Unique unit identifier

        Returns:
            Optional[Unit]: Unit if found, None otherwise
        """
        for unit in self.units:
            if unit.unit_id == unit_id:
                logger.info(f"Found unit: {unit_id}")
                return unit

        logger.warning(f"Unit not found: {unit_id}")
        return None

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

        logger.warning(
            f"Failed to reserve unit: {unit_id} (not found or already reserved)"
        )
        return False


# Global service instance for application use
inventory_service = InventoryService()
