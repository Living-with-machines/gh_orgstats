# Github OrgStats



```python
![CI](https://github.com/Living-with-machines/gh_orgstats/workflows/CI/badge.svg)
```

`ghOrgReport` is intended to provide some easy ways of getting stats for a GitHub org. `ghOrgReport` does this by wrapping some functions around [PyGithub](https://github.com/PyGithub/PyGithub). This code is mainly intended to help generate reports as part of a GitHub actions pipeline to update stats for a funder. \#TODO add link to lwm report

To use `PyGithub` we need to authenticate with GitHub this is done via a token. This token is used to authenticate access and requires at least scope for public repos. See https://github.com/settings/tokens to register a token. 

```python
from dotenv import load_dotenv
import os
```

In this case we use `dotenv` to load the token from a `.env` files. 

```python
load_dotenv()
GH_TOKEN = os.getenv("GH_TOKEN")
```

Currently all functionality is contained within the `stats` module. 

```python
from gh_orgstats.stats import *
```

The `OrgStats` class is used to get stats for a GitHub organization. To create an instance of this class we need to pass a GitHub token to authenticate and the name of the Organization you want stats for. 

```python
test_org = OrgStats(GH_TOKEN, "ghorgstatstestorg")
test_org
```




    OrgStats: ghorgstatstestorg 



### Organization repositories 
As a start we can grab the repositories for an organization via the `repos` attribute of our OrgStats instance

```python
test_org.repos
```




    [Repository(full_name="ghorgstatstestorg/repo1"),
     Repository(full_name="ghorgstatstestorg/repo2"),
     Repository(full_name="ghorgstatstestorg/private_repo_1")]



We can also get a sense of what is in the repository by looking at the file extensions for each repository. 

### Repository file types

```python
test_org.get_org_file_ext_frequency()
```




    {'repo1': {'.md': 1},
     'repo2': {'.md': 1, '.py': 1},
     'private_repo_1': {'.md': 1}}



#### Filtering by publication status 

We can also filter this by publication status

```python
test_org.get_org_file_ext_frequency(pub_status='public')
```




    {'repo1': {'.md': 1}, 'repo2': {'.md': 1, '.py': 1}}



### Snapshot stats
Snapshot stats are captured based on the current view and aren't updated. These include forks and clones

```python
test_org.snapshot_stats
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>stars</th>
      <th>forks</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>repo1</th>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>repo2</th>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



### Traffic stats
We can also get a longer view by using traffic stats for views and clones

```python
test_org.get_org_views_traffic(save_dir='readme_dir')
```

`get_org_views_traffic` will grab data via the GitHub api and update a CSV for each repository under the organization (by default only public) with views counts. This is largely intended to be used to semi-regularly update these stats by running this code as part of a GitHub Action or cron job.


If you want to load a DataFrame of traffic you can pass `load=True`

```python
test_org.get_org_views_traffic(save_dir='readme_dir', load=True).to_markdown()
```




    "|                     |   ('repo1', 'total_views') |   ('repo1', 'unique_views') |   ('repo2', 'total_views') |   ('repo2', 'unique_views') |\n|:--------------------|---------------------------:|----------------------------:|---------------------------:|----------------------------:|\n| 2020-11-30 00:00:00 |                          2 |                           1 |                          8 |                           1 |\n| 2020-12-01 00:00:00 |                          1 |                           1 |                        nan |                         nan |"



Similarly the same can be done for clones

```python
test_org.get_org_clones_traffic(save_dir='readme_dir', load=True)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="2" halign="left">repo1</th>
      <th colspan="2" halign="left">repo2</th>
    </tr>
    <tr>
      <th></th>
      <th>total_clones</th>
      <th>unique_clones</th>
      <th>total_clones</th>
      <th>unique_clones</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2020-11-30</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>3</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>


