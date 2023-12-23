let hamburger = document.querySelector('.hamburger');
let navbar = document.querySelector('.navbar');

hamburger.addEventListener('click', function(){
    hamburger.classList.toggle('active');
    navbar.classList.toggle('active');
})

document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', function(){
    hamburger.classList.remove('active');
    navbar.classList.remove('active');
}))

document.getElementById('show-more-btn').addEventListener('click', function() {
    fetch('/show_more_trainers', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const trainersContainer = document.getElementById('trainersContainer');
        data.trainers.forEach(trainer => {
                
                // Create the trainer card content here similar to the initial ones
                // Append the content to trainerCard
                // Create elements for each trainer card
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
                <a href="#" class="btn home-follow-btn">Follow</a>
                `

            // Append the constructed trainer card to the trainersContainer
            const trainersContainer = document.getElementById('trainersContainer');
            trainersContainer.appendChild(trainerCard);
                
                trainersContainer.appendChild(trainerCard);
            });          

        }).catch(error => {
            console.error('Error fetching trainers:', error)
        })
    
})