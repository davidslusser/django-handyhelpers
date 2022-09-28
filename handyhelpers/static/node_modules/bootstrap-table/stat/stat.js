const issues = require('./issues.json')

const closedIssues = issues.filter(issue => {
  return issue.state === 'closed' && !issue.pull_request
})

const lastClosedIssues = closedIssues.filter(issue => {
  return issue.closed_at > '2019-10-09' && issue.closed_at < '2020-02-12'
})

console.log(lastClosedIssues.length)

const closedPullRequests = issues.filter(issue => {
  return issue.state === 'closed' && issue.pull_request
})

const lastClosedPullRequests = closedPullRequests.filter(issue => {
  return issue.closed_at > '2019-10-09' && issue.closed_at < '2020-02-12'
})

console.log(lastClosedPullRequests.length)
