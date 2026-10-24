"""Tests for FastAPI endpoints."""

def test_learner_lifecycle(client):
    # 1. Create learner
    create_res = client.post("/api/v1/learners", json={"display_alias": "Test Star"})
    assert create_res.status_code == 201
    learner = create_res.json()
    assert learner["display_alias"] == "Test Star"
    assert learner["id"].startswith("mq_")

    # 2. Get profile
    get_res = client.get(f"/api/v1/learners/{learner['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == learner["id"]

    # 3. Get stats
    stats_res = client.get(f"/api/v1/learners/{learner['id']}/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["total_questions_answered"] == 0


def test_session_and_question_flow(client):
    # Create learner
    learner = client.post("/api/v1/learners", json={}).json()
    learner_id = learner["id"]

    # Start session
    session = client.post(
        "/api/v1/sessions",
        json={"learner_id": learner_id, "game_mode": "adaptive"},
    ).json()
    session_id = session["id"]

    # Fetch next question
    q_res = client.get(f"/api/v1/questions/next?learner_id={learner_id}&session_id={session_id}")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert "question_id" in q_data
    assert "question_text" in q_data
    # Crucial security check: correct_answer must NOT be exposed in the question response!
    assert "correct_answer" not in q_data

    # Submit an answer
    chosen_opt = q_data["options"][0] if q_data["options"] else "0"
    ans_res = client.post(
        "/api/v1/questions/answer",
        json={
            "learner_id": learner_id,
            "question_id": q_data["question_id"],
            "session_id": session_id,
            "submitted_answer": chosen_opt,
            "response_time_ms": 4200,
        },
    )
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert "is_correct" in ans_data
    assert "new_mastery_score" in ans_data

    # End session
    end_res = client.post(f"/api/v1/sessions/{session_id}/end")
    assert end_res.status_code == 200
    end_data = end_res.json()
    assert end_data["total_questions"] == 1
