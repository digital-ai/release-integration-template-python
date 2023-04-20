# Template Project for Digital.ai Release Integrations

This project serves as a template for developing a Python-based container plugin.

## Prerequisites

You need to have the following installed in order to develop Python-based container tasks for Release using this project:

* Python 3
* Git
* Docker

For a quick check of your environment, run the [Quickstart](#quickstart) on this template repository.


## How to create your own project

This repo is a template project, meaning you shouldn't make changes to it.
Create a **duplicate** of this project to start developing your own container-based integration. 

Note: Please do _not_ create a fork.

### Create a new repository

Before you duplicate the contents of this repository, you already need a new repository to push to.

Use the following naming convention:

    [company]-release-[target]-integration

For example: `acme-release-jenkins-integration`

Now initialize the Git repository with this name and note the url.  
**⚠️ NOTE:**  Default branch name has to be `main`

* Instructions to [create a repository on GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)


### Clone and duplicate

1. Open Terminal.
2. Create a bare clone of the template repository.

**HTTPS:**

```commandline
git clone --bare https://github.com/digital-ai/release-integration-template-python.git release-integration-temp
```

**SSH:**

```commandline
git clone --bare git@github.com:digital-ai/release-integration-template-python.git release-integration-temp
```

3. Mirror-push to the new repository.

```commandline
cd release-integration-temp
git push --mirror [URL of your new repo]
```

4. Remove the temporary local repository you created earlier.

```commandline
cd ..
rm -rf release-integration-temp
```

5. In your new project, update `project.properties` with the name of the integration plugin

```commandline
cd acme-release-example-integration
```

Change the following line in `project.properties`:

```
PLUGIN=acme-release-example-integration
...
```

For instructions to set up the project with a Python virtual environment and an IDE, refer to XXX

## Quickstart

This section describes the quickest way to get a setup with Release to test containerized plugins. This is not a production setup. For production, please use the [Remote Runner](doc/remote-runner-quickstart.md) to run container tasks.

### 1. Start Release

We will run Release within a local Docker environment. In the development setup, the Release server will manage containerized tasks in Docker. For production, you would use the Remote Runner inside Kubernetes to manage that.

Start the Release environment with the following command

```commandline
cd dev-environment
docker compose up -d --build
```

### 2. Configure your `hosts` file

The Release server needs to be able to find the container images of the integration you are creating. In order to do so the development setup has its own registry running inside Docker. Add the address of the registry to your local machine's `hosts` file.

**Unix / macOS**

Add the following entry to `/etc/hosts` (sudo privileges is required to edit):

    127.0.0.1 container-registry

**Windows**

Add the following entry to `C:\Windows\System32\drivers\etc\hosts` (Run as administrator permission is required to edit):

    127.0.0.1 container-registry


### 3. Build & publish the plugin

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

### 4. Install plugin into Release

In Release UI, use the Plugin Manager interface to upload the jar from `build`.
The jar takes the name of the project, for example `release-integration-template-python-1.0.0.jar`.

Then:
* Restart Release container and wait for it to come up
* Refresh the UI by pressing Reload in the browser.

### 5. Test it!
Create a template with the task **Example: Hello** and run it!

_XXX Expand_

### 6. Clean up

Stop the development environment with the following command:

    docker compose down
