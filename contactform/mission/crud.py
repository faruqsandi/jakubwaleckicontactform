from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contactform.database import Base, Mission
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///contactform.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session will be closed by the caller


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


class MissionCRUD:
    """CRUD operations for Mission model"""

    @staticmethod
    def create_mission(
        name: str, pre_defined_fields: dict[str, str], db: Session | None = None
    ) -> Mission:
        """
        Create a new mission

        Args:
            name: Mission name
            pre_defined_fields: Dictionary of field names and values
            db: Database session (optional)

        Returns:
            Created Mission object
        """
        close_session = False
        if db is None:
            db = get_db()
            close_session = True

        try:
            # Add name to pre_defined_fields if not present
            if "name" not in pre_defined_fields:
                pre_defined_fields["name"] = name

            mission = Mission(pre_defined_fields=pre_defined_fields)
            db.add(mission)
            db.commit()
            db.refresh(mission)
            return mission
        finally:
            if close_session:
                db.close()

    @staticmethod
    def get_mission(mission_id: int, db: Session | None = None) -> Mission | None:
        """
        Get mission by ID

        Args:
            mission_id: Mission ID
            db: Database session (optional)

        Returns:
            Mission object or None if not found
        """
        close_session = False
        if db is None:
            db = get_db()
            close_session = True

        try:
            return db.query(Mission).filter(Mission.id == mission_id).first()
        finally:
            if close_session:
                db.close()

    @staticmethod
    def get_all_missions(db: Session | None = None) -> list[Mission]:
        """
        Get all missions

        Args:
            db: Database session (optional)

        Returns:
            List of Mission objects
        """
        close_session = False
        if db is None:
            db = get_db()
            close_session = True

        try:
            return db.query(Mission).order_by(Mission.created_date.desc()).all()
        finally:
            if close_session:
                db.close()

    @staticmethod
    def update_mission(
        mission_id: int,
        name: str | None = None,
        pre_defined_fields: dict[str, str] | None = None,
        db: Session | None = None,
    ) -> Mission | None:
        """
        Update mission

        Args:
            mission_id: Mission ID
            name: New mission name (optional)
            pre_defined_fields: New pre-defined fields (optional)
            db: Database session (optional)

        Returns:
            Updated Mission object or None if not found
        """
        close_session = False
        if db is None:
            db = get_db()
            close_session = True

        try:
            mission = db.query(Mission).filter(Mission.id == mission_id).first()
            if mission:
                if pre_defined_fields is not None:
                    # Update name in pre_defined_fields if provided
                    if name is not None and "name" in mission.pre_defined_fields:
                        pre_defined_fields["name"] = name
                    mission.pre_defined_fields = pre_defined_fields
                elif name is not None and "name" in mission.pre_defined_fields:
                    # Update just the name in existing pre_defined_fields
                    updated_fields = mission.pre_defined_fields.copy()
                    updated_fields["name"] = name
                    mission.pre_defined_fields = updated_fields

                mission.last_updated = datetime.now(timezone.utc)
                db.commit()
                db.refresh(mission)
            return mission
        finally:
            if close_session:
                db.close()

    @staticmethod
    def delete_mission(mission_id: int, db: Session | None = None) -> bool:
        """
        Delete mission

        Args:
            mission_id: Mission ID
            db: Database session (optional)

        Returns:
            True if deleted, False if not found
        """
        close_session = False
        if db is None:
            db = get_db()
            close_session = True

        try:
            mission = db.query(Mission).filter(Mission.id == mission_id).first()
            if mission:
                db.delete(mission)
                db.commit()
                return True
            return False
        finally:
            if close_session:
                db.close()


# Convenience functions


def create_mission(name: str, pre_defined_fields: dict[str, str]) -> Mission:
    """Create a new mission"""
    return MissionCRUD.create_mission(name, pre_defined_fields)


def get_mission(mission_id: int) -> Mission | None:
    """Get mission by ID"""
    return MissionCRUD.get_mission(mission_id)


def get_all_missions() -> list[Mission]:
    """Get all missions"""
    return MissionCRUD.get_all_missions()


def update_mission(
    mission_id: int,
    name: str | None = None,
    pre_defined_fields: dict[str, str] | None = None,
) -> Mission | None:
    """Update mission"""
    return MissionCRUD.update_mission(mission_id, name, pre_defined_fields)


def delete_mission(mission_id: int) -> bool:
    """Delete mission"""
    return MissionCRUD.delete_mission(mission_id)
