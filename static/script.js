const showMoreBtn = document.getElementById('show-more-btn')

function listExercises () {
    
    const selectedMuscleGroup = document.getElementById('exercises').value;
    const execriceCards = document.getElementById('exercise_cards')
    fetch(`/api/exercises?muscle_group=${selectedMuscleGroup}`, { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        execriceCards.innerHTML = "";
        document.getElementById('exercise_muscle_type').innerHTML = `<h5>Exercises for ${selectedMuscleGroup}</h5>`
        data.exercises.forEach((row) => {
            
            const exerciseArticle = document.createElement('div');
            const contentDiv = document.createElement('div');
            const btnDiv = document.createElement('div');

            exerciseArticle.classList.add("exercise");
            exerciseArticle.classList.add("card");

            contentDiv.classList.add("content-div");

            contentDiv.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${row.name}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">Equipment: ${row.equipment}</h6>
                    <h6 class="card-subtitle mb-2 text-muted">Difficulty: ${row.difficulty}</h6>
                    <p class="card-text">${row.instructions}</p>
            </div>
            `;

            btnDiv.classList.add('btn-container');
            btnDiv.innerHTML = `<button onclick='saveExercise(${JSON.stringify(row)})' class="btn btn-primary">Select</button>`

            execriceCards.appendChild(exerciseArticle)
            exerciseArticle.appendChild(contentDiv)
            exerciseArticle.appendChild(btnDiv)
            console.log(data)
        }); 
    })
    .catch(error => {
        console.error('Error fetching exercises:', error);
    });

}

function saveExercise(row){

    const exerciseOl = document.querySelector('#trainig-plan-tracking')
    const exercisesList = []
    console.log(row, "DEBUG")


    fetch('/api/exercises', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: row.name, 
            equipment: row.equipment,
            difficulty: row.difficulty,
            instructions: row.instructions 
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not OK");
        }
        return response.json();
    })
    .then(data => {
        if (data.message != 'Exercise saved successfully!'){
            window.alert(data.message)
        }
        if (data.session = 'trainer') { 
            exercisesList.push(row.name)
            exercisesList.forEach(exercise => {
                li = document.createElement('li')
                li.innerText = row.name
                exerciseOl.appendChild(li)
            })
            console.log(exercisesList)
            if (exercisesList.length > 0) {
                document.querySelector('#sell-routine-btn').innerHTML = `<button onclick='prepareRoutine()'>Next</button>`
            }
        }
    })
    .catch(error => {
        console.error('Error saving post:', error);
    })
    console.log("ROW sent from JS")
}

const exercisesArr = []

function prepareRoutine() {
    
    const exercises = document.querySelectorAll('#trainig-plan-tracking li')
    exercises.forEach(li => {
        exercisesArr.push(li.textContent)
    })
    console.log(exercisesArr)

    document.querySelector('#sell-routine-btn').innerHTML = 
        `<label>Set a name for this routine:</label>
            <input type="text" name="routine-name" id="routine-name">

        <label>Set a price:</label>
            <input type="number" name="routine-price" id="routine-price">

        <label>Describe this routine:</label>
            <textarea name="routine-description" id="routine-description"></textarea>
            
        <button onclick="submitRoutine()">Submit for sale</button>`
}

function submitRoutine() {
    const routineName = document.querySelector('#routine-name').value
    const routineDesc = document.querySelector('#routine-description').value
    const routinePrice = document.querySelector('#routine-price').value

    if (!routineName){
        window.alert("Please input a name for this routine")
    }else if (!routinePrice){
        window.alert("Please set a price for this routine")
    }else if(!routineDesc){
        window.alert("Please describe this routine")
    }else{
        fetch('/saveroutine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: routineName,
                description: routineDesc,
                price: routinePrice,
                exercises: exercisesArr
            })
        })
        .then(response => {
            if (!response.ok){
                throw new Error('Network response was not OK')
            }
            return response.json()
        })
        .then(data => {
            console.log(data)  
            window.alert(data.message)
        })
        .catch(error => {
            console.error('Error creating post:', error);
        })
    }

     
}

function fetchTrainers() {
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
}
function setCompleted(id) {
    const exerciseCardId = id
    const savedExerciseCard = document.getElementById(id)
    savedExerciseCard.remove()

    fetch('/removeexercise', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({post_id: exerciseCardId})
    })
    .then(response => {
        if (!response.ok){
            throw new Error('Network response was not OK')
        }
        return response.json()
    })
    .then(data => {
        console.log(data)  
        window.alert('Good job on learning this exercise!')
    })
    .catch(error => {
        console.error('Error creating post:', error);
    })

}

function removeExercise(id) {
    const exerciseCardId = id
    const savedExerciseCard = document.getElementById(id)
    savedExerciseCard.remove()

    fetch('/removeexercise', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({post_id: exerciseCardId})
    })
    .then(response => {
        if (!response.ok){
            throw new Error('Network response was not OK')
        }
        return response.json()
    })
    .then(data => {
        console.log(data)  
    })
    .catch(error => {
        console.error('Error creating post:', error);
    })
}



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
                <div class="post-card-content">
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

function balanceWindow() {
    const addBtn = document.querySelector('#add-balance-btn')
    addBtn.remove()

    const financeDiv = document.querySelector('.finances')
    form = document.createElement('div')
    form.classList.add('balance-form')

    form.innerHTML = `<label>Enter the amount you wish to add:</label><br>
                        <input id='add-funds-amount' type='number'></input><br>
                        <button onclick='addFunds()'>Add</button>`
    financeDiv.appendChild(form)
}

function addFunds() {
    const addedFunds = parseInt(document.querySelector('#add-funds-amount').value)
    console.log(addedFunds)
    if (addedFunds < 0) {
        window.alert('Please enter a positive number')
        
    } else if (addFunds.length < 0) {
        console.log(addFunds.length)
        window.alert('You must input an amount')
        
    }
    else {
        fetch('/addfunds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({amount: addedFunds})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then(data => {
            console.log(data.amount)
            const formattedNumber = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data.amount);
            document.querySelector('.finances').innerHTML = `<h6>Your balance:</h6>
                                        <p class="balance">${formattedNumber}</p>
                                        <button onclick="balanceWindow()" id="add-balance-btn">Add balance</button>`
        })
        .catch(error => {
            console.error('Error updating post:', error);
        })
    }
    
}

function changed() {
    console.log("changed")
}

function buyRoutine(id) {
    routineId = id
    console.log(id)

    fetch('/shop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }, 
        body: JSON.stringify({
            routineId: routineId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not OK");
        }
        return response.json();
    })
    .then(data => {
        console.log(data)
        if(data.status == 'Not enough balance!'){
            window.alert(data.status)
        }else if (data.status == 'Successfully purchased'){
            location.reload()
        }
    })
    .catch(error => {
        console.error('Error updating post:', error);
    })
}

function removeRoutine(id) {
    cardId = id
    routineCard = document.getElementById(cardId)
    routineCard.remove()
    routineId = parseInt(id)

    console.log("Routine ID is: ", routineId)

    fetch('/removeroutine', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            routineId: routineId
        })
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
        console.error('Error updating post:', error);
    })
}