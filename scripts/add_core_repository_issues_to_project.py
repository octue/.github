import os
import requests


pat = os.environ.get("PERSONAL_ACCESS_TOKEN_GITHUB")
headers = {"Authorization": pat if pat.startswith("token ") else f"token {pat}"}


CORE_REPOSITORIES = [
    ".github",
    "amy",
    "amy-fibres",
    "amy-ui",
    "conventional-commits",
    "django-twined",
    "octue-sdk-python",
    "octue-sdk-cpp",
    "octue-sdk-fortran",
    "octue-sdk-matlab",
    "planex-site",
    "twined",
    "twined-frontend",
    "twined-server",
    "twined-ui",
]


def run_query(query, is_mutation=False):
    """Use requests.post to make a GitHub API call
    :param string query: The graphQL query
    :return dict: The json response from the API
    """
    request = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
    if request.status_code >= 300:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    else:
        return request.json()


# All mutations available here: https://docs.github.com/en/graphql/reference/mutations#addprojectnextitem


def get_project_id_from_number(project_number, project_owner):
    """Get the id of a projectNext project
    :param int project_number: The number of the projectNext (aka Projects: Beta) project
    :return str: The id of that project
    """
    base_query = """
{
  organization(login: "PROJECT_OWNER") {
    projectNext(number: PROJECT_NUMBER) {
      id
    }
  }
}
"""
    query = base_query.replace("PROJECT_OWNER", project_owner).replace("PROJECT_NUMBER", str(project_number))
    results = run_query(query)
    return results["data"]["organization"]["projectNext"]["id"]


def get_all_repository_issues(repository_name, repository_owner):

    base_query = """
{
  repository(name: "REPOSITORY_NAME", owner: "REPOSITORY_OWNER") {
    id
    name
    issues(after: ISSUES_CURSOR, first: 100) {
      nodes {
        id
        number
        closed
        title
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""
    issues_accumulator = []
    issues_has_next_page = True
    issues_cursor = "null"
    while issues_has_next_page:
        query = (
            base_query.replace("REPOSITORY_NAME", repository_name)
            .replace("REPOSITORY_OWNER", repository_owner)
            .replace("ISSUES_CURSOR", issues_cursor)
        )

        result = run_query(query)
        issues = result["data"]["repository"]["issues"]
        issues_accumulator += issues["nodes"]

        issues_has_next_page = bool(issues["pageInfo"]["hasNextPage"])
        issues_cursor = f'"{issues["pageInfo"]["endCursor"]}"'

        print(repository_name, issues_has_next_page, issues_cursor)

    return issues_accumulator


def addIssueToProject(project_id, issue_id):
    """Runs a mutation to add a project next item"""
    base_query = """
mutation AddProjectNextItem {
  addProjectNextItem(input: {projectId: "PROJECT_ID", contentId: "CONTENT_ID"}) {
    clientMutationId
    projectNextItem {
      id
    }
  }
}
"""
    query = base_query.replace("CONTENT_ID", issue_id).replace("PROJECT_ID", project_id)
    return run_query(query, is_mutation=True)


if __name__ == "__main__":

    # TODO easy to make this a CLI
    project_number = 22
    owner = "octue"
    repo_names = CORE_REPOSITORIES

    project_id = get_project_id_from_number(project_number, owner)
    for repo_name in repo_names:
        issues = get_all_repository_issues(repo_name, owner)
        print(f"Adding {len(issues)} in repository {repo_name} to project {project_number} ({project_id})")
        for issue in issues:
            if not issue["closed"]:
                addIssueToProject(project_id=project_id, issue_id=issue["id"])
