@echo off
:: This script is used to build a jar and/or a docker image of a plugin.
:: The script takes in one optional argument:
:: --jar: build only the jar file
:: --image: build only the docker image
:: If no argument is passed, both jar and image will be built.

if "%1" == "--jar" (
    echo Building jar...
    call :read_properties
    call :build_jar
) else if "%1" == "--image" (
    echo Building image...
    call :read_properties
    call :build_image
) else (
    echo Building jar and image...
    call :read_properties
    call :build_jar
    call :build_image
)
goto :eof

:read_properties
    :: Read project properties from project.properties file and set them as variables
    for /f "tokens=1,2 delims==" %%G in (project.properties) do (set %%G=%%H)
goto :eof

:build_jar
    :: Remove the tmp directory and create it again
    rd /S /Q tmp 2>nul
    mkdir tmp 2>nul

    :: Copy the resources directory contents to tmp
    xcopy /E /I resources tmp

    :: Replace placeholders in synthetic.xml with values from project.properties
    if exist "tmp\synthetic.xml" (
        (for /f "delims=" %%i in (tmp\synthetic.xml) do (
            set "line=%%i"
            setlocal enabledelayedexpansion
            set "line=!line:@project.name@=%PLUGIN%!"
            set "line=!line:@project.version@=%VERSION%!"
            set "line=!line:@registry.url@=%REGISTRY_URL%!"
            set "line=!line:@registry.org@=%REGISTRY_ORG%!"
            echo(!line!
            endlocal
        ))>"tmp\synthetic.xml.bak"
        move tmp\synthetic.xml.bak tmp\synthetic.xml
    )

    :: Replace placeholders in type-definitions.yaml with values from project.properties
    if exist "tmp\type-definitions.yaml" (
        (for /f "delims=" %%i in (tmp\type-definitions.yaml) do (
            set "line=%%i"
            setlocal enabledelayedexpansion
            set "line=!line:@project.name@=%PLUGIN%!"
            set "line=!line:@project.version@=%VERSION%!"
            set "line=!line:@registry.url@=%REGISTRY_URL%!"
            set "line=!line:@registry.org@=%REGISTRY_ORG%!"
            echo(!line!
            endlocal
        ))>"tmp\type-definitions.yaml.bak"
        move tmp\type-definitions.yaml.bak tmp\type-definitions.yaml
    )

    :: Replace placeholders in plugin-version.properties with values from project.properties
    (for /f "delims=" %%i in (tmp\plugin-version.properties) do (
        set "line=%%i"
        setlocal enabledelayedexpansion
        set "line=!line:@project.name@=%PLUGIN%!"
        set "line=!line:@project.version@=%VERSION%!"
        echo(!line!
        endlocal
    ))>"tmp\plugin-version.properties.bak"
    move tmp\plugin-version.properties.bak tmp\plugin-version.properties

    :: Create the build directory and remove any previously created jar file
    mkdir build 2>nul
    del "build\%PLUGIN%-%VERSION%.jar" 2>nul

    :: Create a jar file from the contents of the tmp directory and place it in the build directory
    powershell Compress-Archive -Path tmp\* -DestinationPath build\%PLUGIN%-%VERSION%.zip
    move build\%PLUGIN%-%VERSION%.zip build\%PLUGIN%-%VERSION%.jar
    echo Build completed: %PLUGIN%-%VERSION%.jar

    :: Remove the tmp directory
    rd /S /Q tmp
goto :eof

:build_image
:: Build docker image and push to registry
    call docker build --tag "%REGISTRY_URL%/%REGISTRY_ORG%/%PLUGIN%:%VERSION%" .
    if errorlevel 1 (
      echo Build failed for %REGISTRY_URL%/%REGISTRY_ORG%/%PLUGIN%:%VERSION%
      goto :eof
    )
    call docker image push "%REGISTRY_URL%/%REGISTRY_ORG%/%PLUGIN%:%VERSION%" && (
      echo Build and push completed: %REGISTRY_URL%/%REGISTRY_ORG%/%PLUGIN%:%VERSION%
    ) || (
      echo Push failed for %REGISTRY_URL%/%REGISTRY_ORG%/%PLUGIN%:%VERSION%
    )
goto :eof
