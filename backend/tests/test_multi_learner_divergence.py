"""Integration tests demonstrating multi-learner adaptive path divergence.

Proves that two independent learners with different performance histories
receive legitimate, differentiated learning paths and difficulty levels.
"""

from backend.app.db.models import ConceptMastery, QuestionLog


def test_two_learners_experience_differentiated_paths(client, db_session):
    # 1. Create two anonymous learners
    res_a = client.post("/api/v1/learners", json={"display_alias": "Advanced Alex"}).json()
    res_b = client.post("/api/v1/learners", json={"display_alias": "Struggling Sam"}).json()
    id_a = res_a["id"]
    id_b = res_b["id"]

    # 2. Simulate Learner A: high mastery across addition facts
    mastery_a = ConceptMastery(
        learner_id=id_a,
        topic_id="add_sub",
        concept_id="add_single_digit",
        mastery_score=0.92,
        confidence=0.85,
        attempts_count=8,
        correct_count=8,
        consecutive_correct=4,
        consecutive_incorrect=0,
    )
    # Learner A also has basic subtraction mastered
    mastery_a_sub = ConceptMastery(
        learner_id=id_a,
        topic_id="add_sub",
        concept_id="sub_single_digit",
        mastery_score=0.88,
        confidence=0.80,
        attempts_count=6,
        correct_count=6,
        consecutive_correct=3,
        consecutive_incorrect=0,
    )
    db_session.add_all([mastery_a, mastery_a_sub])

    # Simulate Learner B: low mastery, struggling with addition facts
    mastery_b = ConceptMastery(
        learner_id=id_b,
        topic_id="add_sub",
        concept_id="add_single_digit",
        mastery_score=0.30,
        confidence=0.70,
        attempts_count=5,
        correct_count=1,
        consecutive_correct=0,
        consecutive_incorrect=2,
    )
    db_session.add(mastery_b)
    db_session.commit()

    # 3. Fetch next question for both learners
    q_a = client.get(f"/api/v1/questions/next?learner_id={id_a}").json()
    q_b = client.get(f"/api/v1/questions/next?learner_id={id_b}").json()

    # 4. Verify divergence!
    # Learner A has mastered single digit addition & subtraction, so engine advances them
    # to multi-digit addition/subtraction or times tables, with higher difficulty.
    # Learner B is struggling with foundational addition (mastery 0.30, 2 incorrect),
    # so engine keeps them on foundational addition at lowest difficulty level.

    assert q_b["concept_id"] == "add_single_digit", "Struggling learner must remain on foundational concept"
    assert q_b["difficulty"] == 1, "Struggling learner must receive foundational difficulty 1"

    # Learner A should either be on higher difficulty or advanced concept
    assert (
        q_a["concept_id"] != q_b["concept_id"] or q_a["difficulty"] > q_b["difficulty"]
    ), f"Learner paths must diverge! A: {q_a['concept_id']} (diff {q_a['difficulty']}) vs B: {q_b['concept_id']} (diff {q_b['difficulty']})"

    assert "recommendation_reason" in q_a
    assert "recommendation_reason" in q_b
