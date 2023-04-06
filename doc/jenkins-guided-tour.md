# Jenkins plugin guided tour
* _Jenkins project location_ : https://github.com/xebialabs/xlr-container-jenkins-integration

## How to define a Server in synthetic.xml

  ```xml
      <type type="ContainerJenkins.Server" extends="configuration.HttpConnection" description="Configure Jenkins Server.">
          <property name="apiToken" password="true" label="API Token" description="Username is required if using API Token" required="false"
                    category="Authentication"/>
          <property name="domain" default="empty" hidden="true"/>
          <property name="clientId" default="empty" hidden="true"/>
          <property name="clientSecret" default="empty" hidden="true" password="true"/>
          <property name="scope" default="empty" hidden="true"/>
          <property name="accessTokenUrl" default="empty" hidden="true"/>
          <property name="authenticationMethod" kind="enum"
                    enum-class="com.xebialabs.xlrelease.domain.configuration.HttpConnection$AuthenticationMethod"
                    hidden="true" default="Basic">
              <enum-values>
                  <value>Basic</value>
              </enum-values>
          </property>
          <property name="retryCount" kind="integer" category="Build" required="false" default="5"
                    description="Number of retries connection with jenkins"/>
          <property name="retryWaitingTime" kind="integer" category="Build" required="false" default="10"
                    description="Waiting time for retry in sec"/>
      </type>
  ```
* The given XML defines a type called **ContainerJenkins.Server** which extends the pre-defined type **configuration.HttpConnection**. This type is used for configuring a Jenkins server.
* Some of these properties are not relevant for Jenkins integration, and hence are **hidden** using the hidden attribute set to **true**.
* The properties that are hidden include domain, clientId, clientSecret, scope, accessTokenUrl, and authenticationMethod.
* The additional properties apiToken, retryCount and retryWaitingTime that are specific to Jenkins integration.
* Overall, this XML defines a type that can be used to configure a Jenkins server in XL Release, while hiding irrelevant fields inherited from **configuration.HttpConnection**.

## How to define a task in synthetic.xml

  ```xml
  <type type="ContainerJenkins.BaseTask" extends="xlrelease.ContainerTask" virtual="true">
      <property name="image" required="true" hidden="true" default="@registry.url@/@registry.org@/@project.name@:@project.version@" transient="true"/>
      <property name="iconLocation" default="jenkins.png" hidden="true"/>
      <property name="taskColor" hidden="true" default="#667385"/>
  </type>
  <type type="ContainerJenkins.JenkinsBuild" extends="ContainerJenkins.BaseTask" description="Configure Jenkins build.">
      <property name="jenkinsServer" category="input" label="Server" referenced-type="ContainerJenkins.Server" kind="ci" description="Jenkins server to connect to"/>
      <property name="jobName" category="input"
                description="Name of the job to trigger; this job must be configured on the Jenkins server"/>
      <property name="jobParameters" category="input" size="large" required="false"
                description="If the Jenkins job expects parameters, provide them here, delimited by ~~ (for example,  paramName1=value1~~paramName2=value2)"/>
      <property name="branch" category="input" description="Name of the branch (Mandatory for Multibranch Pipelines and ignored for others)"
                required="false"/>
      <property name="retryAttempt" category="output" kind="integer" required="false" default="0" description="Retry attempts for build queue status"/>
      <property name="buildNumber" category="output" required="false" description="Build number of the triggered job"/>
      <property name="buildStatus" category="output" required="false" description="Build status of the triggered job"/>
      <property name="jobUrl" category="output" required="false" description="Computed job url"/>
  </type>
  ```

## Explains JenkinsBuild class

* The **JenkinsBuild** class is a subclass of **BaseTask** and is responsible for launching and monitoring a Jenkins build job.
* **init(self, params)** initializes the class with the **params** dictionary passed to it. It sets several instance variables, including the Jenkins server URL, authentication credentials, and job parameters. It also sets default values for retry waiting time and maximum retry attempts.
* **execute(self)** method is the main method of the class. This method is an implementation of the abstract method **execute()** defined in the BaseTask class. It calls several other methods to handle the different stages of a Jenkins build job:
    * **handle_multibranch_job(self)** method checks if the job is a multibranch pipeline and sets the job URL accordingly.
    * **launch_build(self)** method launches the build with the given parameters or without parameters, as specified in the class instance. It sets a Jenkins crumb header and makes a POST request to the build URL. It also sets the **queue_url** instance variable and raises an exception if the build job is aborted.
    * **wait_for_build_start(self)** method waits for the build to start by checking the status of the build in the build queue. It retries for a maximum number of attempts if the build does not start, and sets the **build_number** instance variable if the build starts successfully. It also sets the **build_url** instance variable.
    * **check_queue_status(self)** method check the status of the build queue and return the build number if the build has started.
    * **wait_for_build_end(self)** method waits for the build to complete by checking the status of the build continuously until the build completes. It makes a GET request to the build URL to check the status, and waits for a few seconds between requests.
    * **handle_build_completion(self)** method handles the completion of the build by setting the build_status instance variable and logging the build status.
    * **handle_abort(self)** method handles the case when the build job is aborted. It sets the exit code to 1 and logs the message.
    * The **JenkinsBuild** class inherits several methods from the **BaseTask** abstract class, including **execute_task**, **get_output_context**, **get_output_properties**, **set_exit_code**, **set_error_message**, **add_comment**, **set_status_line**, and **add_reporting_record**. These methods are used to set and retrieve the output context, exit code, error message, comments, and reporting records of the task.

## How to use secrets and communicate with a third-party server
  ```python
    class JenkinsBuild(BaseTask):

    def __init__(self, params):
        super().__init__()
        self.params = params
        if not self.params['jenkinsServer']:
            raise ValueError("Server field cannot be empty")
        self.server = params['jenkinsServer']
        self.jenkins_url = self.server['url'].strip("/")
        self.auth = (
            self.server['username'], self.server['apiToken'] if self.server['apiToken'] else self.server['password'])
        self.job_name = params['jobName'].strip("/")
        self.job_params = params['jobParameters']
        self.job_branch = params['branch']
        self.retry_waiting_time = self.server['retryWaitingTime']
        self.max_retry_attempts = self.server['retryCount']
        self.job_url = self.prepare_job_url()
        self.headers = None

    def launch_build(self):
        if self.job_params:
            url = f"{self.jenkins_url}/job/{self.job_url}/buildWithParameters"
        else:
            url = f"{self.jenkins_url}/job/{self.job_url}/build"
        self.set_jenkins_crumb_header()
        response = requests.post(url, auth=self.auth, params=self.build_job_params(), headers=self.headers)
        response.raise_for_status()
  ```
* In above code snippet, designed to launch a Jenkins build by making a REST API call to a Jenkins server.
* The **__init__()** method is the class constructor, which initializes various instance variables using the params dictionary passed to the class constructor.
* The params dictionary contains the following keys:
    * **jenkinsServer**: A dictionary containing information about the Jenkins server, including its URL, username, password, and API token.
    * **jobName**: The name of the Jenkins job to be executed.
    * **jobParameters**: A dictionary of job parameters to be passed to the Jenkins job.
    * **branch**: The branch name for the job.
* The **launch_build()** method is used to actually launch the Jenkins build. It first constructs the URL for the Jenkins build based on the job_url, jenkins_url, and job_params instance variables. It then calls the set_jenkins_crumb_header() method to set a security crumb header, and makes a **POST** request to the Jenkins server using the **requests** library.

##  How to model a long-running task using Python3 constructs
  ```python
    def wait_for_build_start(self):
        for i in range(self.max_retry_attempts):
            build_number = self.check_queue_status()
            if build_number:
                self.build_number = build_number
                self.retry_attempts = i + 1
                break
            self.raise_exception_if_aborted()
            time.sleep(self.retry_waiting_time)
        else:
            raise Exception("Failed to determine queued build status and max number of retries reached.")
        self.build_url = f"{self.jenkins_url}/job/{self.job_url}/{self.build_number}"
        
  ```
* **wait_for_build_start** method that waits for a queued build to start. It does so by first checking the queue status and retrying a maximum number of times, waiting a set amount of time between each attempt.
* If the build starts within the maximum number of retries, the method sets the **build_number** and **build_url** attributes accordingly.
* If a build has not started, the method checks if it has been aborted by calling the **raise_exception_if_aborted** method, and if not, it waits a set amount of time before trying again, specified by the **retry_waiting_time** attribute.
* If the maximum number of retries is reached without the build starting, the method raises an exception indicating that it failed to determine the queued build status.

## How to do status line updates and task comments
  ```python
    def handle_build_completion(self):
        self.add_comment(f"Build is completed and build status is {self.build_status}")
        self.set_status_line(f"[Build #{self.build_number}]({self.build_url})")
        if self.build_status != 'SUCCESS':
            self.set_exit_code(1)
            self.set_error_message(f"Build status is {self.build_status}") 
  ```  
* The above code defines a method called **handle_build_completion** that handles the completion of a build.
* It does so by adding a comment to the build to indicate that it has completed and what its status was, setting the status line to indicate that the build has completed, and if the build status was not successful, setting the exit code to 1 and setting an error message.
