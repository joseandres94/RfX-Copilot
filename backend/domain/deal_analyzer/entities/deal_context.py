from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


@dataclass
class EvidenceRef:
    chunk_id: str
    section: Optional[str] = None
    quote: Optional[str] = None
    confidence: Optional[str] = None


@dataclass
class ExtractionCoverage:
    processed: bool
    warnings: List[str]
    sections_detected: List[str]
    sections_low_confidence: List[str]


@dataclass
class Contact:
    evidence_refs: List[EvidenceRef]
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    
@dataclass
class SubmissionInstructions:
    evidence_refs: List[EvidenceRef]
    method: Optional[str] = None
    format: Optional[str] = None
    portal_link: Optional[str] = None
    qa_process: Optional[str] = None


@dataclass
class DocumentMetadata:
    rfx_type: str
    contacts: List[Contact]
    submission_instructions: SubmissionInstructions
    title: Optional[str] = None
    customer_name: Optional[str] = None
    issuing_org: Optional[str] = None
    document_date: Optional[str] = None
    revision: Optional[str] = None
    confidentiality: Optional[str] = None
    submission_deadline: Optional[str] = None


@dataclass
class CustomerContext:
    regions_markets: List[str]
    current_state: List[str]
    business_problems: List[str]
    key_pain_points: List[str]
    success_definition: List[str]
    evidence_refs: List[EvidenceRef]
    industry: Optional[str] = None
    customer_profile_summary: Optional[str] = None


@dataclass
class Scope:
    in_scope: List[str]
    out_of_scope: List[str]
    assumptions_stated_by_customer: List[str]
    constraints_global: List[str]
    evidence_refs: List[EvidenceRef]


class RequirementType(Enum):
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


class Priority(Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    UNKNOWN = "unknown"

@dataclass
class Requirement:
    id: str
    title: str
    description: str
    type: RequirementType
    category: str
    priority: Priority
    dependencies: List[str]
    evidence_refs: List[EvidenceRef]
    subcategory: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class EvaluationCriteria:
    criterion: str
    evidence_refs: List[EvidenceRef]
    weight: Optional[str] = None
    notes: Optional[str] = None
    

@dataclass
class Stakeholder:
    name: Optional[str] = None
    role: Optional[str] = None
    team: Optional[str] = None


@dataclass
class DecisionProcess:
    stages: List[str]
    stakeholders: List[Stakeholder]
    evidence_refs: List[EvidenceRef]
    timeline: Optional[str] = None
    
    
@dataclass
class EvaluationAndSelection:
    evaluation_criteria: List[EvaluationCriteria]
    decision_process: List[DecisionProcess]


class SystemType(Enum):
    ERP = "erp"
    CRM = "crm"
    PLM = "plm"
    CAD = "cad"
    PIM = "pim"
    PRICING = "pricing"
    IDENTITY = "identity"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass
class System:
    system_name: str
    system_type: SystemType
    constraints: List[str]
    evidence_refs: List[EvidenceRef]
    notes: Optional[str] = None


@dataclass
class DataRequirement:
    data_item: str
    evidence_refs: List[EvidenceRef]
    purpose: Optional[str] = None
    format: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class IntegrationsAndData:
    systems: List[System]
    data_requirements: List[DataRequirement]


@dataclass
class SecurityCompliance:
    requirements: List[str]
    standards_certifications: List[str]
    privacy: List[str]
    access_control_identity: List[str]
    evidence_refs: List[EvidenceRef]
    data_residency: Optional[str] = None


@dataclass
class CommercialLegal:
    commercial_requirements: List[str]
    pricing_licensing_expectations: List[str]
    contract_terms: List[str]
    sla_support: List[str]
    procurement_process: List[str]
    evidence_refs: List[EvidenceRef]

@dataclass
class Milestone:
    milestone: str
    evidence_refs: List[EvidenceRef]
    date_or_window: Optional[str] = None

@dataclass
class DeliveryTimeline:
    milestones: List[Milestone]
    implementation_constraints: List[str]
    evidence_refs: List[EvidenceRef]

@dataclass
class ExplicitDemoOrPocRequest:
    scenario: str
    artifacts: List[str]
    constraints: List[str]
    expectations: List[str]
    evidence_refs: List[EvidenceRef]

@dataclass
class ExplicitDemoOrPocRequests:
    requested: bool
    requests: List[ExplicitDemoOrPocRequest]
    evidence_refs: List[EvidenceRef]


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class RiskUnknownsAmbiguity:
    item: str
    severity: Severity
    evidence_refs: List[EvidenceRef]
    why_it_matters: Optional[str] = None


@dataclass
class ClarificationQuestion:
    question: str
    priority: Severity  # Uses high/medium/low, not must/should/could
    evidence_refs: List[EvidenceRef]
    reason: Optional[str] = None


@dataclass
class KeyTermAcronym:
    term: str
    meaning: Optional[str] = None


@dataclass
class EntitiesGlossary:
    products: List[str]
    roles_personas: List[str]
    geographies: List[str]
    currencies: List[str]
    key_terms_acronyms: List[KeyTermAcronym]


@dataclass
class DealContext:
    dcm_version: str
    extraction_coverage: ExtractionCoverage
    document_metadata: DocumentMetadata
    customer_context: CustomerContext
    scope: Scope
    requirements: List[Requirement]
    evaluation_and_selection: EvaluationAndSelection
    integrations_and_data: IntegrationsAndData
    security_compliance: SecurityCompliance
    commercial_legal: CommercialLegal
    delivery_timeline: DeliveryTimeline
    explicit_demo_or_poc_requests: ExplicitDemoOrPocRequests
    risks_unknowns_ambiguities: List[RiskUnknownsAmbiguity]
    clarification_questions: List[ClarificationQuestion]
    entities_glossary: EntitiesGlossary
    @staticmethod
    def from_dict(data: dict) -> 'DealContext':
        return DealContext(**data)
