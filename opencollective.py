# Helper functions to access Open Collective's API

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

def get_client(personal_token: str or None = None):
    """
    Constructs a GraphQL Client object which can connect to Open Collective's API.
    :param personal_token:
    A personal token to use for authentication.
    """
    if personal_token:
        transport = AIOHTTPTransport('https://api.opencollective.com/graphql/v2', headers={'Personal-Token': personal_token})
    else:
        raise NotImplementedError('OAuth is not implemented. Please supply a personal token.')
    client = Client(transport=transport)
    return client

def get_active_backers(client: Client, org:str = 'getsolus') -> list:
    """
    Retrieves active backers for an Open Collective organization using OC's GraphQL API.
    :param org:
    The slug for an Open Collective organization (defaults to "getsolus").
    :param client:
    A GraphQL Client object. See this module's "get_client" function.
    :return:
    A list of active backers for the given organization.
    """
    query = gql("""
query collective($slug: String, $limit: Int, $offset: Int) {
  collective(slug: $slug) {
    name
    slug
    contributors(roles: BACKER, limit: $limit, offset: $offset) {
      totalCount
      nodes {
        name
        description
        account {
          emails
        }
      }
    }
  }
}
    """)
    limit = 100
    offset = 0
    query.variable_values = {"slug": org, "limit": limit, "offset": offset}
    result = client.execute(query)
    backers = result['collective']['contributors']['nodes']
    while len(backers) < result['collective']['contributors']['totalCount']:
        offset += limit
        query.variable_values = {"slug": org, "limit": limit, "offset": offset}
        backers += client.execute(query)['collective']['contributors']['nodes']
    backers = [backer for backer in backers if backer["description"]]
    return backers

def filter_backers(backers: list, tier: str) -> list:
    """
    Filters a list of Open Collective backers based on their contribution tier.
    :param backers:
    The list of backers.
    :param tier:
    The tier name. Valid choices for a given organization may be acquired using this module's "get_tiers" function.
    """
    return [backer for backer in backers if backer["description"] == tier]

def get_tiers(client: Client, org:str = 'getsolus') -> list:
    """
    Retrieves a list of valid contribution tiers for a given Open Collective organization.
    :param client:
    A GraphQL Client object. See this module's "get_client" function.
    :param org:
    The slug for an Open Collective organization (defaults to "getsolus").
    """
    query = gql("""
query collective($slug: String) {
  collective(slug: $slug) {
    name
    slug
    tiers {
      totalCount
      nodes {
        name
      }
    }
  }
}
    """)
    query.variable_values = {"slug": org}
    result = client.execute(query)
    return [tier["name"] for tier in result["collective"]["tiers"]["nodes"]]