# _Template Project for Digital.ai Release Integrations_

_This project serves as a template for developing a Python-based container plugin._

_See [How to create a new project](#how-to-create-a-new-project) below_

---

# Digital.ai Release integration to TARGET by PUBLISHER

⮕ Insert description here ⬅

---
## How to build and run

This section describes the quickest way to get a setup with Release to test containerized plugins using the SDK Development environment. For a production setup, please refer to the documentation. <!-- XXX insert link to documentation -->

### Prerequisites

You need to have the following installed in order to develop Python-based container tasks for Release using this project:

* Python 3
* Git
* Docker

### Start Release

We will run Release within a local Docker environment. In the development setup, the Release server will manage containerized tasks in Docker.

Start the Release environment with the following command

```commandline
cd dev-environment
docker compose up -d --build
```

### Configure your `hosts` file

The Release server needs to be able to find the container images of the integration you are creating. In order to do so the development setup has its own registry running inside Docker. Add the address of the registry to your local machine's `hosts` file.

**Unix / macOS**

Add the following entry to `/etc/hosts` (sudo privileges is required to edit):

    127.0.0.1 container-registry

**Windows**

Add the following entry to `C:\Windows\System32\drivers\etc\hosts` (Run as administrator permission is required to edit):

    127.0.0.1 container-registry


### Build & publish the plugin

Run the build script

**Unix / macOS**

```commandline
sh build.sh 
```

**Windows**

```commandline
build.bat 
```

This builds the jar and the container image and pushes the image to the configured registry.

### Install plugin into Release

In the Release UI, use the Plugin Manager interface to upload the jar from `build`.
The jar takes the name of the project, for example `release-integration-template-python-1.0.0.jar`.

Then:
* Restart Release container and wait for it to come up
* Refresh the UI by pressing Reload in the browser.

### 5. Test it!

Create a template with the task **Container Example: Hello** and run it!

### 6. Clean up

Stop the development environment with the following command:

    docker compose down

---

## How to create a new project

The  [release-integration-template-python](https://github.com/digital-ai/release-integration-template-python) repository is a template project.

On the main page of this repository, click **Use this template** button, and select **Create new repository**. This will create a duplicate of this project to start developing your own container-based integration. 

**Naming conventions**

Use the following naming convention for developing Digital.ai Release integration plugins:

    [publisher]-release-[target]-integration

Where publisher would be the name of your company.

For example:

    acme-release-example-integration

### Repository configuration

In the new project, update `project.properties` with the name of the integration plugin

```commandline
cd acme-release-example-integration
```

Change the following line in `project.properties`:

```
PLUGIN=acme-release-example-integration
...
```


