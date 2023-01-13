const submitBtn = document.querySelector("#submit-btn")
const inputText = document.querySelector("#input-text")
const inputFile = document.querySelector('#input-file')
let imageUrl
let inputTextContent

submitBtn.addEventListener("click", () => {
  uploadFile()

  async function uploadFile() {
    const message = inputText.value
    const image = inputFile.files[0]

    let formData = new FormData()
    formData.append("message", message)
    formData.append("file", image)

    const response = await fetch("/api/file", {
      method: "POST",
      body: formData
    })
    const jsonData = await response.json()
    imageUrl = jsonData.data[0]
    inputTextContent = jsonData.data[1]
    loadPost(inputTextContent, imageUrl)
  }
})

displayMessageImage()

async function displayMessageImage() {
  const response = await fetch("/api/file", {
    method: "GET"
  })
  const jsonData = await response.json()
  jsonData.data.forEach((value) => {
    imageUrl = value[0]
    inputTextContent = value[1]

    loadPost(inputTextContent, imageUrl)
  })
}


function loadPost(msg, img) {
  const messageImageBox = document.querySelector(".message-image-box")

  const messageImage = document.createElement("div")
  messageImage.classList.add("message-image")

  const message = document.createElement("div")
  message.classList.add("message")
  message.innerText = msg

  const image = document.createElement("img")
  image.classList.add("image")
  image.src = img

  messageImage.appendChild(message)
  messageImage.appendChild(image)
  messageImageBox.appendChild(messageImage)

  inputText.value = ""
  inputFile.value = ""
}


