from sqlalchemy import text, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base, str_uniq
from typing import Literal


class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class Position(Base):
    __tablename__ = "position"

    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="position")
    process_description = relationship(
        "ProcessDescription",
        back_populates="position"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    position_id: Mapped[int] = mapped_column(
        ForeignKey('position.id'),
        default=1,
        server_default=text("1")
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id'),
        default=1,
        server_default=text("1")
    )
    position: Mapped["Position"] = relationship(
        "Position",
        back_populates="users",
        lazy="joined"
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        lazy="joined"
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Clients(Base):
    __tablename__: Literal["clients"] = "clients"

    name: Mapped[str]
    description: Mapped[str] = mapped_column(Text)

    orders = relationship(
        "Orders",
        back_populates="clients"
    )


class Orders(Base):
    __tablename__: Literal["orders"] = "orders"

    number: Mapped[int] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    clients = relationship("Clients", back_populates="orders")


class Action(Base):
    __tablename__: Literal["action"] = "action"

    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(
        ForeignKey("process.id"),
        nullable=False
    )
    actions_description_id: Mapped[int] = mapped_column(
        ForeignKey("action_description.id"),
        nullable=False
    )
    implementer_user_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True
    )
    queue: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="pending")

    __table_args__ = (
        UniqueConstraint(
            'process_id',
            'queue',
            name='uq_action_process_queue'
        ),
    )

    action_description = relationship(
        "ActionDescription",
        back_populates="actions",
        lazy="joined"
    )
    process = relationship(
        "Process",
        back_populates="actions"
    )


class ActionDescription(Base):
    __tablename__: Literal["action_description"] = "action_description"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    description: Mapped[str] = mapped_column(Text)

    actions = relationship(
        "Action",
        back_populates="action_description",
        cascade="all, delete-orphan"
    )


class Process(Base):
    __tablename__: Literal["process"] = "process"

    id: Mapped[int] = mapped_column(primary_key=True)
    process_description_id: Mapped[int] = mapped_column(
        ForeignKey("process_description.id"))
    order_id: Mapped[int] = mapped_column(index=True)
    coordinator_user_id: Mapped[int] = mapped_column(index=True)
    queue: Mapped[int]
    status: Mapped[str] = mapped_column(default="pending")

    __table_args__ = (
        UniqueConstraint(
            'order_id',
            'queue',
            name='uq_process_order_queue'
        ),
    )

    process_description = relationship(
        "ProcessDescription",
        back_populates="processes",
        lazy="joined"
    )
    actions = relationship(
        "Action",
        back_populates="process",
        cascade="all, delete-orphan"
    )


class ProcessDescription(Base):
    __tablename__: Literal["process_description"] = "process_description"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column(Text)
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"))
    position = relationship("Position", back_populates="process_description")
    processes = relationship(
        "Process",
        back_populates="process_description",
        cascade="all, delete-orphan"
    )
