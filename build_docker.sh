#!/bin/bash
IMAGENAME="schoolnotebookbase"
REPO_URL="ghcr.io"
REPO_USER="tna76874"

# Überprüfen, ob ungecommitete Änderungen vorhanden sind
if [[ -n $(git status -s) ]]; then
  echo "Es gibt ungecommitete Änderungen im Repository. Bitte committen oder stashen Sie Ihre Änderungen, bevor Sie das Skript ausführen."
  exit 1
fi

# Git-Hash des HEAD abrufen
GIT_HASH=$(git rev-parse HEAD)
current_branch=$(git symbolic-ref --short HEAD 2>/dev/null)

# Überprüfen, ob der Branch "master" ist
if [[ $current_branch == "master" ]]; then
  channel="latest"
else
  channel=$current_branch
fi

docker build --file Dockerfile_build -t $REPO_URL/$REPO_USER/$IMAGENAME:$channel .
docker build --file Dockerfile_build -t $REPO_URL/$REPO_USER/$IMAGENAME:$GIT_HASH .