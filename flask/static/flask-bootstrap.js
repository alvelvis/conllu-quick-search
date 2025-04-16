const textarea = document.querySelector('#inputText')
const highlightLabels = document.querySelector('#highlight-labels')
const clusterBy = document.querySelector('#cluster-by')
const maxResults = document.querySelector('#max-results')

function handleKeydown(e, element) {
  if (e.keyCode === 9) {
    e.preventDefault()
    document.execCommand("insertText", false, "\t")
  } else if (e.ctrlKey && e.keyCode === 13) {
    e.preventDefault()
    document.querySelector('#annotate').click()
  }
}

textarea.addEventListener('keydown', (e) => handleKeydown(e, textarea))
highlightLabels.addEventListener('keydown', (e) => handleKeydown(e, highlightLabels))
clusterBy.addEventListener('keydown', (e) => handleKeydown(e, clusterBy))
maxResults.addEventListener('keydown', (e) => handleKeydown(e, maxResults))
