"""
DTOs (Data Transfer Objects) for Gap Analysis using Pydantic.
These models are used to validate and parse responses from the LLM.
They follow the same pattern as deal_context_dto.py.
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# =====================
# Evidence References
# =====================

class EvidenceRefDTO(BaseModel):
    """Evidence reference for gap analysis"""
    chunk_id: str
    section: Optional[str] = None


# =====================
# Enums
# =====================

class RequirementPriorityEnum(str, Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    UNKNOWN = "unknown"


class CoverageStatusEnum(str, Enum):
    COVERED = "covered"
    PARTIALLY_COVERED = "partially_covered"
    NOT_COVERED = "not_covered"
    UNKNOWN = "unknown"


class GapTypeEnum(str, Enum):
    MISSING_INFO = "missing_info"
    NOT_COVERED = "not_covered"
    PARTIAL_COVERAGE = "partial_coverage"
    CONFLICT = "conflict"
    SCOPE_RISK = "scope_risk"
    FEASIBILITY_RISK = "feasibility_risk"
    COMPLIANCE_RISK = "compliance_risk"
    DATA_RISK = "data_risk"
    INTEGRATION_RISK = "integration_risk"
    SUBMISSION_RISK = "submission_risk"
    ASSUMPTION_TO_CONFIRM = "assumption_to_confirm"  # LLM sometimes uses this value
    UNKNOWN = "unknown"


class SeverityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class PriorityEnum(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ActionTypeEnum(str, Enum):
    CUSTOMER_QUESTION = "customer_question"
    INTERNAL_VALIDATION = "internal_validation"
    DEMO_ADJUSTMENT = "demo_adjustment"
    ASSUMPTION_TO_CONFIRM = "assumption_to_confirm"
    UNKNOWN = "unknown"


class TeamEnum(str, Enum):
    SALES_ENGINEERING = "sales_engineering"
    PRODUCT = "product"
    SECURITY = "security"
    LEGAL = "legal"
    INFRA = "infra"
    OTHER = "other"
    UNKNOWN = "unknown"


class ConfidenceEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =====================
# Coverage Audit
# =====================

class WhereInDemoBriefDTO(BaseModel):
    scenario_ids: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class CoverageAuditDTO(BaseModel):
    req_id: str
    priority: RequirementPriorityEnum
    status: CoverageStatusEnum
    where_in_demo_brief: WhereInDemoBriefDTO
    impact_if_missing: Optional[str] = None
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        """Convert status to lowercase before validation"""
        if isinstance(v, str):
            return v.lower().replace('-', '_')
        return v


# =====================
# Gaps
# =====================

class RecommendedActionDTO(BaseModel):
    action_type: ActionTypeEnum
    owner_team: TeamEnum
    suggested_next_step: str

    @field_validator('action_type', mode='before')
    @classmethod
    def normalize_action_type(cls, v):
        """Convert action_type to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('owner_team', mode='before')
    @classmethod
    def normalize_owner_team(cls, v):
        """Convert owner_team to lowercase, handle 'Sales Engineering' format"""
        if isinstance(v, str):
            # Handle "Sales Engineering" -> "sales_engineering"
            return v.lower().replace(' ', '_')
        return v


class GapDTO(BaseModel):
    id: str
    title: str
    type: GapTypeEnum
    severity: SeverityEnum
    priority: PriorityEnum
    description: str
    affected_requirements: List[str] = Field(default_factory=list)
    recommended_action: RecommendedActionDTO
    confidence: ConfidenceEnum
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)

    @field_validator('type', mode='before')
    @classmethod
    def normalize_type(cls, v):
        """Convert gap type to lowercase before validation"""
        if isinstance(v, str):
            return v.lower().replace('-', '_')
        return v

    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v):
        """Convert severity to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to uppercase (P0, P1, P2)"""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator('confidence', mode='before')
    @classmethod
    def normalize_confidence(cls, v):
        """Convert confidence to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Conflicts
# =====================

class ConflictDTO(BaseModel):
    conflict: str
    why_it_matters: Optional[str] = None
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


# =====================
# Next Steps
# =====================

class NextStepInternalDTO(BaseModel):
    priority: PriorityEnum
    team: TeamEnum
    task: str
    expected_output: Optional[str] = None

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to uppercase (P0, P1, P2)"""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator('team', mode='before')
    @classmethod
    def normalize_team(cls, v):
        """Convert team to lowercase, handle 'Sales Engineering' format"""
        if isinstance(v, str):
            return v.lower().replace(' ', '_')
        return v


class NextStepCustomerDTO(BaseModel):
    priority: PriorityEnum
    question_or_request: str
    reason: Optional[str] = None

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to uppercase (P0, P1, P2)"""
        if isinstance(v, str):
            return v.upper()
        return v


# =====================
# Drafts Optional
# =====================

class DraftOutlineDTO(BaseModel):
    include: bool
    bullets: List[str] = Field(default_factory=list)


class DraftsOptionalDTO(BaseModel):
    clarification_email_outline: DraftOutlineDTO
    workshop_agenda_outline: DraftOutlineDTO


# =====================
# Top Risks
# =====================

class TopRiskDTO(BaseModel):
    risk: str
    severity: SeverityEnum
    mitigation: Optional[str] = None

    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v):
        """Convert severity to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Gap Analysis Spec
# =====================

class GapAnalysisSpecDTO(BaseModel):
    deal_id: Optional[str] = None
    coverage_audit: List[CoverageAuditDTO] = Field(default_factory=list)
    gaps: List[GapDTO] = Field(default_factory=list)
    conflicts: List[ConflictDTO] = Field(default_factory=list)
    next_steps_internal: List[NextStepInternalDTO] = Field(default_factory=list)
    next_steps_customer: List[NextStepCustomerDTO] = Field(default_factory=list)
    drafts_optional: DraftsOptionalDTO
    assumptions_to_confirm: List[str] = Field(default_factory=list)
    top_risks: List[TopRiskDTO] = Field(default_factory=list)


# =====================
# Main Gap Analysis DTO
# =====================

class GapAnalysisDTO(BaseModel):
    """
    Main DTO for Gap Analysis.
    Validates LLM response and can be converted to Domain entity if needed.
    """
    gap_analysis_markdown: str
    gap_analysis_spec: GapAnalysisSpecDTO

