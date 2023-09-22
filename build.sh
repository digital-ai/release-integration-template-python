#!/bin/bash
# This script is used to build a zip and/or a docker image of a plugin.
# The script takes in one optional argument:
# --zip: build only the zip file
# --image: build only the docker image
# --upload: both the zip and image will be built and uploaded zip to the release server
# If no argument is passed, both the zip and image will be built

read_properties(){
  # Remove the tmp directory and create it again
  rm -rf tmp 2>/dev/null
  mkdir tmp 2>/dev/null

  # Remove all the carriage returns
  sed 's/\r$//' project.properties > tmp/project.properties

  # Read project properties from project.properties file and set them as variables
  . ./tmp/project.properties

  # Remove project.properties from tmp
  rm tmp/project.properties
}

build_zip(){

  # Copy the resources directory contents to tmp
  cp -R resources/. tmp/

  # Replace placeholders in type-definitions.xml/type-definitions.yaml & plugin-version.properties with values from project.properties
  if [ "$(uname)" = "Darwin" ]; then
    echo "Detected MAC OS X platform"

    sed -i '' 's/@project.name@/'"$PLUGIN"'/g' tmp/plugin-version.properties
    sed -i '' 's/@project.version@/'"$VERSION"'/g' tmp/plugin-version.properties
    if [ -s tmp/type-definitions.xml ]; then
      sed -i '' 's/@project.name@/'"$PLUGIN"'/g' tmp/type-definitions.xml
      sed -i '' 's/@project.version@/'"$VERSION"'/g' tmp/type-definitions.xml
      sed -i '' 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/type-definitions.xml
      sed -i '' 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/type-definitions.xml
    fi
    if [ -s tmp/type-definitions.yaml ]; then
      sed -i '' 's/@project.name@/'"$PLUGIN"'/g' tmp/type-definitions.yaml
      sed -i '' 's/@project.version@/'"$VERSION"'/g' tmp/type-definitions.yaml
      sed -i '' 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/type-definitions.yaml
      sed -i '' 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/type-definitions.yaml
    fi

  elif [ "$(expr substr $(uname -s) 1 5)" = "Linux" ]; then
    echo "Detected GNU/Linux platform"

    sed -i.bak 's/@project.name@/'"$PLUGIN"'/g' tmp/plugin-version.properties
    sed -i.bak 's/@project.version@/'"$VERSION"'/g' tmp/plugin-version.properties
    if [ -s tmp/type-definitions.xml ]; then
      sed -i.bak 's/@project.name@/'"$PLUGIN"'/g' tmp/type-definitions.xml
      sed -i.bak 's/@project.version@/'"$VERSION"'/g' tmp/type-definitions.xml
      sed -i.bak 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/type-definitions.xml
      sed -i.bak 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/type-definitions.xml
      rm tmp/type-definitions.xml.bak
    fi
    if [ -s tmp/type-definitions.yaml ]; then
      sed -i.bak 's/@project.name@/'"$PLUGIN"'/g' tmp/type-definitions.yaml
      sed -i.bak 's/@project.version@/'"$VERSION"'/g' tmp/type-definitions.yaml
      sed -i.bak 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/type-definitions.yaml
      sed -i.bak 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/type-definitions.yaml
      rm tmp/type-definitions.yaml.bak
    fi
    rm tmp/plugin-version.properties.bak
  fi

  # Create the build directory and remove any previously created zip file
  mkdir build 2>/dev/null
  rm -f "build/$PLUGIN-$VERSION.zip" 2>/dev/null

  # Create a zip file from the contents of the tmp directory and place it in the build directory
  cd tmp && zip -r "../build/$PLUGIN-$VERSION.zip" . && cd ..
  echo "Build completed: $PLUGIN-$VERSION.zip"
  # Remove the tmp directory
  rm -rf tmp
}

build_image(){
  # Build docker image and push to registry
  if docker build --tag "$REGISTRY_URL/$REGISTRY_ORG/$PLUGIN:$VERSION" .; then
    if docker image push "$REGISTRY_URL/$REGISTRY_ORG/$PLUGIN:$VERSION"; then
      echo "Build and push completed: $REGISTRY_URL/$REGISTRY_ORG/$PLUGIN:$VERSION"
    else
      echo "Push failed for $REGISTRY_URL/$REGISTRY_ORG/$PLUGIN:$VERSION"
    fi
  else
    echo "Build failed for $REGISTRY_URL/$REGISTRY_ORG/$PLUGIN:$VERSION"
  fi
}

upload_zip(){
  # upload the zip to the release server
  chmod +x ./xlw
  ./xlw plugin release install --file build/$PLUGIN-$VERSION.zip --config .xebialabs/config.yaml
}

if [ "$1" = "--zip" ]; then
  echo "Building zip..."
  read_properties
  build_zip
elif [ "$1" = "--image" ]; then
  echo "Building image..."
  read_properties
  build_image
elif [ "$1" = "--upload" ]; then
  echo "Building zip, image and Uploading zip..."
  read_properties
  build_zip
  build_image
  upload_zip
else
  echo "Building zip and image..."
  read_properties
  build_zip
  build_image
fi
