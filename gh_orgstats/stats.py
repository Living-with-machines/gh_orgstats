# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_stats.ipynb (unless otherwise specified).

__all__ = ['create_github_session', 'OrgStats', 'get_repos', 'repos', 'repo_count', 'public_repos', 'public_repo_count',
           'private_repos', 'private_repo_count', 'get_repo_files', 'get_org_files', 'files', 'files_public',
           'files_private', 'get_ext', 'get_repo_file_ext_frequency', 'get_org_file_ext_frequency',
           'get_org_snapshot_stats', 'snapshot_stats', 'get_repo_views_traffic', 'get_org_views_traffic', 'repos',
           'get_repo_clones_traffic', 'get_org_clones_traffic']

# Cell
import github
import pandas
from typing import Union, List, Optional, Generator, Dict, Iterable
import pathlib

# Cell
from dotenv import load_dotenv
from github import Github
import pandas as pd
import os
from fastcore.all import *
from pathlib import Path
from functools import lru_cache
from toolz import itertoolz

# Cell
def create_github_session(GH_TOKEN):
    """creates a session for GitHub"""
    global g
    g = Github(GH_TOKEN)
    return g

# Cell
class OrgStats:
    """Class for collecting GitHub statistics for an Organization"""
    def __init__(self, GH_TOKEN: str, org: str):
        """
        Parameters
        ----------
        GH_TOKEN : str
            `GH_TOKEN` is a GitHub access token with at least public repo scope.
            See https://github.com/settings/tokens
        org : str
            a Github Organization
        """
        self.__GH_TOKEN = GH_TOKEN
        self.gh_session = create_github_session(self.__GH_TOKEN)
        self.org = self._get_org(org)

    def __str__(self):
        return f"OrgStats: {self.org.name} "

    def __repr__(self):
        return self.__str__()

    def _get_org(self, org:'str'):
        return g.get_organization(org)

# Cell
@patch_to(OrgStats)
@lru_cache(maxsize=512)
def get_repos(self, pub_status: Union[None, str] = None) -> List[github.Repository.Repository]:
    """
    Returns repositories for organisaton
    optional `pub_status` filter for `public` or `private` repositories
    """
    org = self.org
    all_repos = [repo for repo in org.get_repos()]
    if pub_status:
        if pub_status == 'private':
            return list(filter(lambda x: x.private == True, all_repos))
        elif pub_status == 'public':
            return list(filter(lambda x: x.private == False, all_repos))
    return all_repos

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache(maxsize=128)
def repos(self):
    """all repositories of `org`"""
    return self.get_repos()

# Cell
@patch_to(OrgStats, as_prop=True)
def repo_count(self):
    """count of all repositories of `org`"""
    return len(self.get_repos())

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache(maxsize=128)
def public_repos(self):
    """public repositories of `org`"""
    return self.get_repos('public')

# Cell
@patch_to(OrgStats, as_prop=True)
def public_repo_count(self):
    """count of public repositories of `org`"""
    return len(self.get_repos('public'))

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache(maxsize=128)
def private_repos(self):
    """private repositories of `org`"""
    return self.get_repos('private')

# Cell
@patch_to(OrgStats, as_prop=True)
def private_repo_count(self):
    """count of private repositories of `org`"""
    return len(self.get_repos('private'))

# Cell
@patch_to(OrgStats)
def get_repo_files(self, repo: Union[str, github.Repository.Repository]) -> Generator[github.ContentFile.ContentFile, None, None]:
    """return files for `repo`"""
    files = []
    if type(repo) == str:
        repo = self.org.get_repo(repo)
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            yield file_content

# Cell
@patch_to(OrgStats)
@lru_cache(maxsize=512)
def get_org_files(self, pub_status: Union[None, str]=None) -> Dict[str, List[github.ContentFile.ContentFile]]:
    """returns repo files for `org`"""
    org_files = {}
    if pub_status:
        if pub_status == 'private':
            for repo in self.private_repos:
                org_files[repo.name] = list(self.get_repo_files(repo))
        elif pub_status == 'public':
            for repo in self.public_repos:
                org_files[repo.name] = list(self.get_repo_files(repo))
    else:
        for repo in self.repos:
            org_files[repo.name] = list(self.get_repo_files(repo))
    return org_files

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache(maxsize=256)
def files(self):
    """files for all repos"""
    return self.get_org_files(pub_status='private')

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache()
def files_public(self):
    """files for public repos"""
    return self.get_org_files(pub_status='public')

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache()
def files_private(self):
    """files for private repos"""
    return self.get_org_files(pub_status='private')

# Cell
def get_ext(x): return Path(x).suffix

# Cell
def _get_ext_freqs(files:Generator[github.ContentFile.ContentFile,None,None]) -> Dict[str,int]:
    """Returns frequencies of file extension in `files`"""
    file_list = [file.name for file in files]
    return itertoolz.frequencies(filter(lambda x: x!='',map(get_ext,file_list)))

# Cell
@patch_to(OrgStats)
def get_repo_file_ext_frequency(self, repo: Union[str, github.Repository.Repository]) -> Dict[str,int]:
    """returns frequencies of file extensions for `repo` """
    files = self.get_repo_files(repo)
    return _get_ext_freqs(files)

# Cell
@patch_to(OrgStats)
def get_org_file_ext_frequency(self, pub_status: Union[None, str] = None) ->Dict[str, Dict[str,int]]:
    """returns frequencies of file extensions for repos in `OrgStats` `org` """
    return {k: _get_ext_freqs(v) for k,v in self.get_org_files(pub_status).items()}

# Cell
@patch_to(OrgStats)
def get_org_snapshot_stats(self, repos: Iterable[github.Repository.Repository]) -> Dict[str,Dict[str,int]]:
    """Returns dictionary of star and fork counts for `repos`"""
    repos_stats = {}
    for repo in repos:
        stats = {'stars': repo.get_stargazers().totalCount}
        stats['forks'] = repo.get_forks().totalCount
        repos_stats[repo.name] = stats
    return repos_stats

# Cell
@patch_to(OrgStats, as_prop=True)
@lru_cache(maxsize=256)
def snapshot_stats(self) -> pd.DataFrame:
    """Returns a Pandas DataFrame of star and fork counts for public repos"""
    return pd.DataFrame.from_dict(self.get_org_snapshot_stats(self.public_repos), orient='index')

# Cell
@patch_to(OrgStats)
def get_repo_views_traffic(self, repo: Union[str,github.Repository.Repository], save_dir:Union[str, pathlib.Path]='view_data', load=False) -> pd.DataFrame:
    """gets views traffic for `repo` and saves as csv in `save_dir`

    Parameters
    ----------
    repo : Union[str,github.Repository.Repository]
        repository from `org`
    save_dir : Union[str, pathlib.Path], optional
        directory where output CSV should be saved, by default 'view_data'
    load : bool, optional
        load data into a Pandas DataFrame, by default False

    Returns
    -------
    pd.DataFrame
        contains unique and total views for `repo` with dates
    """
    if type(repo) == str:
        repo = self.org.get_repo(repo)
    traffic = repo.get_views_traffic()
    traffic_dict = {
        view.timestamp: {
            "total_views": view.count,
            "unique_views": view.uniques,
        }
        for view in traffic['views']
    }

    try:
        old_traffic_data = pd.read_csv(f'{save_dir}/{repo.name}_views_traffic.csv', index_col="_date", parse_dates=["_date"]).to_dict(orient="index")
        updated_dict = {**old_traffic_data, **traffic_dict}
        traffic_frame = pd.DataFrame.from_dict(data=updated_dict, orient="index", columns=["total_views", "unique_views"])
    except:
        traffic_frame = pd.DataFrame.from_dict(data=traffic_dict, orient="index", columns=["total_views", "unique_views"])
    traffic_frame.index.name = "_date"
    if not Path(save_dir).exists():
        Path(save_dir).mkdir()
    traffic_frame.to_csv(f'{save_dir}/{repo.name}_views_traffic.csv')
    if load:
        return traffic_frame

# Cell
@patch_to(OrgStats)
def get_org_views_traffic(self, public_only:bool=True, save_dir:Union[str,pathlib.Path]='view_data',
repos:Optional[Iterable[github.Repository.Repository]]=None, load=False) -> Union[None, pd.DataFrame]:
    """Get view traffic for multiple repos from `Org`

    Parameters
    ----------
    public_only : bool, optional
        only get stats for public repos, by default True
    save_dir : Union[str,pathlib.Path], optional
        directory where csvs of stats should be saved, by default 'view_data'
    repos : Optional[Iterable[github.Repository.Repository]], optional
        to access stats for a specific set of repos, by default None
    load : bool, optional
        whether to load views data into a DataFrame, by default False

    Returns
    -------
    Union[None, pd.DataFrame]
    """
    if public_only and not repos:
        repos = self.public_repos
    dfs = []
    for repo in repos:
        df = self.get_repo_views_traffic(repo, save_dir,load)
        dfs.append(df)
    if load:
        org_traffic = {}
        for repo, df in zip(repos,dfs):
            repo_views_traffic_dict = df.to_dict()
            repo_name = repo.name
            org_traffic[repo_name] = repo_views_traffic_dict
        return pd.DataFrame.from_dict(
            {
                (i, j): org_traffic[i][j]
                for i in org_traffic
                for j in org_traffic[i].keys()
            }
        )

# Cell
@patch_to(OrgStats)
def get_repo_clones_traffic(self, repo: github.Repository.Repository,
                            save_dir:Union[str, pathlib.Path]='clones_data', load=False):
    """gets clones traffic for `repo` and saves as csv in `save_dir`

    Parameters
    ----------
    repo : Union[str,github.Repository.Repository]
        repository from `org`
    save_dir : Union[str, pathlib.Path], optional
        directory where output CSV should be saved, by default 'view_data'
    load : bool, optional
        load data into a Pandas DataFrame, by default False

    Returns
    -------
    pd.DataFrame
        contains unique and total clones for `repo` with dates
    """
    if type(repo) == str:
        repo = self.org.get_repo(repo)
    clones = repo.get_clones_traffic()
    clones_dict = {
        view.timestamp: {
            "total_clones": view.count,
            "unique_clones": view.uniques,
        }
        for view in clones['clones']
    }

    try:
        old_clones_data = pd.read_csv(f'clones_data/{repo.name}_clones_traffic.csv', index_col="_date", parse_dates=["_date"]).to_dict(orient="index")
        updated_clones_dict = {**old_clones_data, **clones_dict}
        clones_frame = pd.DataFrame.from_dict(data=updated_clones_dict, orient="index", columns=["total_clones", "unique_clones"])
    except:
        clones_frame = pd.DataFrame.from_dict(data=clones_dict, orient="index", columns=["total_clones", "unique_clones"])
    clones_frame.index.name = "_date"
    if not Path(save_dir).exists():
        Path(save_dir).mkdir()
    clones_frame.to_csv(f'{save_dir}/{repo.name}_clones_traffic.csv')
    if load:
        return clones_frame

# Cell
@patch_to(OrgStats)
def get_org_clones_traffic(self, public_only:bool = True, repos: Optional[Iterable[github.Repository.Repository]] = None,
                           save_dir:Union[str,pathlib.Path]='clones_data', load=False) -> Union[None,pd.DataFrame]:
    """get clone traffic for multiple repos from `Org`

    Parameters
    ----------
    public_only : bool, optional
        only get stats for public repos, by default True
    save_dir : Union[str,pathlib.Path], optional
        directory where csvs of stats should be saved, by default 'view_data'
    repos : Optional[Iterable[github.Repository.Repository]], optional
        to access stats for a specific set of repos, by default None
    load : bool, optional
        whether to load views data into a DataFrame, by default False

    Returns
    -------
    Union[None, pd.DataFrame]
    """
    if public_only and not repos:
            repos = self.public_repos
    dfs = []
    for repo in repos:
        df = self.get_repo_clones_traffic(repo, save_dir,load)
        dfs.append(df)
    if load:
        clones_traffic = {}
        for repo, df in zip(repos,dfs):
            repo_clones_traffic_dict = df.to_dict()
            repo_name = repo.name
            clones_traffic[repo_name] = repo_clones_traffic_dict
        return pd.DataFrame.from_dict(
            {
                (i, j): clones_traffic[i][j]
                for i in clones_traffic
                for j in clones_traffic[i].keys()
            }
        )