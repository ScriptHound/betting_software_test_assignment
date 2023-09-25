# kinda sophisticated i know, but this is for the sake of
# proper testing, read
# https://realpython.com/python-mock-library/#where-to-patch


class LineProviderClient:
    @staticmethod
    async def get_all_events_data_from_line_provider(http_client):
        response = await http_client.get("http://bsw_test_line_provider:8080/events")
        return response.json()


async def get_line_provider_client():
    return LineProviderClient
