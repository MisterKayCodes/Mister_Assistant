from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from data.models import User, Activity, Spending, Pattern
from config import settings

class Repository:
    """The Librarian (Vault Access)."""
    
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def get_user_by_tg_id(self, telegram_id: int) -> Optional[User]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, recovery_key: str) -> User:
        async with self.session_factory() as session:
            user = User(telegram_id=telegram_id, recovery_key=recovery_key)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def update_owner_id(self, old_tg_id: int, new_tg_id: int):
        async with self.session_factory() as session:
            await session.execute(
                update(User).where(User.telegram_id == old_tg_id).values(telegram_id=new_tg_id)
            )
            await session.commit()

    # Activity Tracking
    async def start_activity(self, name: str, mood: Optional[str] = None) -> Activity:
        async with self.session_factory() as session:
            activity = Activity(name=name, mood=mood)
            session.add(activity)
            await session.commit()
            await session.refresh(activity)
            return activity

    async def get_active_activity(self) -> Optional[Activity]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Activity).where(Activity.end_time == None)
            )
            return result.scalar_one_or_none()

    async def end_activity(self, activity_id: int, end_time: datetime, context: dict):
        async with self.session_factory() as session:
            activity = await session.get(Activity, activity_id)
            if activity:
                activity.end_time = end_time
                activity.duration_minutes = int((end_time - activity.start_time).total_seconds() / 60)
                for key, value in context.items():
                    setattr(activity, key, value)
                await session.commit()

    async def add_spending(self, amount: float, category: str, description: Optional[str] = None):
        async with self.session_factory() as session:
            spending = Spending(amount=amount, category=category, description=description)
            session.add(spending)
            await session.commit()

    async def recover_identity(self, recovery_key: str, new_tg_id: int) -> bool:
        """Swap owner ID using the recovery key."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).where(User.recovery_key == recovery_key)
            )
            user = result.scalar_one_or_none()
            if user:
                user.telegram_id = new_tg_id
                await session.commit()
                return True
            return False


    async def get_daily_activities(self, date: datetime) -> List[Activity]:
        """Get all activities for a specific day."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        async with self.session_factory() as session:
            result = await session.execute(
                select(Activity).where(
                    Activity.start_time >= start_of_day,
                    Activity.start_time <= end_of_day
                )
            )
            return result.scalars().all()

    async def get_daily_spending(self, date: datetime) -> List[Spending]:
        """Get all spending for a specific day."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        async with self.session_factory() as session:
            result = await session.execute(
                select(Spending).where(
                    Spending.timestamp >= start_of_day,
                    Spending.timestamp <= end_of_day
                )
            )
            return result.scalars().all()

    async def is_vault_empty(self) -> bool:
        """Check if any user is registered (The Vault check)."""
        async with self.session_factory() as session:
            result = await session.execute(select(User))
            return result.first() is None


repo = Repository(settings.DATABASE_URL)
