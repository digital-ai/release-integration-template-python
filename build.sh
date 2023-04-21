#!/bin/bash
# This script is used to build a jar and/or a docker image of a plugin.
# The script takes in one optional argument:
# --jar: build only the jar file
# --image: build only the docker image
# If no argument is passed, both jar and image will be built.

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

build_jar(){

  # Copy the resources directory contents to tmp
  cp -R resources/. tmp/

  # Replace placeholders in synthetic.xml/type-definitions.yaml & plugin-version.properties with values from project.properties
  if [ "$(uname)" = "Darwin" ]; then
    echo "Detected MAC OS X platform"

    sed -i '' 's/@project.name@/'"$PLUGIN"'/g' tmp/plugin-version.properties
    sed -i '' 's/@project.version@/'"$VERSION"'/g' tmp/plugin-version.properties
    if [ -s tmp/synthetic.xml ]; then
      sed -i '' 's/@project.name@/'"$PLUGIN"'/g' tmp/synthetic.xml
      sed -i '' 's/@project.version@/'"$VERSION"'/g' tmp/synthetic.xml
      sed -i '' 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/synthetic.xml
      sed -i '' 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/synthetic.xml
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
    if [ -s tmp/synthetic.xml ]; then
      sed -i.bak 's/@project.name@/'"$PLUGIN"'/g' tmp/synthetic.xml
      sed -i.bak 's/@project.version@/'"$VERSION"'/g' tmp/synthetic.xml
      sed -i.bak 's/@registry.url@/'"$REGISTRY_URL"'/g' tmp/synthetic.xml
      sed -i.bak 's/@registry.org@/'"$REGISTRY_ORG"'/g' tmp/synthetic.xml
      rm tmp/synthetic.xml.bak
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

  # Create the build directory and remove any previously created jar file
  mkdir build 2>/dev/null
  rm -f "build/$PLUGIN-$VERSION.jar" 2>/dev/null

  # Create a jar file from the contents of the tmp directory and place it in the build directory
  cd tmp && zip -r "../build/$PLUGIN-$VERSION.jar" . && cd ..
  echo "Build completed: $PLUGIN-$VERSION.jar"
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

if [ "$1" = "--jar" ]; then
  echo "Building jar..."
  read_properties
  build_jar
elif [ "$1" = "--image" ]; then
  echo "Building image..."
  read_properties
  build_image
else
  echo "Building jar and image..."
  read_properties
  build_jar
  build_image
fi
