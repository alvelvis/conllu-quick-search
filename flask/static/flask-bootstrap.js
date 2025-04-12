const textarea = document.querySelector('#inputText')
const highlightLabels = document.querySelector('#highlight-labels')

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
