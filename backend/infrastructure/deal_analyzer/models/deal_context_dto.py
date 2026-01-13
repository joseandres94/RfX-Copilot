"""
DTOs (Data Transfer Objects) for Deal Context using Pydantic.
These models are used to validate and parse responses from the LLM.
They mirror the Domain entities but use Pydantic for automatic validation.
"""
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# =====================
# Evidence & Metadata
# =====================

class EvidenceRefDTO(BaseModel):
    chunk_id: str
    section: Optional[str] = None
    quote: Optional[str] = None
    confidence: Optional[str] = None


class ExtractionCoverageDTO(BaseModel):
    processed: bool
    warnings: List[str] = Field(default_factory=list)
    sections_detected: List[str] = Field(default_factory=list)
    sections_low_confidence: List[str] = Field(default_factory=list)


class ContactDTO(BaseModel):
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class SubmissionInstructionsDTO(BaseModel):
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    method: Optional[str] = None
    format: Optional[str] = None
    portal_link: Optional[str] = None
    qa_process: Optional[str] = None


class DocumentMetadataDTO(BaseModel):
    rfx_type: str
    contacts: List[ContactDTO] = Field(default_factory=list)
    submission_instructions: SubmissionInstructionsDTO
    title: Optional[str] = None
    customer_name: Optional[str] = None
    issuing_org: Optional[str] = None
    document_date: Optional[str] = None
    revision: Optional[str] = None
    confidentiality: Optional[str] = None
    submission_deadline: Optional[str] = None


# =====================
# Context & Scope
# =====================

class CustomerContextDTO(BaseModel):
    regions_markets: List[str] = Field(default_factory=list)
    current_state: List[str] = Field(default_factory=list)
    business_problems: List[str] = Field(default_factory=list)
    business_drivers: List[str] = Field(default_factory=list)  # LLM returns this field
    key_pain_points: List[str] = Field(default_factory=list)
    success_definition: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    industry: Optional[str] = None
    customer_profile_summary: Optional[str] = None


class ScopeDTO(BaseModel):
    in_scope: List[str] = Field(default_factory=list)
    out_of_scope: List[str] = Field(default_factory=list)
    assumptions_stated_by_customer: List[str] = Field(default_factory=list)
    constraints_global: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


# =====================
# Requirements
# =====================

class RequirementTypeEnum(str, Enum):
    FUNCTIONAL = "functional"
    NONFUNCTIONAL = "nonfunctional"
    INTEGRATION = "integration"
    SECURITY = "security"
    COMMERCIAL = "commercial"
    LEGAL = "legal"
    DELIVERY = "delivery"
    SUPPORT_TRAINING = "support_training"
    UX = "ux"
    DATA = "data"
    UNKNOWN = "unknown"


class PriorityEnum(str, Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    UNKNOWN = "unknown"


class RequirementDTO(BaseModel):
    id: str
    title: str
    description: str
    type: RequirementTypeEnum
    category: str
    priority: PriorityEnum
    dependencies: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    subcategory: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('type', mode='before')
    @classmethod
    def normalize_type(cls, v):
        """Convert requirement type to lowercase before validation"""
        if isinstance(v, str):
            # Handle underscore format: support_training -> support_training
            return v.lower().replace('-', '_')
        return v

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Evaluation
# =====================

class EvaluationCriteriaDTO(BaseModel):
    criterion: str
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    weight: Optional[str] = None
    notes: Optional[str] = None


class StakeholderDTO(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    team: Optional[str] = None


class DecisionProcessDTO(BaseModel):
    stages: List[str] = Field(default_factory=list)
    stakeholders: List[StakeholderDTO] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    timeline: Optional[str] = None


class EvaluationAndSelectionDTO(BaseModel):
    evaluation_criteria: List[EvaluationCriteriaDTO] = Field(default_factory=list)
    decision_process: DecisionProcessDTO


# =====================
# Integrations
# =====================

class SystemTypeEnum(str, Enum):
    ERP = "erp"
    CRM = "crm"
    PLM = "plm"
    CAD = "cad"
    PIM = "pim"
    PRICING = "pricing"
    IDENTITY = "identity"
    OTHER = "other"
    UNKNOWN = "unknown"


class SystemDTO(BaseModel):
    system_name: Optional[str] = None
    system_type: SystemTypeEnum
    constraints: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    notes: Optional[str] = None

    @field_validator('system_name', mode='before')
    @classmethod
    def default_system_name(cls, v):
        """Provide default name if system_name is null"""
        if v is None or v == "":
            return "Unknown System"
        return v

    @field_validator('system_type', mode='before')
    @classmethod
    def normalize_system_type(cls, v):
        """Convert system_type to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


class DataRequirementDTO(BaseModel):
    data_item: str
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    purpose: Optional[str] = None
    format: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class IntegrationsAndDataDTO(BaseModel):
    systems: List[SystemDTO] = Field(default_factory=list)
    data_requirements: List[DataRequirementDTO] = Field(default_factory=list)


# =====================
# Security & Legal
# =====================

class SecurityComplianceDTO(BaseModel):
    requirements: List[str] = Field(default_factory=list)
    standards_certifications: List[str] = Field(default_factory=list)
    privacy: List[str] = Field(default_factory=list)
    access_control_identity: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    data_residency: Optional[str] = None


class CommercialLegalDTO(BaseModel):
    commercial_requirements: List[str] = Field(default_factory=list)
    pricing_licensing_expectations: List[str] = Field(default_factory=list)
    contract_terms: List[str] = Field(default_factory=list)
    sla_support: List[str] = Field(default_factory=list)
    procurement_process: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


# =====================
# Timeline & Demo
# =====================

class MilestoneDTO(BaseModel):
    milestone: str
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    date_or_window: Optional[str] = None


class DeliveryTimelineDTO(BaseModel):
    milestones: List[MilestoneDTO] = Field(default_factory=list)
    implementation_constraints: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


class ExplicitDemoOrPocRequestDTO(BaseModel):
    title: Optional[str] = None  # LLM uses 'title'
    scenario: Optional[str] = None  # Domain uses 'scenario'
    artifacts: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    expectations: List[str] = Field(default_factory=list)
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


class ExplicitDemoOrPocRequestsDTO(BaseModel):
    requested: bool
    requests: List[ExplicitDemoOrPocRequestDTO] = Field(default_factory=list)
    scenarios: List[ExplicitDemoOrPocRequestDTO] = Field(default_factory=list)  # LLM uses 'scenarios'
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)


# =====================
# Risks & Questions
# =====================

class SeverityEnum(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RiskUnknownsAmbiguityDTO(BaseModel):
    item: str
    severity: SeverityEnum
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    why_it_matters: Optional[str] = None

    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v):
        """Convert severity to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


class ClarificationQuestionDTO(BaseModel):
    question: str
    priority: SeverityEnum  # LLM uses high/medium/low, not must/should/could
    evidence_refs: List[EvidenceRefDTO] = Field(default_factory=list)
    reason: Optional[str] = None

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to lowercase before validation"""
        if isinstance(v, str):
            return v.lower()
        return v


# =====================
# Glossary
# =====================

class KeyTermAcronymDTO(BaseModel):
    term: str
    meaning: Optional[str] = None


class EntitiesGlossaryDTO(BaseModel):
    products: List[str] = Field(default_factory=list)
    roles_personas: List[str] = Field(default_factory=list)
    geographies: List[str] = Field(default_factory=list)
    currencies: List[str] = Field(default_factory=list)
    key_terms_acronyms: List[KeyTermAcronymDTO] = Field(default_factory=list)


# =====================
# Main DealContext DTO
# =====================

class DealContextDTO(BaseModel):
    """
    Main DTO for Deal Context Model.
    Validates LLM response and can be converted to Domain entity.
    """
    dcm_version: str
    extraction_coverage: ExtractionCoverageDTO
    document_metadata: DocumentMetadataDTO
    customer_context: CustomerContextDTO
    scope: ScopeDTO
    requirements: List[RequirementDTO] = Field(default_factory=list)
    evaluation_and_selection: EvaluationAndSelectionDTO
    integrations_and_data: IntegrationsAndDataDTO
    security_compliance: SecurityComplianceDTO
    commercial_legal: CommercialLegalDTO
    delivery_timeline: DeliveryTimelineDTO
    explicit_demo_or_poc_requests: ExplicitDemoOrPocRequestsDTO
    risks_unknowns_ambiguities: List[RiskUnknownsAmbiguityDTO] = Field(default_factory=list)
    clarification_questions: List[ClarificationQuestionDTO] = Field(default_factory=list)
    entities_glossary: EntitiesGlossaryDTO

