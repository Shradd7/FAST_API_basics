### Building and running your application

From the project directory, start the application with:

```powershell
docker compose up --build
```

The API will be available at http://localhost:8080 and its interactive docs at
http://localhost:8080/docs. Patient data is persisted in the `patient-data`
Docker volume.

Stop the application with:

```powershell
docker compose down
```

To also delete the persisted patient data, run `docker compose down --volumes`.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)
