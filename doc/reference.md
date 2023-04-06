# Digital.ai SDK Reference 

This documents describes the technical details of an Digital.ai Release integration project.

## Digital.ai Release SDK Project

This sample project is based on the SDK base defined here:

https://github.com/xebialabs/xlr-container-python-sdk

The SDK is available for testing at test.pypi.org:

https://test.pypi.org/project/digitalai

## Build & publish the plugin

Run the build script

Unix/macOS

* Builds the jar, image and pushes the image to the configured registry  
  ``` sh build.sh ```
* Builds the jar  
  ``` sh build.sh --jar ```
* Builds the image and pushes the image to the configured registry  
  ```  sh build.sh --image ```

Windows

* Builds the jar, image and pushes the image to the configured registry  
  ``` build.bat ```
* Builds the jar  
  ``` build.bat --jar ```
* Builds the image and pushes the image to the configured registry  
  ``` build.bat --image ```

## Publishing to a different registry

