from src.views.bets.schemas import EventState


async def test_get_all_bettable_events_view(async_http_client, mock_line_provider):
    response = await async_http_client.get("/events/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "event_id": "1",
            "coefficient": 1.2,
            "deadline": 1600,
            "state": EventState.NEW.value,
        },
        {
            "event_id": "2",
            "coefficient": 1.15,
            "deadline": 1060,
            "state": EventState.NEW.value,
        },
        {
            "event_id": "3",
            "coefficient": 1.67,
            "deadline": 1090,
            "state": EventState.NEW.value,
        },
    ]


async def test_make_a_bet_on_event(
    async_http_client, async_testing_session, mock_line_provider, mock_database_session
):
    data = {
        "event_id": "1",
        "amount": "100.00",
    }
    response = await async_http_client.post("/bet/", json=data)
    jsonified_response = response.json()
    assert response.status_code == 201
    assert jsonified_response == {"bet_id": 1}


async def test_get_bets_history_view(
    async_http_client,
    async_testing_session,
    mock_line_provider,
    mock_database_session,
    bets_fixture,
):
    expected_json = [
        {"id": 1, "event_id": "1", "amount": 100.0, "status": 1},
        {"id": 2, "event_id": "2", "amount": 100.0, "status": 1},
        {"id": 3, "event_id": "3", "amount": 100.0, "status": 1},
        {"id": 4, "event_id": "4", "amount": 100.0, "status": 3},
    ]
    response = await async_http_client.get("/bets/")
    jsonified_response = response.json()
    assert jsonified_response == expected_json
