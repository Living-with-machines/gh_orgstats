# Github OrgStats



![CI](https://github.com/Living-with-machines/gh_orgstats/workflows/CI/badge.svg)

`gh_orgstats` is intended to provide some easy ways of getting stats for a GitHub org. `gh_orgstats` does this by wrapping some functions around [PyGithub](https://github.com/PyGithub/PyGithub). This code is mainly intended to help generate reports as part of a GitHub actions pipeline to update stats for a funder. \ # TODO add link to lwm report
 \ # TODO add install instructions 

To use `PyGithub` we need to authenticate with GitHub this is done via a token. This token is used to authenticate access and requires at least scope for public repos. See https://github.com/settings/tokens to register a token. 

```
from dotenv import load_dotenv
import os
```

In this case we use `dotenv` to load the token from a `.env` files. 

```
load_dotenv()
GH_TOKEN = os.getenv("GH_TOKEN")
```

Currently all functionality is contained within the `stats` module. 

```
from gh_orgstats.stats import *
```

The `OrgStats` class is used to get stats for a GitHub organization. To create an instance of this class we need to pass a GitHub token to authenticate and the name of the Organization you want stats for. 

```
test_org = OrgStats(GH_TOKEN, "ghorgstatstestorg")
test_org
```




    OrgStats: ghorgstatstestorg 



### Organization repositories 
As a start we can grab the repositories for an organization via the `repos` attribute of our OrgStats instance

```
test_org.repos
```




    [Repository(full_name="ghorgstatstestorg/repo1"),
     Repository(full_name="ghorgstatstestorg/repo2"),
     Repository(full_name="ghorgstatstestorg/private_repo_1")]



We can also get a sense of what is in the repository by looking at the file extensions for each repository. 

### Repository file types

```
test_org.get_org_file_ext_frequency()
```




    {'repo1': {'.md': 1},
     'repo2': {'.md': 1, '.py': 1},
     'private_repo_1': {'.md': 1}}



#### Filtering by publication status 

We can also filter this by publication status

```
test_org.get_org_file_ext_frequency(pub_status='public')
```




    {'repo1': {'.md': 1}, 'repo2': {'.md': 1, '.py': 1}}



### Snapshot stats
Snapshot stats are captured based on the current view and aren't updated. These include forks and clones

```
test_org.snapshot_stats.to_dict()
```




    {'stars': {'repo1': 1, 'repo2': 0}, 'forks': {'repo1': 0, 'repo2': 0}}



### Traffic stats
We can also get a longer view by using traffic stats for views and clones

```
test_org.get_org_views_traffic(save_dir='readme_dir')
```

`get_org_views_traffic` will grab data via the GitHub api and update a CSV for each repository under the organization (by default only public) with views counts. This is largely intended to be used to semi-regularly update these stats by running this code as part of a GitHub Action or cron job.


If you want to load a DataFrame of traffic you can pass `load=True`

```
test_org.get_org_views_traffic(save_dir='readme_dir', load=True).to_dict()
```




    {('repo1', 'total_views'): {Timestamp('2020-11-30 00:00:00'): 2,
      Timestamp('2020-12-01 00:00:00'): 1},
     ('repo1', 'unique_views'): {Timestamp('2020-11-30 00:00:00'): 1,
      Timestamp('2020-12-01 00:00:00'): 1},
     ('repo2', 'total_views'): {Timestamp('2020-11-30 00:00:00'): 8.0,
      Timestamp('2020-12-01 00:00:00'): nan},
     ('repo2', 'unique_views'): {Timestamp('2020-11-30 00:00:00'): 1.0,
      Timestamp('2020-12-01 00:00:00'): nan}}



Similarly the same can be done for clones
