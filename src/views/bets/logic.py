async def get_all_events_data_from_line_provider(http_client):
    response = await http_client.get("http://bsw-test-line-provider:8000/events/")
    return response.json()
