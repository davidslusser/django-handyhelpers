#!/bin/bash

if [ "$DEBUG" == "1" ]; then
  set -x
fi

set -e

target_version=$1
current_version=`node -e "console.log(require('./package').version)"`
version_start=`echo $current_version | cut -d '.' -f 1-2`

echo "Current version: $current_version"

build_docs () {
  # target version not start with current version
  if [[ ! $1 == $version_start* ]]; then
    echo "Building docs: $current_version"
    git checkout master
    git pull --rebase
    yarn docs
    mv _gh_pages $current_version
    git checkout gh-pages
    git pull --rebase
    mv $current_version versions/
    git add versions/$current_version
    git commit -m "Add $current_version"
    git push
  fi
}

update_version () {
  echo "Updating version: $target_version"
  git checkout develop
  git pull --rebase
  node tools/release.js $target_version
}

build_dist () {
  echo "Building dist"
  yarn build
  git add dist
  git commit -a -m "Build $target_version"
  git push
}

merge_develop () {
  echo "Merging develop to master"
  git checkout master
  git pull --rebase
  git merge develop
  git push -u origin master
}

add_tag () {
  echo "Adding tag: $target_version"
  git tag $target_version
  git push --tags
}

npm_publish () {
  echo "NPM publishing"
  npm publish --registry=https://registry.npmjs.org
}

update_algolia_and_live () {
  echo "Updating algolia and bootstrap-table-live"
  ALGOLIA_API_KEY='94b423a877c9386f44876be39c7ace24' bundle exec jekyll algolia

  cd tools
  node get-extensions-list.js
  cd ..
}

# build_docs
# update_version
# build_dist
# merge_develop
# add_tag
npm_publish
update_algolia_and_live
