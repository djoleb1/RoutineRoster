
const showMoreBtn = document.getElementById('show-more-btn')

function delete_post(id) {
    const post_id = id
    const postCard = document.getElementById(id)
    postCard.remove()

    fetch("/delete_post", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ post_id: post_id }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not OK");
        }
        return response.json();
    })
    .then(data => {
        console.log(data)
    })
    .catch(error => {
        console.error('Error deleting post:', error);
    })
}

showMoreBtn.addEventListener('click', function() {
    fetch('/show_more_trainers', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const trainersContainer = document.getElementById('trainersContainer');
        data.trainers.forEach(trainer => {
                
                // creating elements for each trainer card
                const trainerCard = document.createElement('div');
                trainerCard.classList.add('trainer-card');
                trainerCard.innerHTML = `
                <div class="image-container">
                    <img src="/static/${trainer.profile_picture}" alt="Profile picture" class="home-follow-image">
                </div>
                <div class="main-follow-handles">
                    <h6 class="card-title"><b>${trainer.full_name}</b></h6>
                    <p>@${trainer.username}</p>
                </div>
                <form action="/home" method="post" class="acc-form">
                    <input type="hidden" name="id" value="${trainer.id}">
                    <button type="submit" class="btn home-follow-btn">Follow</button>
                </form>
                `

            // appending the constructed trainer card to the trainersContainer
            trainersContainer.appendChild(trainerCard);
            });          

        }).catch(error => {
            console.error('Error fetching trainers:', error)
        })
    showMoreBtn.remove()
})

document.getElementById("postForm").addEventListener("submit", function(event) {

    event.preventDefault()
    const mainPage = document.getElementById('main-content')
    const mainPosts = document.getElementById('main-posts')
    const content = document.getElementById('content').value;
    
    
    fetch("/create_post", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: content }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not OK");
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        const newPostElement = document.createElement('div');
        newPostElement.classList.add("card");
        newPostElement.classList.add("home-trainer-post");
        newPostElement.setAttribute("id", data.id);

        newPostElement.innerHTML = `
        <div class="row no-gutters">
            <div class="col-md-2">
                <img src="/static/${data.profile_picture}" alt="Profile Picture" class="card-img">
            </div>
            <div class="col-md-10">
                <div class="card-body">
                    <h5 class="card-title"><b>@${data.username}</b></h5>
                    <p class="card-text">${data.message}</p>
                </div>
                <div class="manage-post">
                    <button class="mng-post-icon" onclick="delete_post(${data.id})"><span class="material-symbols-outlined">close</span></button>
                    <button class="mng-post-icon"><span class="material-symbols-outlined">edit</span></button>
                </div>
            </div>
        </div>
        `;
        mainPosts.insertBefore(newPostElement, mainPosts.firstChild);
    })
    .catch(error => {
        console.error('Error creating post:', error);
    })
})
