"""Tests for the My Story submission and listing endpoints, including moderation filters."""

from app.models.asset import Asset

def test_unauthenticated_story_submission_rejected(client):
    payload = {
        "description": "Growing up in Ekiti during the 90s.",
        "rights_status": "owned",
        "folder": "EKITI30/Stories"
    }
    response = client.post("/api/stories/", json=payload)
    assert response.status_code in [401, 403, 503]

def test_authenticated_story_submission_success(client, contributor_headers):
    payload = {
        "description": "My first day at school in Ado.",
        "rights_status": "owned",
        "folder": "EKITI30/Stories",
        "source": "Family archive",
        "location_lga": "Ado-Ekiti"
    }
    response = client.post("/api/stories/", json=payload, headers=contributor_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["folder"] == "EKITI30/Stories"
    assert data["contributor"] is not None

def test_get_stories_returns_only_approved(client, db_session):
    # Insert assets with different statuses and folders
    approved_story = Asset(
        folder="EKITI30/Stories",
        description="Approved story test",
        rights_status="owned",
        contributor="Test User",
        status="approved"
    )
    pending_story = Asset(
        folder="EKITI30/Stories",
        description="Pending story test",
        rights_status="owned",
        contributor="Test User",
        status="pending"
    )
    rejected_story = Asset(
        folder="EKITI30/Stories",
        description="Rejected story test",
        rights_status="owned",
        contributor="Test User",
        status="rejected"
    )
    other_folder_approved = Asset(
        folder="EKITI30/Historical",
        description="Other folder approved",
        rights_status="owned",
        contributor="Test User",
        status="approved"
    )
    
    db_session.add_all([approved_story, pending_story, rejected_story, other_folder_approved])
    db_session.commit()

    response = client.get("/api/stories/")
    assert response.status_code == 200
    stories = response.json()
    
    # Only the approved story in "EKITI30/Stories" should be returned
    descriptions = [s["description"] for s in stories]
    assert "Approved story test" in descriptions
    assert "Pending story test" not in descriptions
    assert "Rejected story test" not in descriptions
    assert "Other folder approved" not in descriptions

def test_get_stories_empty_when_none_approved(client):
    response = client.get("/api/stories/")
    assert response.status_code == 200
    assert response.json() == []
