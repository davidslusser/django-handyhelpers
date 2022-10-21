const axios = require('axios')
const fs = require('fs')

const ISSUE_API = 'https://api.github.com/repos/wenzhixin/bootstrap-table/issues'
let issues = []

const fetchIssuesByPage = async page => {
  console.log(`start to fetch page ${page}`)
  const response = await axios.get(ISSUE_API, {
    params: {
      state: 'all',
      per_page: 100,
      page
    }
  })
  console.log(`fetched ${response.data.length} issues`)
  issues = issues.concat(response.data)
  if (response.data.length === 100) {
    fetchIssuesByPage(page + 1)
  } else {
    fs.writeFileSync('./issues.json', JSON.stringify(issues, null, 4))
  }
}

fetchIssuesByPage(1)
