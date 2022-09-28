Release new version

## bootstrap-table

* Update CHANGELOG.md
* Create PR from develop to master and reviewed the changed
* Run `./release.sh <version>`
* Update released tag: https://github.com/wenzhixin/bootstrap-table/releases

## bootstrap-table-examples

1. update version and create PR from develop to master
2. merged PR
3. `cd tools && node algolia.js && node data.js`

## bootstrap-table-live

1. update `src/constants.js` and add version
2. `cd static && ./deploy.sh`
