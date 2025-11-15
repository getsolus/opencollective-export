# Helper functions to access Open Collective's API

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

def get_client(personal_token: str or None = None):
    if personal_token:
        transport = AIOHTTPTransport('https://api.opencollective.com/graphql/v2', headers={'Personal-Token': personal_token})
    else:
        raise NotImplementedError('OAuth is not implemented. Please supply a personal token.')
    client = Client(transport=transport)
    return client

def get_backers(client: Client, org:str = 'getsolus') -> None:
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
    print(result['collective']['contributors']['totalCount'])
    print(len(backers))
    for backer in backers:
        print(backer['name'], backer['description'], backer['account']['emails'])