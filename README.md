# Watchlist

*A self-hosted watchlist app*

> **NOTE:**  The project is still in early development.

Watchlist is a full rewrite of the watchlist feature from a previous hobby project. This time it’s being built as a standalone application from the ground up, applying lessons learned to improve structure, maintainability, and overall design.

![Alpha preview of the homepage](/docs/assets/home_page.png)

> [!TIP]
> **Want to see more?** Check out the full list of screenshots [here](/docs/SCREENSHOTS.md).


## Planned key features

- Sleak mobile and desktop UI
- Rich metadata from TMDB and other sources
- Watch count tracking
- Personal library management
    - Custom collections
    - Favourites
    - Watchlist
- Comprehensive search tools
- Fully local, user-owned data


## Local development

Detailed setup instructions for the frontend and backend can be found in their respective `README.md` files. For the database, it’s recommended to run a local PostgreSQL instance.

After initial setup, you can start both servers together using the VS Code task **Watchlist Dev: all** to start the servers at once (`Ctrl + Shift + P` -> `Tasks: Run tasks` -> `Watchlist Dev: all`). 


## Deployment

The project can be easily deployed via Docker. Use the provided [`docker-compose.yml`](docker-compose.yml) and [`.env.sample`](.env.sample) as your base. 

1. Copy both files onto your host environment.
2. Rename `.env.sample` to `.env` and fill in your credentials.
3. Adjust the `docker-compose.yml` to fit your needs, then spin it up with:

```bash
docker compose up -d
```

If you are new to Docker and Docker Compose, you can learn more about how it works [here](https://docs.docker.com/compose).


## License

This project is licensed under the [AGPL-3.0](LICENSE). See the LICENSE file for details.
