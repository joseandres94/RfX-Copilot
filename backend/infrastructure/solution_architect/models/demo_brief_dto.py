"""
DTOs (Data Transfer Objects) for Demo Brief using Pydantic.
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
    """Evidence reference for demo brief"""
    chunk_id: str
    section: Optional[str] = None


# =====================
# Enums
# =====================

class DemoTypeEnum(str, Enum):
    STANDARD = "standard"
    CUSTOM = "custom"
    POC = "poc"
    WORKSHOP = "workshop"
    UNKNOWN = "unknown"


class CoverageEnum(str, Enum):
    COVERED = "covered"
    PARTIALLY_COVERED = "partially_covered"
    NOT_COVERED = "not_covered"
    UNKNOWN = "unknown"


class PersonaEnum(str, Enum):
    SALES_REP = "sales_rep"
    DEALER = "dealer"
    APPROVER = "approver"
    OTHER = "other"
    UNKNOWN = "unknown"


class DataSourceEnum(str, Enum):
    CUSTOMER = "customer"
    SYNTHETIC = "synthetic"
    INTERNAL_TEMPLATE = "internal_template"
    UNKNOWN = "unknown"


class DataStatusEnum(str, Enum):
    MISSING = "missing"
    AVAILABLE = "available"
    TO_GENERATE = "to_generate"
    UNKNOWN = "unknown"


class SeverityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class StandaloneOrIntegratedEnum(str, Enum):
    STANDALONE = "standalone"
    INTEGRATED = "integrated"
    UNKNOWN = "unknown"


class TeamEnum(str, Enum):
    PRODUCT = "product"
    SECURITY = "security"
    LEGAL = "legal"
    INFRA = "infra"
    SALES_ENGINEERING = "sales_engineering"
    SALES = "sales"  # LLM sometimes uses this short form
    OTHER = "other"
    UNKNOWN = "unknown"


# =====================
# Recommended Engagement
# =====================

class RecommendedEngagementDTO(BaseModel):
    demo_type: DemoTypeEnum
    rationale: List[str] = Field(default_factory=list)

    @field_validator('demo_type', mode='before')
    @classmethod
    def normalize_demo_type(cls, v):
        """Convert demo_type to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Requirement Coverage
# =====================

class RequirementCoverageSummaryDTO(BaseModel):
    req_id: str
    coverage: CoverageEnum
    notes: Optional[str] = None

    @field_validator('coverage', mode='before')
    @classmethod
    def normalize_coverage(cls, v):
        """Convert coverage to lowercase before validation"""
        if isinstance(v, str):
            return v.lower().replace('-', '_')
        return v


# =====================
# Scenarios
# =====================

class ScenarioDTO(BaseModel):
    id: str
    name: str
    persona: PersonaEnum
    goal: str
    steps: List[str] = Field(default_factory=list)
    requirements_covered: List[str] = Field(default_factory=list)
    tacton_capabilities_to_highlight: List[str] = Field(default_factory=list)
    demo_assets_needed: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)

    @field_validator('persona', mode='before')
    @classmethod
    def normalize_persona(cls, v):
        """Convert persona to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('acceptance_criteria', mode='before')
    @classmethod
    def normalize_acceptance_criteria(cls, v):
        """Convert string to array if LLM returns string instead of array"""
        if isinstance(v, str):
            return [v]
        return v


# =====================
# Data and Content Plan
# =====================

class DataRequirementDTO(BaseModel):
    item: str
    purpose: Optional[str] = None
    source: DataSourceEnum
    status: DataStatusEnum
    notes: Optional[str] = None

    @field_validator('source', mode='before')
    @classmethod
    def normalize_source(cls, v):
        """Convert source to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        """Convert status to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


class DataAndContentPlanDTO(BaseModel):
    data_requirements: List[DataRequirementDTO] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


# =====================
# Environment Spec
# =====================

class EnvironmentSpecDTO(BaseModel):
    standalone_or_integrated: StandaloneOrIntegratedEnum
    base_template: Optional[str] = None
    markets_regions_to_simulate: List[str] = Field(default_factory=list)
    roles_to_simulate: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    nonfunctional_expectations: List[str] = Field(default_factory=list)

    @field_validator('standalone_or_integrated', mode='before')
    @classmethod
    def normalize_standalone_or_integrated(cls, v):
        """Convert standalone_or_integrated to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('nonfunctional_expectations', mode='before')
    @classmethod
    def normalize_nonfunctional_expectations(cls, v):
        """Convert string to array if LLM returns string instead of array"""
        if isinstance(v, str):
            return [v]
        return v


# =====================
# Risks
# =====================

class RiskDTO(BaseModel):
    risk: str
    severity: SeverityEnum
    mitigation: Optional[str] = None
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)

    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v):
        """Convert severity to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Internal Alignment Needs
# =====================

class InternalAlignmentNeedDTO(BaseModel):
    team: TeamEnum
    topic: str
    priority: SeverityEnum

    @field_validator('team', mode='before')
    @classmethod
    def normalize_team(cls, v):
        """Convert team to lowercase and normalize common variations"""
        if isinstance(v, str):
            v_lower = v.lower()
            # Map common variations
            if v_lower == "sales":
                return "sales_engineering"  # "sales" -> "sales_engineering"
            # Handle "Product|Security|Legal|Infra|Other" format from prompt
            return v_lower.replace(' ', '_')  # "Sales Engineering" -> "sales_engineering"
        return v

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Phase 2 Automation Hooks
# =====================

class Phase2AutomationHooksDTO(BaseModel):
    goal: str
    provisioning_inputs: List[str] = Field(default_factory=list)
    config_artifacts_to_generate: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


# =====================
# Demo Brief Spec
# =====================

class DemoBriefSpecDTO(BaseModel):
    deal_id: Optional[str] = None
    recommended_engagement: RecommendedEngagementDTO
    demo_objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    requirement_coverage_summary: List[RequirementCoverageSummaryDTO] = Field(default_factory=list)
    scenarios: List[ScenarioDTO] = Field(default_factory=list)
    data_and_content_plan: DataAndContentPlanDTO
    environment_spec: EnvironmentSpecDTO
    risks: List[RiskDTO] = Field(default_factory=list)
    open_questions_customer: List[str] = Field(default_factory=list)
    internal_alignment_needs: List[InternalAlignmentNeedDTO] = Field(default_factory=list)
    phase2_automation_hooks: Phase2AutomationHooksDTO


# =====================
# Main Demo Brief DTO
# =====================

class DemoBriefDTO(BaseModel):
    """
    Main DTO for Demo Brief.
    Validates LLM response and can be converted to Domain entity if needed.
    """
    demo_brief_markdown: str
    demo_brief_spec: DemoBriefSpecDTO

