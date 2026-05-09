from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    papers = relationship("Paper", back_populates="owner", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    owner = relationship("User", back_populates="papers")
    extracted_data = relationship(
        "ExtractedData",
        back_populates="paper",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    page_wise_text = Column(JSONB, nullable=False)
    complete_text = Column(Text, nullable=False)
    meta_data = Column("metadata", JSONB, nullable=False)
    sections = Column(JSONB, nullable=False)
    algorithms = Column(JSONB, nullable=False)
    datasets = Column(JSONB, nullable=False)
    results = Column(JSONB, nullable=False)
    
    # Advanced Intelligence Fields
    strengths = Column(JSONB, nullable=True)
    weaknesses = Column(JSONB, nullable=True)
    novelty = Column(Text, nullable=True)
    research_gap = Column(Text, nullable=True)
    future_scope = Column(Text, nullable=True)
    complexity = Column(String(50), nullable=True) # e.g., "Intermediate"
    reading_time = Column(Integer, nullable=True) # in minutes
    reproducibility_score = Column(Float, nullable=True) # 0 to 1
    domain = Column(String(255), nullable=True)
    intelligence_report = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    paper = relationship("Paper", back_populates="extracted_data")
