"""
Mapper to convert DealContextDTO (Pydantic) to DealContext (Domain Entity).
Follows Clean Architecture: Infrastructure → Domain conversion.
"""
from ....domain.deal_analyzer.entities.deal_context import (
    DealContext, ExtractionCoverage, DocumentMetadata, CustomerContext,
    Scope, Requirement, EvaluationAndSelection, IntegrationsAndData,
    SecurityCompliance, CommercialLegal, DeliveryTimeline,
    ExplicitDemoOrPocRequests, RiskUnknownsAmbiguity, ClarificationQuestion,
    EntitiesGlossary, EvidenceRef, Contact, SubmissionInstructions,
    EvaluationCriteria, Stakeholder, DecisionProcess, System, DataRequirement,
    Milestone, ExplicitDemoOrPocRequest, KeyTermAcronym,
    RequirementType, Priority, SystemType, Severity
)
from ..models.deal_context_dto import DealContextDTO


class DealContextMapper:
    """Maps DealContextDTO (Pydantic) to DealContext (Domain)"""

    @staticmethod
    def to_domain(dto: DealContextDTO) -> DealContext:
        """Convert DTO to Domain entity"""
        return DealContext(
            dcm_version=dto.dcm_version,
            extraction_coverage=ExtractionCoverage(
                processed=dto.extraction_coverage.processed,
                warnings=dto.extraction_coverage.warnings,
                sections_detected=dto.extraction_coverage.sections_detected,
                sections_low_confidence=dto.extraction_coverage.sections_low_confidence,
            ),
            document_metadata=DocumentMetadata(
                rfx_type=dto.document_metadata.rfx_type,
                contacts=[
                    Contact(
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in contact.evidence_refs
                        ],
                        name=contact.name,
                        role=contact.role,
                        email=contact.email,
                        phone=contact.phone,
                    )
                    for contact in dto.document_metadata.contacts
                ],
                submission_instructions=SubmissionInstructions(
                    evidence_refs=[
                        EvidenceRef(
                            chunk_id=ref.chunk_id,
                            section=ref.section,
                            quote=ref.quote,
                            confidence=ref.confidence,
                        )
                        for ref in dto.document_metadata.submission_instructions.evidence_refs
                    ],
                    method=dto.document_metadata.submission_instructions.method,
                    format=dto.document_metadata.submission_instructions.format,
                    portal_link=dto.document_metadata.submission_instructions.portal_link,
                    qa_process=dto.document_metadata.submission_instructions.qa_process,
                ),
                title=dto.document_metadata.title,
                customer_name=dto.document_metadata.customer_name,
                issuing_org=dto.document_metadata.issuing_org,
                document_date=dto.document_metadata.document_date,
                revision=dto.document_metadata.revision,
                confidentiality=dto.document_metadata.confidentiality,
                submission_deadline=dto.document_metadata.submission_deadline,
            ),
            customer_context=CustomerContext(
                regions_markets=dto.customer_context.regions_markets,
                current_state=dto.customer_context.current_state,
                # Map business_drivers to business_problems (LLM returns business_drivers)
                business_problems=dto.customer_context.business_drivers or dto.customer_context.business_problems,
                key_pain_points=dto.customer_context.key_pain_points,
                success_definition=dto.customer_context.success_definition,
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.customer_context.evidence_refs
                ],
                industry=dto.customer_context.industry,
                customer_profile_summary=dto.customer_context.customer_profile_summary,
            ),
            scope=Scope(
                in_scope=dto.scope.in_scope,
                out_of_scope=dto.scope.out_of_scope,
                assumptions_stated_by_customer=dto.scope.assumptions_stated_by_customer,
                constraints_global=dto.scope.constraints_global,
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.scope.evidence_refs
                ],
            ),
            requirements=[
                Requirement(
                    id=req.id,
                    title=req.title,
                    description=req.description,
                    type=RequirementType(req.type.value),
                    category=req.category,
                    priority=Priority(req.priority.value),
                    dependencies=req.dependencies,
                    evidence_refs=[
                        EvidenceRef(
                            chunk_id=ref.chunk_id,
                            section=ref.section,
                            quote=ref.quote,
                            confidence=ref.confidence,
                        )
                        for ref in req.evidence_refs
                    ],
                    subcategory=req.subcategory,
                    acceptance_criteria=req.acceptance_criteria,
                    notes=req.notes,
                )
                for req in dto.requirements
            ],
            evaluation_and_selection=EvaluationAndSelection(
                evaluation_criteria=[
                    EvaluationCriteria(
                        criterion=crit.criterion,
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in crit.evidence_refs
                        ],
                        weight=crit.weight,
                        notes=crit.notes,
                    )
                    for crit in dto.evaluation_and_selection.evaluation_criteria
                ],
                decision_process=[
                    DecisionProcess(
                        stages=dto.evaluation_and_selection.decision_process.stages,
                        stakeholders=[
                            Stakeholder(
                                name=sh.name,
                                role=sh.role,
                                team=sh.team,
                            )
                            for sh in dto.evaluation_and_selection.decision_process.stakeholders
                        ],
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in dto.evaluation_and_selection.decision_process.evidence_refs
                        ],
                        timeline=dto.evaluation_and_selection.decision_process.timeline,
                    )
                ],
            ),
            integrations_and_data=IntegrationsAndData(
                systems=[
                    System(
                        system_name=sys.system_name,
                        system_type=SystemType(sys.system_type.value),
                        constraints=sys.constraints,
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in sys.evidence_refs
                        ],
                        notes=sys.notes,
                    )
                    for sys in dto.integrations_and_data.systems
                ],
                data_requirements=[
                    DataRequirement(
                        data_item=dr.data_item,
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in dr.evidence_refs
                        ],
                        purpose=dr.purpose,
                        format=dr.format,
                        source=dr.source,
                        notes=dr.notes,
                    )
                    for dr in dto.integrations_and_data.data_requirements
                ],
            ),
            security_compliance=SecurityCompliance(
                requirements=dto.security_compliance.requirements,
                standards_certifications=dto.security_compliance.standards_certifications,
                privacy=dto.security_compliance.privacy,
                access_control_identity=dto.security_compliance.access_control_identity,
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.security_compliance.evidence_refs
                ],
                data_residency=dto.security_compliance.data_residency,
            ),
            commercial_legal=CommercialLegal(
                commercial_requirements=dto.commercial_legal.commercial_requirements,
                pricing_licensing_expectations=dto.commercial_legal.pricing_licensing_expectations,
                contract_terms=dto.commercial_legal.contract_terms,
                sla_support=dto.commercial_legal.sla_support,
                procurement_process=dto.commercial_legal.procurement_process,
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.commercial_legal.evidence_refs
                ],
            ),
            delivery_timeline=DeliveryTimeline(
                milestones=[
                    Milestone(
                        milestone=m.milestone,
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in m.evidence_refs
                        ],
                        date_or_window=m.date_or_window,
                    )
                    for m in dto.delivery_timeline.milestones
                ],
                implementation_constraints=dto.delivery_timeline.implementation_constraints,
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.delivery_timeline.evidence_refs
                ],
            ),
            explicit_demo_or_poc_requests=ExplicitDemoOrPocRequests(
                requested=dto.explicit_demo_or_poc_requests.requested,
                # Map 'scenarios' (LLM) to 'requests' (Domain)
                requests=[
                    ExplicitDemoOrPocRequest(
                        scenario=req.scenario or req.title or "",
                        artifacts=req.artifacts,
                        constraints=req.constraints,
                        expectations=req.expectations,
                        evidence_refs=[
                            EvidenceRef(
                                chunk_id=ref.chunk_id,
                                section=ref.section,
                                quote=ref.quote,
                                confidence=ref.confidence,
                            )
                            for ref in req.evidence_refs
                        ],
                    )
                    for req in (dto.explicit_demo_or_poc_requests.scenarios or dto.explicit_demo_or_poc_requests.requests)
                ],
                evidence_refs=[
                    EvidenceRef(
                        chunk_id=ref.chunk_id,
                        section=ref.section,
                        quote=ref.quote,
                        confidence=ref.confidence,
                    )
                    for ref in dto.explicit_demo_or_poc_requests.evidence_refs
                ],
            ),
            risks_unknowns_ambiguities=[
                RiskUnknownsAmbiguity(
                    item=risk.item,
                    severity=Severity(risk.severity.value),
                    evidence_refs=[
                        EvidenceRef(
                            chunk_id=ref.chunk_id,
                            section=ref.section,
                            quote=ref.quote,
                            confidence=ref.confidence,
                        )
                        for ref in risk.evidence_refs
                    ],
                    why_it_matters=risk.why_it_matters,
                )
                for risk in dto.risks_unknowns_ambiguities
            ],
            clarification_questions=[
                ClarificationQuestion(
                    question=q.question,
                    priority=Severity(q.priority.value),  # Map SeverityEnum to Severity
                    evidence_refs=[
                        EvidenceRef(
                            chunk_id=ref.chunk_id,
                            section=ref.section,
                            quote=ref.quote,
                            confidence=ref.confidence,
                        )
                        for ref in q.evidence_refs
                    ],
                    reason=q.reason,
                )
                for q in dto.clarification_questions
            ],
            entities_glossary=EntitiesGlossary(
                products=dto.entities_glossary.products,
                roles_personas=dto.entities_glossary.roles_personas,
                geographies=dto.entities_glossary.geographies,
                currencies=dto.entities_glossary.currencies,
                key_terms_acronyms=[
                    KeyTermAcronym(
                        term=kta.term,
                        meaning=kta.meaning,
                    )
                    for kta in dto.entities_glossary.key_terms_acronyms
                ],
            ),
        )

