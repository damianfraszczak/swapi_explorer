# swapi_explorer

It is Start Wars data browser utilizing [https://swapi.dev/](SWAPI) to load data.

Currently it only supports browsing star wars characters.

## Features

- It utilize asyncio and aiohttp to load remote data.
- It uses petl to do some ETL tasks.
- It provides two modes to import data, it is to show how big datasets can be handled. SWAPI API returns people data in
  pages and currently there are just 82 records, so it is not a problem to download all data and then do sth with them
  but for big datasets it is not efficient so two modes are implemented:
    - Fetch all and then does ETL.
    - Fetch page and then ETL on each page separately.
- It utilize aiocache to cache API requests results.

## TODO

- Implement sync data fetching to show difference between sync vs async data collecting.
- Add unit tests
- Improve error handling
- Prepare squash.io deployment

## How to run
To run application with Docker you need it installed and configured, please see [this](https://docs.docker.com/engine/install/) for a reference.
Then execute the following commands:
1. Go into `docker` directory with `cd docker`.
2. `docker-compose build`
3. `docker-compose up`
4. Open browser too see [http://localhost:8000](http://localhost:8000).


## Pre-commit Hooks

This project supports [**pre-commit**](https://pre-commit.com/). To use it please install it
in the `pip install pre-commit` and then run `pre-commit install` and you are ready to go.
Bunch of checks will be executed before commit and files will be formatted correctly.

Pre-commit works on staged files while commiting. To run it without a command one should run `pre-commit run`. Changes has to be staged.

To run pre-commit hooks on all changes in the branch:

1.  Sync branch with main
1.  Run `git diff --name-only --diff-filter=MA origin/main | xargs pre-commit run --files`

For branches that are not based on `main` you might replace `origin/main` with `origin/{your_branch}`
