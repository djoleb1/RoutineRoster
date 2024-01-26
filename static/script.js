const showMoreBtn = document.getElementById('show-more-btn')

document.getElementById('pick_muscle_group').addEventListener("submit", function(event) {

    event.preventDefault()
    const selectedMuscleGroup = document.getElementById('exercises').value;
    const execrice_cards = document.getElementById('exercise_cards')
    fetch(`/api/exercises?muscle_group=${selectedMuscleGroup}`, { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        data.exercises.forEach((row) => {
            const exerciseArticle = document.createElement('article')
            exerciseArticle.classList.add("exercise");
            exerciseArticle.innerHTML = `
            <h4>${row.name}</h3>
            <h5>Equipment: ${row.equipment}</h5>
            <h5>Difficulty: ${row.difficulty}</h5>
            <p>${row.instructions}</p>
            `
            execrice_cards.appendChild(exerciseArticle)
        }); 
    })
    .catch(error => {
        console.error('Error fetching exercises:', error);
    });

})

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
    const mainPosts = document.getElementById('main-posts')
    const content = document.getElementById('content');

    if (content.value.length < 1){
        window.alert("You cannot post an empty post!")
        return
    }
    
    fetch("/create_post", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: content.value }),
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
                    <button class="mng-post-icon" id ="deleteBtn" onclick="delete_post(${data.id})"><span class="material-symbols-outlined">close</span></button>
                    <button class="mng-post-icon" id="editBtn" onclick="editPost(${data.id})"><span class="material-symbols-outlined">edit</span></button>
                </div>
            </div>
        </div>
        `;
        mainPosts.insertBefore(newPostElement, mainPosts.firstChild);
        content.value = '';

    })
    .catch(error => {
        console.error('Error creating post:', error);
    })
    
})

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

function editPost(id){
    
    document.getElementById('editBtn').parentNode.classList.toggle('hidden');

    // selecting the trainer card/post that will be edited
    const trainerCard = document.getElementById(id)

    // selecting the card-text class on the selected trainer card/post
    const postTextElement = trainerCard.querySelector('.card-text');

    // creating a text area in which we will edit the post content
    const editInput = document.createElement("textarea")
    editInput.setAttribute("id", `post${id}`)
    editInput.name = "editPost";
    
    // adding the current content into a textarea
    const currentContent = trainerCard.querySelector(".card-text").textContent.trim();
    editInput.value = currentContent;

    editInput.classList.add('form-control');

    postTextElement.textContent = '';
    postTextElement.appendChild(editInput)

    const updateBtn = document.createElement("button");
    updateBtn.innerText = "Update";
    updateBtn.classList.add('btn', 'btn-primary', 'mr-2');
    postTextElement.appendChild(updateBtn)

    const cancelBtn = document.createElement("button");
    cancelBtn.innerText = "Cancel";
    cancelBtn.classList.add('btn', 'btn-secondary');
    postTextElement.appendChild(cancelBtn)

    cancelBtn.addEventListener("click", function() {
        postTextElement.innerHTML = `<p>${currentContent}</p>`;
        document.getElementById('editBtn').parentNode.classList.toggle('hidden');
    })
    
   

    updateBtn.addEventListener("click", function()
    {
        document.getElementById('editBtn').parentNode.classList.toggle('hidden');
        
        const editedContent = editInput.value.trim();

        fetch("/edit_post", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ post_id: id, new_content: editedContent }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then(data => {
            postTextElement.innerHTML = `${data.new_content}`
            console.log(data)
        })
        .catch(error => {
            console.error('Error updating post:', error);
        })
    })
}


