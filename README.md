# Watchlist
*A self-hosted watchlist app*

> **NOTE:**  The project is still in early development.

Watchlist is a full rewrite of the watchlist feature from a previous hobby project. This time it’s being built as a standalone application from the ground up, applying lessons learned to improve structure, maintainability, and overall design.

![Alpha preview of the homepage](/images/home_page.png)

> [!TIP]
> **Want to see more?** Check out the full list of screenshots [here](SCREENSHOTS.md).


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

Detailed setup instructions for the frontend and backend can be found in their respective `README.md` files. After initial setup, you can start both servers together using the VS Code task **Start Full Stack** to start the servers at once (`Ctrl + Shift + P` -> `Tasks: Run tasks` -> `Start Full Stack`). 

For the database, it’s recommended to run a local PostgreSQL server and connect the backend to it.


## Deployment

The project will be deployable via Docker. Once implemented docker images will be published to GHCR.


## License

This project is licensed under the [AGPL-3.0](LICENSE). See the LICENSE file for details.
