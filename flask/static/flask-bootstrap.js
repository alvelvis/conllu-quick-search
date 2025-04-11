const textarea = document.querySelector('#inputText')

textarea.addEventListener('keydown', (e) => {
  if (e.keyCode === 9) {
    e.preventDefault()
    document.execCommand("insertText", false, "\t")
  }
})

textarea.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.keyCode === 13) {
    e.preventDefault()
    document.querySelector('#annotate').click()
  }
})