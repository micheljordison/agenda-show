from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.repositorio.db.context import Base


class AppointmentUser(Base):
    __tablename__ = "appointment_users"
    __table_args__ = (UniqueConstraint("user_id", "appointment_id", name="uq_appointment_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    user: Mapped["User"] = relationship(back_populates="appointments")
    appointment: Mapped["Appointment"] = relationship(back_populates="participants")
