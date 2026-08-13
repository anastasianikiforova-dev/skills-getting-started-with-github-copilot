from fastapi import status


def test_root_redirects_to_static_index(client):
    # follow_redirects=False запрещает клиенту автоматически переходить по редиректу
    response = client.get("/", follow_redirects=False)
    
    # Проверяем код статуса редиректа (307 или 302/301)
    assert response.status_code in (301, 302, 307, 308)
    # Проверяем, что редирект ведет на static/index.html
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()

    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Chess Club"]["max_participants"] == 12
    assert payload["Programming Class"]["participants"] == [
        "emma@mergington.edu",
        "sophia@mergington.edu",
    ]


def test_signup_for_activity_adds_student(client):
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_student_from_activity(client):
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_student_not_signed_up(client):
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Student is not signed up for this activity"
