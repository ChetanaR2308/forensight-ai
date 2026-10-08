from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.deps import get_current_user
from app.container import get_container
from app.models.domain import Evidence, ProcessingStatus, User
from app.models.schemas import EvidenceUploadResponse, IntegrityCheckResponse, TimelineResponse
from app.services.access import ensure_case_access

router = APIRouter(prefix="/cases/{case_id}/evidence", tags=["evidence"])


@router.get("")
def list_case_evidence(case_id: str, user: User = Depends(get_current_user)) -> list[Evidence]:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)
    return repository.list_case_evidence(case_id)


@router.post("", response_model=EvidenceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> EvidenceUploadResponse:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    evidence = Evidence(
        case_id=case_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=0,
        sha256="",
        storage_path="",
        uploaded_by=user.id,
    )

    try:
        storage_path, size_bytes, sha256 = await get_container().storage.save_upload(case_id, evidence.id, file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    evidence.storage_path = storage_path
    evidence.size_bytes = size_bytes
    evidence.sha256 = sha256

    metadata, observations = get_container().pipeline.process(case_id, evidence.id, storage_path)
    evidence.metadata = metadata
    evidence.processing_status = ProcessingStatus.processed

    repository.add_evidence(evidence)
    for observation in observations:
        repository.add_observation(observation)

    get_container().vector.upsert(case_id, observations)
    get_container().audit.log(
        user.id,
        "evidence.upload",
        case_id=case_id,
        evidence_id=evidence.id,
        details={"filename": file.filename, "sha256": sha256, "size_bytes": size_bytes},
    )

    return EvidenceUploadResponse(evidence=evidence, observations=observations)


@router.get("/{evidence_id}/integrity", response_model=IntegrityCheckResponse)
def verify_integrity(case_id: str, evidence_id: str, user: User = Depends(get_current_user)) -> IntegrityCheckResponse:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    evidence = repository.get_evidence(evidence_id)
    if not evidence or evidence.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")

    actual_sha256 = get_container().storage.compute_sha256(evidence.storage_path)
    matches = actual_sha256 == evidence.sha256
    return IntegrityCheckResponse(
        evidence_id=evidence_id,
        expected_sha256=evidence.sha256,
        actual_sha256=actual_sha256,
        matches=matches,
    )


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(case_id: str, user: User = Depends(get_current_user)) -> TimelineResponse:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    observations = repository.list_case_observations(case_id)
    events = get_container().timeline.build_timeline(case_id, observations)
    return TimelineResponse(case_id=case_id, events=events)
