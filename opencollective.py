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
        transport = AIOHTTPTransport(
            "https://api.opencollective.com/graphql/v2",
            headers={"Personal-Token": personal_token},
        )
    else:
        raise NotImplementedError(
            "OAuth is not implemented. Please supply a personal token."
        )
    client = Client(transport=transport)
    return client


def get_active_backers(client: Client, org: str) -> list:
    """
    Retrieves active backers for an Open Collective organization using OC's GraphQL API.
    :param org:
    The slug for an Open Collective organization.
    :param client:
    A GraphQL Client object. See this module's "get_client" function.
    :return:
    A list of active backers for the given organization.
    """
    query = gql(
        """
query collective($slug: String, $limit: Int, $offset: Int) {
  collective(slug: $slug) {
    name
    slug
    contributors(roles: BACKER, limit: $limit, offset: $offset) {
      totalCount
      nodes {
        name
        account {
          emails
          type
          orders {
            totalCount
            nodes {
              status
              frequency
              tier {
                name
              }
              toAccount {
                slug
              }
            }
          }
        }
      }
    }
  }
}
    """
    )
    limit = 100
    offset = 0
    query.variable_values = {"slug": org, "limit": limit, "offset": offset}
    result = client.execute(query)
    backers = result["collective"]["contributors"]["nodes"]
    while len(backers) < result["collective"]["contributors"]["totalCount"]:
        offset += limit
        query.variable_values = {"slug": org, "limit": limit, "offset": offset}
        backers += client.execute(query)["collective"]["contributors"]["nodes"]
    output_backers = []
    for backer in backers:
        for order in backer["account"]["orders"]["nodes"]:
            if (
                order["status"] == "ACTIVE"
                and order["frequency"] == "MONTHLY"
                and order["toAccount"]["slug"] == org
            ):
                output_backers.append(backer)
                break
    return output_backers


def __test_backer_for_tier(backer: dict, tier: str) -> bool:
    """
    Tests an individual backer record to see if they are a member of the specified contribution tier.
    :param backer:
    An individual backer, as returned by this module's get_active_backers() function..
    :param tier:
    A contribution tier name. Valid choices for a given organization may be acquired using this module's "get_tiers" function.
    """
    output = False
    for order in backer["account"]["orders"]["nodes"]:
        if order["status"] == "ACTIVE" and order["tier"] and order["tier"]["name"] == tier:
            output = True
    return output


def filter_backers(backers: list, tiers: list[str]) -> list:
    """
    Filters a list of Open Collective backers based on their contribution tier.
    :param backers:
    The list of backers.
    :param tiers:
    A list of tier names to select. Valid choices for a given organization may be acquired using this module's "get_tiers" function.
    """
    output = []
    for tier in tiers:
        output += [backer for backer in backers if __test_backer_for_tier(backer, tier)]
    return output


def get_tiers(client: Client, org: str) -> list:
    """
    Retrieves a list of valid contribution tiers for a given Open Collective organization.
    :param client:
    A GraphQL Client object. See this module's "get_client" function.
    :param org:
    The slug for an Open Collective organization.
    """
    query = gql(
        """
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
    """
    )
    query.variable_values = {"slug": org}
    result = client.execute(query)
    return [tier["name"] for tier in result["collective"]["tiers"]["nodes"]]
