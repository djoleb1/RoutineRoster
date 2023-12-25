
let navbar = document.querySelector('.navbar');
const showMoreBtn = document.getElementById('show-more-btn')

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